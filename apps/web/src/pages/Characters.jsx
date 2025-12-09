import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Users, RefreshCw, Loader2 } from 'lucide-react'
import { booksApi, analysisApi } from '../services/api'
import { useBookStore } from '../stores/bookStore'

export default function Characters() {
  const { currentBookId } = useBookStore()
  const queryClient = useQueryClient()

  const { data: book } = useQuery({
    queryKey: ['book', currentBookId],
    queryFn: () => booksApi.get(currentBookId),
    enabled: !!currentBookId,
  })

  const { data: characters = [], isLoading } = useQuery({
    queryKey: ['characters', currentBookId],
    queryFn: () => analysisApi.getCharacters(currentBookId),
    enabled: !!currentBookId,
  })

  const extractMutation = useMutation({
    mutationFn: () => analysisApi.extractCharacters(currentBookId),
    onSuccess: () => {
      queryClient.invalidateQueries(['characters', currentBookId])
    },
  })

  if (!currentBookId) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Users size={48} className="mx-auto text-slate-600 mb-4" />
          <p className="text-slate-400">请先在书籍页面选择一本书</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">人物分析</h1>
          <p className="text-slate-400 mt-1">{book?.title}</p>
        </div>

        <button
          onClick={() => extractMutation.mutate()}
          disabled={extractMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
        >
          {extractMutation.isPending ? (
            <Loader2 size={20} className="animate-spin" />
          ) : (
            <RefreshCw size={20} />
          )}
          提取人物
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-slate-400">加载中...</div>
      ) : characters.length === 0 ? (
        <div className="text-center py-12">
          <Users size={48} className="mx-auto text-slate-600 mb-4" />
          <p className="text-slate-400">还没有提取人物，点击上方按钮开始</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {characters.map((char) => (
            <div
              key={char.id}
              className="bg-slate-800 rounded-xl p-6 border border-slate-700"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center font-bold">
                  {char.name[0]}
                </div>
                <div>
                  <h3 className="font-semibold">{char.name}</h3>
                  <span
                    className={`text-xs px-2 py-0.5 rounded ${
                      char.role === 'protagonist'
                        ? 'bg-blue-900 text-blue-300'
                        : char.role === 'antagonist'
                        ? 'bg-red-900 text-red-300'
                        : 'bg-slate-700 text-slate-300'
                    }`}
                  >
                    {char.role === 'protagonist'
                      ? '主角'
                      : char.role === 'antagonist'
                      ? '反派'
                      : char.role === 'supporting'
                      ? '配角'
                      : '次要'}
                  </span>
                </div>
              </div>

              {char.aliases?.length > 0 && (
                <p className="text-sm text-slate-400 mb-2">
                  别名：{char.aliases.join('、')}
                </p>
              )}

              <p className="text-sm text-slate-300">{char.description}</p>

              {char.first_appearance !== undefined && (
                <p className="text-xs text-slate-500 mt-3">
                  首次出场：第 {char.first_appearance + 1} 章
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
