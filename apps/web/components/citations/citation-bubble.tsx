"use client"

import {
  FileText,
  FileSpreadsheet,
  File,
  FolderOpen,
  ExternalLink,
} from "lucide-react"
import type { Citation } from "@/lib/types"
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card"
import { Badge } from "@/components/ui/badge"

interface CitationBubbleProps {
  number: number
  citation?: Citation
  onClick?: (citation: Citation) => void
}

function FileIcon({ fileType }: { fileType?: string }) {
  if (fileType?.includes("pdf")) return <FileText className="size-4 text-red-500" />
  if (fileType?.includes("word") || fileType?.includes("docx"))
    return <FileSpreadsheet className="size-4 text-blue-500" />
  return <File className="size-4 text-muted-foreground" />
}

export function CitationBubble({
  number,
  citation,
  onClick,
}: CitationBubbleProps) {
  const bubble = (
    <button
      type="button"
      className="mx-0.5 inline-flex size-5 cursor-pointer items-center justify-center rounded-full bg-primary/10 text-[10px] font-semibold text-primary transition-colors hover:bg-primary/20"
      onClick={() => citation && onClick?.(citation)}
    >
      {number}
    </button>
  )

  if (!citation) return bubble

  return (
    <HoverCard openDelay={200} closeDelay={100}>
      <HoverCardTrigger asChild>{bubble}</HoverCardTrigger>
      <HoverCardContent side="top" className="w-80 p-3" align="start">
        <div className="space-y-2">
          {/* Header: icon + document name */}
          <div className="flex items-start gap-2">
            <FileIcon fileType={citation.fileType} />
            <p className="text-sm font-medium leading-tight">
              {citation.documentName}
            </p>
          </div>

          {/* Folder + page badges */}
          <div className="flex flex-wrap items-center gap-1.5">
            {citation.folderName && (
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <FolderOpen className="size-3" />
                <span>{citation.folderName}</span>
              </div>
            )}
            {citation.pageNumber > 0 && (
              <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                Page {citation.pageNumber}
              </Badge>
            )}
          </div>

          {/* Snippet */}
          {citation.chunkText && (
            <p className="line-clamp-3 text-xs leading-relaxed text-muted-foreground">
              {citation.chunkText}
            </p>
          )}

          {/* View source link */}
          <button
            type="button"
            className="flex items-center gap-1 text-xs font-medium text-primary hover:underline"
            onClick={() => onClick?.(citation)}
          >
            <ExternalLink className="size-3" />
            View source
          </button>
        </div>
      </HoverCardContent>
    </HoverCard>
  )
}
