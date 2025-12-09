import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Play, Loader2, CheckCircle } from 'lucide-react'
import { booksApi, analysisApi } from '../services/api'

export default function ChapterAnalysis() {
  const { bookId } = useParams()
  const queryClient = useQueryClient()
  const [selectedChapter, setSelectedChapter] = useState(null)

  const { data: book } = useQuery({
    queryKey: ['book', bookId],
    queryFn: () => booksApi.get(bookId),
    enabled: !!bookId,
  })

  const { data: chapters = [] } = useQuery({
    queryKey: ['chapters', bookId],
    queryFn: () => booksApi.getChapters(bookId),
    enabled: !!bookId,
  })

  const { data: analyses = [] } = useQuery({
    queryKey: ['analyses', bookId],
    queryFn: () => analysisApi.getChapterAnalyses(bookId),
    enabled: !!bookId,
  })

  const { data: chapterContent } = useQuery({
    queryKey: ['chapterContent', bookId, selectedChapter],
    queryFn: () => booksApi.getChapterContent(bookId, selectedChapter),
    enabled: !!bookId && selectedChapter !== null,
  })

  const { data: selectedAnalysis } = useQuery({
    queryKey: ['chapterAnalysis', bookId, selectedChapter],
    queryFn: () => analysisApi.getChapterAnalysis(bookId, selectedChapter),
    enabled: !!bookId && selectedChapter !== null,
  })

  const analyzeMutation = useMutation({
    mutationFn: (chapterIndex) => analysisApi.analyzeChapter(bookId, chapterIndex),
    onSuccess: () => {
      queryClient.invalidateQueries(['analyses', bookId])
      queryClient.invalidateQueries(['chapterAnalysis', bookId, selectedChapter])
    },
  })

  // Check if chapter is analyzed
  const isAnalyzed = (index) => analyses.some((a) => a.chapter_index === index)

  return (
    <div className="flex h-full">
      {/* Chapter list */}
      <div className="w-64 bg-slate-800 border-r border-slate-700 overflow-auto">
        <div className="p-4 border-b border-slate-700">
          <h2 className="font-semibold">{book?.title}</h2>
          <p className="text-sm text-slate-400">{chapters.length} 章</p>
        </div>
        <div className="p-2">
          {chapters.map((chapter) => (
            <button
              key={chapter.index}
              onClick={() => setSelectedChapter(chapter.index)}
              className={`w-full text-left px-3 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                selectedChapter === chapter.index
                  ? 'bg-blue-600'
                  : 'hover:bg-slate-700'
              }`}
            >
              {isAnalyzed(chapter.index) && (
                <CheckCircle size={14} className="text-green-400 flex-shrink-0" />
              )}
              <span className="truncate text-sm">{chapter.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex">
        {selectedChapter === null ? (
          <div className="flex-1 flex items-center justify-center text-slate-500">
            选择一个章节查看
          </div>
        ) : (
          <>
            {/* Chapter content */}
            <div className="flex-1 p-6 overflow-auto">
              <h3 className="text-lg font-semibold mb-4">
                {chapterContent?.title}
              </h3>
              <div className="whitespace-pre-wrap text-slate-300 text-sm leading-relaxed">
                {chapterContent?.content}
              </div>
            </div>

            {/* Analysis panel */}
            <div className="w-80 bg-slate-800 border-l border-slate-700 p-4 overflow-auto">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">分析</h3>
                <button
                  onClick={() => analyzeMutation.mutate(selectedChapter)}
                  disabled={analyzeMutation.isPending}
                  className="flex items-center gap-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors disabled:opacity-50"
                >
                  {analyzeMutation.isPending ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <Play size={14} />
                  )}
                  分析
                </button>
              </div>

              {selectedAnalysis ? (
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium text-slate-400 mb-1">
                      摘要
                    </h4>
                    <p className="text-sm">{selectedAnalysis.summary}</p>
                  </div>

                  {selectedAnalysis.characters?.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-slate-400 mb-1">
                        人物
                      </h4>
                      <div className="flex flex-wrap gap-1">
                        {selectedAnalysis.characters.map((char) => (
                          <span
                            key={char}
                            className="text-xs px-2 py-0.5 bg-slate-700 rounded"
                          >
                            {char}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedAnalysis.events?.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-slate-400 mb-1">
                        事件
                      </h4>
                      <ul className="text-sm space-y-1">
                        {selectedAnalysis.events.map((event, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-blue-400">•</span>
                            {event}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {selectedAnalysis.sentiment && (
                    <div>
                      <h4 className="text-sm font-medium text-slate-400 mb-1">
                        情感
                      </h4>
                      <p className="text-sm">{selectedAnalysis.sentiment}</p>
                    </div>
                  )}

                  {selectedAnalysis.keywords?.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-slate-400 mb-1">
                        关键词
                      </h4>
                      <div className="flex flex-wrap gap-1">
                        {selectedAnalysis.keywords.map((kw) => (
                          <span
                            key={kw}
                            className="text-xs px-2 py-0.5 bg-blue-900 text-blue-300 rounded"
                          >
                            {kw}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm text-slate-500">
                  点击"分析"按钮开始 AI 分析
                </p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
