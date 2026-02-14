import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  timeout: 120_000,
})

export function setApiBaseUrl(url: string) {
  console.log(`[API] Setting base URL to: ${url}`)
  api.defaults.baseURL = url
}

// ── Health ──────────────────────────────────────────────
export interface HealthResponse {
  ok: boolean
  version?: string
}

export function fetchHealth(): Promise<HealthResponse> {
  return api.get<HealthResponse>('/api/health').then((r) => r.data)
}

// ── Projects ────────────────────────────────────────────
export interface Project {
  id: string
  name: string
  description?: string
  embedding_model?: string
  created_at?: string
}

export function fetchProjects(): Promise<Project[]> {
  return api.get<Project[]>('/api/projects').then((r) => r.data)
}

export interface ProjectUpdate {
  name?: string
  embedding_model?: string
}

export function createProjectApi(
  name: string,
  description?: string,
  embedding_model?: string,
): Promise<Project> {
  return api
    .post<Project>('/api/projects', { name, description, embedding_model })
    .then((r) => r.data)
}

export function updateProjectApi(id: string, data: ProjectUpdate): Promise<Project> {
  return api.patch<Project>(`/api/projects/${id}`, data).then((r) => r.data)
}

export function deleteProjectApi(id: string): Promise<void> {
  return api.delete(`/api/projects/${id}`).then(() => undefined)
}

// ── Files (project-scoped) ──────────────────────────────
export type FileStatus =
  | 'queued'
  | 'parsing'
  | 'chunking'
  | 'embedding'
  | 'indexing'
  | 'indexed'
  | 'failed'

export interface FileRecord {
  id: string
  filename: string
  size_bytes: number
  status: FileStatus
  created_at: string
  chunk_count?: number
  mime_type?: string
  added_chunks?: number
  skipped_chunks?: number
  progress?: number
}

export interface UploadResult {
  uploaded: { id: string; filename: string; status: string }[]
  ingestion_job_id?: string
}

export function fetchFiles(projectId: string): Promise<FileRecord[]> {
  return api.get<FileRecord[]>(`/api/projects/${projectId}/files`).then((r) => r.data)
}

export async function uploadFiles(
  projectId: string,
  files: File[],
  options?: { embedding_api_key?: string; embedding_base_url?: string },
): Promise<UploadResult> {
  const form = new FormData()
  files.forEach((f) => form.append('files', f))
  if (options?.embedding_api_key) {
    form.append('embedding_api_key', options.embedding_api_key)
  }
  if (options?.embedding_base_url) {
    form.append('embedding_base_url', options.embedding_base_url)
  }

  return api
    .post<UploadResult>(`/api/projects/${projectId}/files/upload`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then((r) => r.data)
}

export function deleteFile(projectId: string, fileId: string): Promise<void> {
  return api.delete(`/api/projects/${projectId}/files/${fileId}`).then(() => undefined)
}

export function reindexFile(projectId: string, fileId: string): Promise<void> {
  return api.post(`/api/projects/${projectId}/files/${fileId}/reindex`).then(() => undefined)
}

// ── Query (project-scoped) ──────────────────────────────
export interface QuerySettings {
  k: number
  search_type: 'similarity' | 'mmr'
  temperature: number
  model: string
  chunk_size?: number
  chunk_overlap?: number
  embedding_model?: string
  query_translation?: boolean
  show_debug?: boolean
  api_key?: string
  base_url?: string

  // RAG quality
  min_score?: number
  enable_reranking?: boolean
  max_context_tokens?: number

  // Web search
  web_search_enabled?: boolean
  web_search_threshold?: number
  web_search_mode?: 'fallback' | 'augment'
  web_search_api_key?: string

  // Embedding config
  embedding_api_key?: string
  embedding_base_url?: string
}

export interface Source {
  source_id: string
  filename: string
  page?: number
  snippet: string
  content?: string
  chunk_index?: number
  file_id?: string
  score?: number

  // Web search support
  source_type?: 'local' | 'web'
  url?: string
}

export interface RetrievalDebug {
  rewritten_query?: string
  queries?: string[]
  retrieval_method?: string
  k?: number
  scores?: number[]
}

export interface QueryResponse {
  answer: string
  sources: Source[]
  debug?: RetrievalDebug
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface QueryRequest {
  question: string
  history?: ChatMessage[]
  settings?: QuerySettings
}

export async function queryRAG(
  projectId: string,
  question: string,
  history: ChatMessage[] = [],
  settings?: QuerySettings,
): Promise<QueryResponse> {
  const response = await api.post<QueryResponse>(`/api/projects/${projectId}/query`, {
    question,
    history,
    settings,
  })
  return response.data
}

export function getErrorMessage(error: any): string {
  if (error?.response?.data) {
    const detail = error.response.data.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      // FastAPI validation errors
      return detail.map((e: any) => e.msg || JSON.stringify(e)).join('; ')
    }
    if (typeof detail === 'object') return JSON.stringify(detail)
  }
  return error?.message ?? 'Unknown error'
}

// ── Study Mode ──────────────────────────────────────────
export type StudyMode = 'quiz' | 'summary' | 'flashcards'

export interface StudyRequest {
  mode: StudyMode
  count?: number
  topic?: string
  settings?: QuerySettings
}

export interface StudyResponse {
  content: string
  mode: string
  sources: Source[]
}

export function generateStudyGuide(
  projectId: string,
  req: StudyRequest,
): Promise<StudyResponse> {
  return api.post<StudyResponse>(`/api/projects/${projectId}/study`, req).then((r) => r.data)
}

// ── Chat History ────────────────────────────────────────
export interface ChatMessageOut {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
  metadata_json?: {
    sources?: Source[]
    debug?: RetrievalDebug
  }
}

export function fetchProjectHistory(projectId: string): Promise<ChatMessageOut[]> {
  return api.get<ChatMessageOut[]>(`/api/projects/${projectId}/history`).then((r) => r.data)
}

export function clearProjectHistory(projectId: string): Promise<void> {
  return api.delete(`/api/projects/${projectId}/history`).then(() => undefined)
}

export default api
