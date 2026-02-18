"use client"

export function PdfViewer({
  url,
  initialPage,
}: {
  url: string
  initialPage: number
}) {
  const src = initialPage > 1 ? `${url}#page=${initialPage}` : url

  return (
    <iframe
      src={src}
      className="h-[500px] w-full rounded-lg border"
      title="PDF viewer"
    />
  )
}
