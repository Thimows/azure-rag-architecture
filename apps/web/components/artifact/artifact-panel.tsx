"use client"

import { useState } from "react"
import dynamic from "next/dynamic"
import {
  FileText,
  FileSpreadsheet,
  File,
  FolderOpen,
  ChevronRight,
  Loader2,
  X,
} from "lucide-react"

import type { Citation } from "@/lib/types"
import { trpc } from "@/lib/trpc/client"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"

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

/** Extract just the filename from a blob path like "orgId/folderId/file.pdf" */
function getFileName(documentName: string): string {
  const parts = documentName.split("/")
  return parts[parts.length - 1] ?? documentName
}

function FileIcon({ name, fileType }: { name: string; fileType?: string }) {
  const lower = (fileType ?? name).toLowerCase()
  if (lower.includes("pdf"))
    return <FileText className="size-4 shrink-0 text-red-500" />
  if (lower.includes("word") || lower.includes("docx"))
    return <FileSpreadsheet className="size-4 shrink-0 text-blue-500" />
  return <File className="size-4 shrink-0 text-muted-foreground" />
}

function isPdf(citation: Citation): boolean {
  const name = getFileName(citation.documentName).toLowerCase()
  return (
    citation.fileType?.toLowerCase().includes("pdf") === true ||
    name.endsWith(".pdf")
  )
}

interface ArtifactPanelProps {
  citation: Citation | null
  onClose: () => void
}

export function ArtifactPanel({ citation, onClose }: ArtifactPanelProps) {
  const [chunkOpen, setChunkOpen] = useState(false)
  const showPdf = citation ? isPdf(citation) : false
  const { data: viewUrlData, isLoading: isLoadingUrl } =
    trpc.document.getViewUrl.useQuery(
      { documentId: citation?.documentId ?? "" },
      { enabled: !!citation?.documentId && showPdf },
    )

  const displayName = citation ? getFileName(citation.documentName) : ""

  const isOpen = !!citation

  return (
    <aside
      className={`flex h-full shrink-0 flex-col overflow-hidden border-l bg-background transition-[width] duration-300 ease-in-out ${isOpen ? "w-[480px]" : "w-0 border-l-0"}`}
    >
      {citation && (
        <>
          {/* Header */}
          <div className="flex w-[480px] items-center gap-2 border-b px-4 py-3">
            <FileIcon name={displayName} fileType={citation.fileType} />
            <span className="min-w-0 flex-1 truncate text-base font-semibold">
              {displayName}
            </span>
            <Button
              variant="ghost"
              size="icon"
              className="size-7 shrink-0"
              onClick={onClose}
            >
              <X className="size-4" />
              <span className="sr-only">Close</span>
            </Button>
          </div>

          {/* Content */}
          <div className="flex min-h-0 w-[480px] flex-1 flex-col gap-4 px-4 py-4">
            {/* Metadata badges */}
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="secondary">Source [{citation.number}]</Badge>
              {citation.pageNumber > 0 && (
                <Badge variant="outline">Page {citation.pageNumber}</Badge>
              )}
              {citation.folderName && (
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <FolderOpen className="size-3" />
                  <span>{citation.folderName}</span>
                </div>
              )}
            </div>
            <Separator />

            <ScrollArea className="min-h-0 flex-1">
              {/* PDF viewer (shown first) */}
              {showPdf && (
                <div className="mb-4">
                  {isLoadingUrl ? (
                    <div className="flex h-96 items-center justify-center">
                      <Loader2 className="size-6 animate-spin text-muted-foreground" />
                    </div>
                  ) : viewUrlData?.url ? (
                    <PdfViewer
                      key={`${citation.documentId}-${citation.pageNumber}`}
                      url={viewUrlData.url}
                      initialPage={citation.pageNumber}
                    />
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      Unable to load document preview.
                    </p>
                  )}
                  <Separator className="mt-4" />
                </div>
              )}

              {/* Collapsible referenced text */}
              <Collapsible open={chunkOpen} onOpenChange={setChunkOpen}>
                <CollapsibleTrigger className="flex w-full cursor-pointer items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground">
                  <ChevronRight
                    className={`size-3.5 shrink-0 transition-transform ${chunkOpen ? "rotate-90" : ""}`}
                  />
                  Referenced text
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <div className="mt-2 rounded-lg bg-muted p-3">
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">
                      {citation.chunkText}
                    </p>
                  </div>
                </CollapsibleContent>
              </Collapsible>
            </ScrollArea>
          </div>
        </>
      )}
    </aside>
  )
}
