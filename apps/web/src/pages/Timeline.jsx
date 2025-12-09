import { useQuery } from '@tanstack/react-query'
import { Clock, ChevronRight } from 'lucide-react'
import { booksApi, analysisApi } from '../services/api'
import { useBookStore } from '../stores/bookStore'

export default function Timeline() {
  const { currentBookId } = useBookStore()

  const { data: book } = useQuery({
    queryKey: ['book', currentBookId],
    queryFn: () => booksApi.get(currentBookId),
    enabled: !!currentBookId,
  })

  const { data: analyses = [], isLoading } = useQuery({
    queryKey: ['analyses', currentBookId],
    queryFn: () => analysisApi.getChapterAnalyses(currentBookId),
    enabled: !!currentBookId,
  })

  if (!currentBookId) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Clock size={48} className="mx-auto text-slate-600 mb-4" />
          <p className="text-slate-400">请先在书籍页面选择一本书</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">情节时间线</h1>
        <p className="text-slate-400 mt-1">{book?.title}</p>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-slate-400">加载中...</div>
      ) : analyses.length === 0 ? (
        <div className="text-center py-12">
          <Clock size={48} className="mx-auto text-slate-600 mb-4" />
          <p className="text-slate-400">还没有章节分析，请先分析一些章节</p>
        </div>
      ) : (
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-700" />

          {/* Events */}
          <div className="space-y-6">
            {analyses.map((analysis) => (
              <div key={analysis.chapter_index} className="relative pl-12">
                {/* Dot */}
                <div className="absolute left-2.5 w-3 h-3 bg-blue-500 rounded-full border-2 border-slate-900" />

                <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                  <div className="flex items-center gap-2 text-sm text-slate-400 mb-2">
                    <span>第 {analysis.chapter_index + 1} 章</span>
                    <ChevronRight size={14} />
                    <span>{analysis.title}</span>
                  </div>

                  <p className="text-slate-200 mb-3">{analysis.summary}</p>

                  {analysis.events?.length > 0 && (
                    <div className="space-y-1">
                      {analysis.events.map((event, i) => (
                        <div
                          key={i}
                          className="text-sm text-slate-400 flex items-start gap-2"
                        >
                          <span className="text-blue-400">•</span>
                          {event}
                        </div>
                      ))}
                    </div>
                  )}

                  {analysis.characters?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-3">
                      {analysis.characters.map((char) => (
                        <span
                          key={char}
                          className="text-xs px-2 py-0.5 bg-slate-700 rounded"
                        >
                          {char}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
