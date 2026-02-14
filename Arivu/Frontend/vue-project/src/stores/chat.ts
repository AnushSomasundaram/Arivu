import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import {
  queryRAG,
  getErrorMessage,
  fetchProjectHistory,
  type Source,
  type RetrievalDebug,
} from '@/lib/api'
import { useSettingsStore } from './settings'
import { useProjectsStore } from './projects'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  debug?: RetrievalDebug
  error?: boolean
  thinking?: boolean
  timestamp: number
}

let nextId = 0
function makeId() {
  return `msg-${Date.now()}-${nextId++}`
}

interface ProjectMessages {
  [projectId: string]: ChatMessage[]
}

export const useChatStore = defineStore('chat', () => {
  const allMessages = ref<ProjectMessages>({})
  const querying = ref(false)
  const lastSources = ref<Source[]>([])

  function pid(): string {
    return useProjectsStore().activeProjectId
  }

  const messages = computed<ChatMessage[]>(() => allMessages.value[pid()] ?? [])

  async function send(question: string) {
    const projectId = pid()
    if (!allMessages.value[projectId]) allMessages.value[projectId] = []

    const userMsg: ChatMessage = {
      id: makeId(),
      role: 'user',
      content: question,
      timestamp: Date.now(),
    }
    allMessages.value[projectId].push(userMsg)

    const thinkingId = makeId()
    const thinkingMsg: ChatMessage = {
      id: thinkingId,
      role: 'assistant',
      content: 'Thinking...',
      timestamp: Date.now(),
      thinking: true,
    }
    allMessages.value[projectId].push(thinkingMsg)

    querying.value = true
    const settings = useSettingsStore()

    try {
      // Prepare history (last 10 messages)
      const history = messages.value
        .slice(-10)
        .filter((m) => !m.error && !m.thinking) // Filter out error/thinking states
        .map((m) => ({
          role: m.role,
          content: m.content || '',
        }))

      const data = await queryRAG(projectId, question, history, settings.asPayload())

      // Remove thinking indicator
      allMessages.value[projectId] = allMessages.value[projectId].filter((m) => m.id !== thinkingId)

      const assistantMsg: ChatMessage = {
        id: makeId(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        debug: data.debug,
        timestamp: Date.now(),
      }
      allMessages.value[projectId].push(assistantMsg)
      lastSources.value = data.sources
    } catch (e: any) {
      const errMsg: ChatMessage = {
        id: makeId(),
        role: 'assistant',
        content: getErrorMessage(e) ?? 'Something went wrong. Please try again.',
        error: true,
        timestamp: Date.now(),
      }
      allMessages.value[projectId].push(errMsg)
    } finally {
      querying.value = false
    }
  }

  function clear() {
    allMessages.value[pid()] = []
    lastSources.value = []
  }

  async function loadHistory(projectId: string) {
    if (!projectId) return
    try {
      const history = await fetchProjectHistory(projectId)
      allMessages.value[projectId] = history.map((h) => ({
        id: h.id,
        role: h.role as 'user' | 'assistant',
        content: h.content,
        timestamp: new Date(h.created_at).getTime(),
        sources: h.metadata_json?.sources,
        debug: h.metadata_json?.debug,
      }))
    } catch (e) {
      console.error('Failed to load history', e)
    }
  }

  return { messages, querying, lastSources, send, clear, loadHistory }
})
