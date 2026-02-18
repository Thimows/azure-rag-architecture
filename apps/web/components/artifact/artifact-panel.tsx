"use client"

import dynamic from "next/dynamic"
import {
  FileText,
  FileSpreadsheet,
  File,
  FolderOpen,
  Loader2,
} from "lucide-react"

import type { Citation } from "@/lib/types"
import { trpc } from "@/lib/trpc/client"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"

const PdfViewer = dynamic(
  () =>
    import("@/components/artifact/pdf-viewer").then((mod) => mod.PdfViewer),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="size-6 animate-spin text-muted-foreground" />
      </div>
    ),
  },
)

function FileIcon({ fileType }: { fileType?: string }) {
  if (fileType?.includes("pdf"))
    return <FileText className="size-4 text-red-500" />
  if (fileType?.includes("word") || fileType?.includes("docx"))
    return <FileSpreadsheet className="size-4 text-blue-500" />
  return <File className="size-4 text-muted-foreground" />
}

function isPdf(citation: Citation): boolean {
  return (
    citation.fileType?.includes("pdf") === true ||
    citation.documentName.toLowerCase().endsWith(".pdf")
  )
}

interface ArtifactPanelProps {
  citation: Citation | null
  onClose: () => void
}

export function ArtifactPanel({ citation, onClose }: ArtifactPanelProps) {
  const { data: viewUrlData, isLoading: isLoadingUrl } =
    trpc.document.getViewUrl.useQuery(
      { documentId: citation?.documentId ?? "" },
      { enabled: !!citation?.documentId },
    )

  return (
    <Sheet open={!!citation} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="w-full sm:max-w-lg">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2 text-base">
            <FileIcon fileType={citation?.fileType} />
            <span className="truncate">{citation?.documentName}</span>
          </SheetTitle>
        </SheetHeader>
        {citation && (
          <div className="mt-4 space-y-4">
            {/* Metadata badges */}
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="secondary">Source [{citation.number}]</Badge>
              {citation.pageNumber > 0 && (
                <Badge variant="outline">Page {citation.pageNumber}</Badge>
              )}
              {citation.relevanceScore > 0 && (
                <Badge variant="outline">
                  Score: {(citation.relevanceScore * 100).toFixed(0)}%
                </Badge>
              )}
              {citation.folderName && (
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <FolderOpen className="size-3" />
                  <span>{citation.folderName}</span>
                </div>
              )}
            </div>
            <Separator />

            <ScrollArea className="h-[calc(100vh-220px)]">
              {/* Chunk text reference */}
              <div className="mb-4 rounded-lg bg-muted p-3">
                <p className="mb-1 text-xs font-medium text-muted-foreground">
                  Referenced text
                </p>
                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                  {citation.chunkText}
                </p>
              </div>

              {/* PDF viewer or fallback */}
              {isPdf(citation) && (
                <>
                  <Separator className="my-4" />
                  {isLoadingUrl ? (
                    <div className="flex h-96 items-center justify-center">
                      <Loader2 className="size-6 animate-spin text-muted-foreground" />
                    </div>
                  ) : viewUrlData?.url ? (
                    <PdfViewer
                      url={viewUrlData.url}
                      initialPage={citation.pageNumber}
                    />
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      Unable to load document preview.
                    </p>
                  )}
                </>
              )}
            </ScrollArea>
          </div>
        )}
      </SheetContent>
    </Sheet>
  )
}
