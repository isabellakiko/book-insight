import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000, // AI operations can take time
})

// Books
export const booksApi = {
  list: () => api.get('/books').then((r) => r.data),
  get: (bookId) => api.get(`/books/${bookId}`).then((r) => r.data),
  getChapters: (bookId) => api.get(`/books/${bookId}/chapters`).then((r) => r.data),
  getChapterContent: (bookId, chapterIndex) =>
    api.get(`/books/${bookId}/chapters/${chapterIndex}/content`).then((r) => r.data),
  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/books/upload', formData).then((r) => r.data)
  },
  delete: (bookId) => api.delete(`/books/${bookId}`).then((r) => r.data),
}

// Analysis
export const analysisApi = {
  // 章节分析
  getChapterAnalyses: (bookId) => api.get(`/analysis/${bookId}/chapters`).then((r) => r.data),
  getChapterAnalysis: (bookId, chapterIndex) =>
    api.get(`/analysis/${bookId}/chapters/${chapterIndex}`).then((r) => r.data),
  analyzeChapter: (bookId, chapterIndex) =>
    api.post(`/analysis/${bookId}/chapters/${chapterIndex}`).then((r) => r.data),
  analyzeBatch: (bookId, start, end, parallel = 3) =>
    api.post(`/analysis/${bookId}/batch`, { start_chapter: start, end_chapter: end, parallel }).then((r) => r.data),

  // 人物按需分析
  searchCharacter: (bookId, name) =>
    api.post(`/analysis/${bookId}/characters/search`, { name }).then((r) => r.data),
  analyzeCharacter: (bookId, name, maxChapters = 30) =>
    api.post(`/analysis/${bookId}/characters/analyze`, { name, max_chapters: maxChapters }).then((r) => r.data),
  getCharacterStreamUrl: (bookId, name) =>
    `/api/analysis/${bookId}/characters/stream?name=${encodeURIComponent(name)}`,
  getDetailedCharacter: (bookId, name) =>
    api.get(`/analysis/${bookId}/characters/detailed/${encodeURIComponent(name)}`).then((r) => r.data),
  getDetailedCharacters: (bookId) =>
    api.get(`/analysis/${bookId}/characters/detailed`).then((r) => r.data),
}

// RAG
export const ragApi = {
  getStatus: (bookId) => api.get(`/rag/${bookId}/status`).then((r) => r.data),
  index: (bookId, chunkSize = 500, chunkOverlap = 100) =>
    api.post(`/rag/${bookId}/index`, { chunk_size: chunkSize, chunk_overlap: chunkOverlap }).then((r) => r.data),
  query: (bookId, query, topK = 10) =>
    api.post(`/rag/${bookId}/query`, { query, top_k: topK }).then((r) => r.data),
  ask: (bookId, query, topK = 10) =>
    api.post(`/rag/${bookId}/ask`, { query, top_k: topK }).then((r) => r.data),
}

export default api
