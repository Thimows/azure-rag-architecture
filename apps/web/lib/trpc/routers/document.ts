import { z } from "zod"
import { createTRPCRouter, protectedProcedure } from "../init"
import { document } from "@/lib/db/schema"
import { eq, and, desc } from "drizzle-orm"

export const documentRouter = createTRPCRouter({
  list: protectedProcedure
    .input(z.object({ folderId: z.string().optional() }).optional())
    .query(async ({ ctx, input }) => {
      const conditions = [eq(document.organizationId, ctx.organizationId)]

      if (input?.folderId) {
        conditions.push(eq(document.folderId, input.folderId))
      }

      return ctx.db
        .select({
          id: document.id,
          name: document.name,
          fileType: document.fileType,
          fileSize: document.fileSize,
          status: document.status,
          error: document.error,
          createdAt: document.createdAt,
        })
        .from(document)
        .where(and(...conditions))
        .orderBy(desc(document.createdAt))
    }),

  create: protectedProcedure
    .input(
      z.object({
        id: z.string(),
        name: z.string(),
        folderId: z.string(),
        blobUrl: z.string(),
        fileType: z.string(),
        fileSize: z.number(),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      const [row] = await ctx.db
        .insert(document)
        .values({
          id: input.id,
          organizationId: ctx.organizationId,
          folderId: input.folderId,
          name: input.name,
          blobUrl: input.blobUrl,
          fileType: input.fileType,
          fileSize: input.fileSize,
          status: "uploaded",
          error: null,
          uploadedBy: ctx.session.user.id,
        })
        .onConflictDoUpdate({
          target: [document.organizationId, document.folderId, document.name],
          set: {
            status: "uploaded",
            error: null,
            fileSize: input.fileSize,
            blobUrl: input.blobUrl,
          },
        })
        .returning({ id: document.id })

      return row
    }),

  delete: protectedProcedure
    .input(z.object({ id: z.string() }))
    .mutation(async ({ ctx, input }) => {
      await ctx.db
        .delete(document)
        .where(
          and(
            eq(document.id, input.id),
            eq(document.organizationId, ctx.organizationId),
          ),
        )
      return { ok: true }
    }),
})
