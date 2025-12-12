import { useState, useCallback, useRef } from 'react'
import { analysisApi } from '../services/api'

/**
 * Hook for character on-demand analysis with SSE streaming
 */
export function useCharacterAnalysis(bookId) {
  const [status, setStatus] = useState('idle') // idle/searching/analyzing/completed/error
  const [searchResult, setSearchResult] = useState(null)
  const [appearances, setAppearances] = useState([])
  const [relations, setRelations] = useState([])
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const eventSourceRef = useRef(null)

  const reset = useCallback(() => {
    setStatus('idle')
    setSearchResult(null)
    setAppearances([])
    setRelations([])
    setResult(null)
    setError(null)
  }, [])

  const analyzeCharacter = useCallback(
    (name) => {
      reset()
      setStatus('searching')

      // Close previous connection
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }

      const url = analysisApi.getCharacterStreamUrl(bookId, name)
      const eventSource = new EventSource(url)
      eventSourceRef.current = eventSource

      eventSource.addEventListener('search_complete', (e) => {
        const data = JSON.parse(e.data)
        setSearchResult(data)
        if (data.found_in_chapters.length === 0) {
          setStatus('completed')
          setError('未找到该人物')
          eventSource.close()
        } else {
          setStatus('analyzing')
        }
      })

      eventSource.addEventListener('chapter_analyzed', (e) => {
        const data = JSON.parse(e.data)
        setAppearances((prev) => [...prev, data.appearance])
      })

      eventSource.addEventListener('chapter_error', (e) => {
        // 章节分析失败时静默处理，SSE 流会继续
        JSON.parse(e.data)
      })

      eventSource.addEventListener('relations_analyzed', (e) => {
        const data = JSON.parse(e.data)
        setRelations(data.relations)
      })

      eventSource.addEventListener('completed', (e) => {
        const data = JSON.parse(e.data)
        if (data.error) {
          setError(data.error)
        } else {
          setResult(data)
        }
        setStatus('completed')
        eventSource.close()
      })

      eventSource.onerror = () => {
        setStatus('error')
        setError('分析过程中断，请重试')
        eventSource.close()
      }
    },
    [bookId, reset]
  )

  const cancel = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      setStatus('idle')
    }
  }, [])

  // Load cached character directly (no re-analysis)
  const loadCached = useCallback(
    async (name) => {
      reset()
      setStatus('searching')
      try {
        const data = await analysisApi.getDetailedCharacter(bookId, name)
        // 有 appearances 数据就认为缓存有效
        if (data && data.appearances && data.appearances.length > 0) {
          setResult(data)
          setAppearances(data.appearances || [])
          setRelations(data.relations || [])
          setStatus('completed')
          return true
        }
        // No cache, need to analyze
        return false
      } catch {
        // 缓存加载失败是正常情况（首次分析）
        return false
      }
    },
    [bookId, reset]
  )

  // Calculate progress - 使用实际分析的章节数计算
  const progress =
    searchResult && searchResult.found_in_chapters.length > 0
      ? Math.round((appearances.length / Math.min(searchResult.found_in_chapters.length, 100)) * 100)
      : 0

  return {
    status,
    searchResult,
    appearances,
    relations,
    result,
    error,
    progress,
    analyzeCharacter,
    loadCached,
    cancel,
    reset,
  }
}
