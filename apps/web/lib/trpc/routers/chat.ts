import { z } from "zod"
import { createTRPCRouter, protectedProcedure } from "../init"
import { chat, message, citation, document, folder } from "@/lib/db/schema"
import { eq, and, desc, asc, inArray } from "drizzle-orm"
import { generateId } from "@/lib/id"

export const chatRouter = createTRPCRouter({
  list: protectedProcedure.query(async ({ ctx }) => {
    return ctx.db
      .select({ id: chat.id, title: chat.title })
      .from(chat)
      .where(
        and(
          eq(chat.userId, ctx.session.user.id),
          eq(chat.organizationId, ctx.organizationId),
        ),
      )
      .orderBy(desc(chat.updatedAt))
      .limit(50)
  }),

  create: protectedProcedure
    .input(z.object({ id: z.string(), title: z.string().optional() }))
    .mutation(async ({ ctx, input }) => {
      await ctx.db.insert(chat).values({
        id: input.id,
        organizationId: ctx.organizationId,
        userId: ctx.session.user.id,
        title: input.title ?? null,
      })
      return { id: input.id }
    }),

  getMessages: protectedProcedure
    .input(z.object({ chatId: z.string() }))
    .query(async ({ ctx, input }) => {
      const chatRecord = await ctx.db.query.chat.findFirst({
        where: eq(chat.id, input.chatId),
      })

      if (!chatRecord || chatRecord.userId !== ctx.session.user.id) {
        return { title: null, messages: [], organizationId: "" }
      }

      const messages = await ctx.db
        .select()
        .from(message)
        .where(eq(message.chatId, input.chatId))
        .orderBy(asc(message.createdAt))

      // Fetch citations for ALL assistant messages in one batch
      const assistantIds = messages
        .filter((m) => m.role === "assistant")
        .map((m) => m.id)

      const citationsByMessage = new Map<
        string,
        {
          number: number
          documentId: string
          documentName: string
          documentUrl: string
          pageNumber: number
          chunkText: string
          relevanceScore: number
          folderId?: string
          folderName?: string
          fileType?: string
        }[]
      >()

      if (assistantIds.length > 0) {
        const rows = await ctx.db
          .select()
          .from(citation)
          .where(inArray(citation.messageId, assistantIds))

        // Collect unique documentIds for enrichment
        const docIds = [
          ...new Set(rows.map((c) => c.documentId).filter(Boolean)),
        ] as string[]

        // Batch query documents + folders for enrichment
        const docMap = new Map<
          string,
          { blobUrl: string; fileType: string; folderId: string; folderName: string | null }
        >()
        if (docIds.length > 0) {
          const docs = await ctx.db
            .select({
              id: document.id,
              blobUrl: document.blobUrl,
              fileType: document.fileType,
              folderId: document.folderId,
              folderName: folder.name,
            })
            .from(document)
            .leftJoin(folder, eq(document.folderId, folder.id))
            .where(inArray(document.id, docIds))

          for (const doc of docs) {
            docMap.set(doc.id, {
              blobUrl: doc.blobUrl,
              fileType: doc.fileType,
              folderId: doc.folderId,
              folderName: doc.folderName,
            })
          }
        }

        // Group citations by messageId
        for (const c of rows) {
          const enrichment = c.documentId ? docMap.get(c.documentId) : undefined
          const mapped = {
            number: c.number,
            documentId: c.documentId ?? "",
            documentName: c.documentName,
            documentUrl: enrichment?.blobUrl ?? "",
            pageNumber: c.pageNumber ?? 0,
            chunkText: c.chunkText,
            relevanceScore: c.relevanceScore ?? 0,
            folderId: enrichment?.folderId,
            folderName: enrichment?.folderName ?? undefined,
            fileType: enrichment?.fileType,
          }
          const arr = citationsByMessage.get(c.messageId) ?? []
          arr.push(mapped)
          citationsByMessage.set(c.messageId, arr)
        }
      }

      return {
        title: chatRecord.title,
        messages: messages.map((m) => ({
          role: m.role as "user" | "assistant",
          content: m.content,
          citations: citationsByMessage.get(m.id),
        })),
        organizationId: chatRecord.organizationId,
      }
    }),

  addMessage: protectedProcedure
    .input(
      z.object({
        chatId: z.string(),
        role: z.enum(["user", "assistant"]),
        content: z.string(),
        citations: z
          .array(
            z.object({
              number: z.number(),
              documentId: z.string().optional(),
              documentName: z.string(),
              pageNumber: z.number().optional(),
              chunkText: z.string(),
              relevanceScore: z.number().optional(),
            }),
          )
          .optional(),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      const messageId = generateId()
      await ctx.db.insert(message).values({
        id: messageId,
        chatId: input.chatId,
        role: input.role,
        content: input.content,
      })

      if (input.citations?.length) {
        await ctx.db.insert(citation).values(
          input.citations.map((c) => ({
            id: generateId(),
            messageId,
            number: c.number,
            documentId: c.documentId ?? null,
            documentName: c.documentName,
            pageNumber: c.pageNumber ?? null,
            chunkText: c.chunkText,
            relevanceScore: c.relevanceScore ?? null,
          })),
        )
      }

      return { id: messageId }
    }),
})
