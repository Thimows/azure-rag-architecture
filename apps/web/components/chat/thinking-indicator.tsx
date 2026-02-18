"use client"

import { useState } from "react"
import { ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"

interface ThinkingIndicatorProps {
  content: string
  isThinking: boolean
}

export function ThinkingIndicator({
  content,
  isThinking,
}: ThinkingIndicatorProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="mb-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex cursor-pointer items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        <ChevronRight
          className={cn(
            "size-3 transition-transform",
            expanded && "rotate-90",
          )}
        />
        {isThinking ? (
          <span className="flex items-center gap-1.5">
            Thinking
            <span className="flex gap-0.5">
              <span className="size-1 animate-pulse rounded-full bg-muted-foreground/60" />
              <span className="size-1 animate-pulse rounded-full bg-muted-foreground/60 [animation-delay:150ms]" />
              <span className="size-1 animate-pulse rounded-full bg-muted-foreground/60 [animation-delay:300ms]" />
            </span>
          </span>
        ) : (
          <span>Thought process</span>
        )}
      </button>
      {expanded && (
        <div className="mt-1.5 border-l-2 border-muted-foreground/20 pl-3 text-xs text-muted-foreground whitespace-pre-wrap">
          {content}
        </div>
      )}
    </div>
  )
}
