import { ref, watch } from 'vue'
import { defineStore, storeToRefs } from 'pinia'
import type { QuerySettings } from '@/lib/api'
import { useProjectsStore } from './projects'

const STORAGE_KEY = 'arivu-settings'

interface SettingsMap {
  [projectId: string]: QuerySettings
}

const DEFAULTS: QuerySettings = {
  k: 5,
  search_type: 'similarity',
  temperature: 0.2,
  model: 'llama3',
  chunk_size: 1000,
  chunk_overlap: 150,
  embedding_model: 'all-MiniLM-L6-v2',
  query_translation: false,
  show_debug: false,
  api_key: '',
  base_url: '',

  // RAG quality
  min_score: 0.5,
  enable_reranking: true,
  max_context_tokens: 6000,

  // Web search
  web_search_enabled: false,
  web_search_threshold: 0.5,
  web_search_mode: 'fallback',
  web_search_api_key: '',

  // Embedding config
  embedding_api_key: '',
  embedding_base_url: '',
}

function loadMap(): SettingsMap {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw) as SettingsMap
  } catch {
    // ignore corrupt storage
  }
  return {}
}

function saveMap(map: SettingsMap) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(map))
}

export const useSettingsStore = defineStore('settings', () => {
  const allSettings = ref<SettingsMap>(loadMap())
  const projectsStore = useProjectsStore()
  const { activeProjectId } = storeToRefs(projectsStore)

  const k = ref(DEFAULTS.k)
  const searchType = ref<'similarity' | 'mmr'>(DEFAULTS.search_type)
  const temperature = ref(DEFAULTS.temperature)
  const model = ref(DEFAULTS.model)
  const chunkSize = ref(DEFAULTS.chunk_size ?? 1000)
  const chunkOverlap = ref(DEFAULTS.chunk_overlap ?? 150)
  const embeddingModel = ref(DEFAULTS.embedding_model ?? 'all-MiniLM-L6-v2')
  const queryTranslation = ref(DEFAULTS.query_translation ?? false)
  const showDebug = ref(DEFAULTS.show_debug ?? false)
  const apiKey = ref(DEFAULTS.api_key ?? '')
  const baseUrl = ref(DEFAULTS.base_url ?? '')

  // RAG quality
  const minScore = ref(DEFAULTS.min_score ?? 0.5)
  const enableReranking = ref(DEFAULTS.enable_reranking ?? true)
  const maxContextTokens = ref(DEFAULTS.max_context_tokens ?? 6000)

  // Web search
  const webSearchEnabled = ref(DEFAULTS.web_search_enabled ?? false)
  const webSearchThreshold = ref(DEFAULTS.web_search_threshold ?? 0.5)
  const webSearchMode = ref<'fallback' | 'augment'>(DEFAULTS.web_search_mode ?? 'fallback')
  const webSearchApiKey = ref(DEFAULTS.web_search_api_key ?? '')

  // Internal Embedding Keys (not in defaults usually, but persisted)
  const embeddingApiKey = ref(DEFAULTS.embedding_api_key ?? '')
  const embeddingBaseUrl = ref(DEFAULTS.embedding_base_url ?? '')

  function loadCurrent() {
    const s = allSettings.value[activeProjectId.value] ?? { ...DEFAULTS }
    k.value = s.k
    searchType.value = s.search_type
    temperature.value = s.temperature
    model.value = s.model
    chunkSize.value = s.chunk_size ?? 1000
    chunkOverlap.value = s.chunk_overlap ?? 150
    embeddingModel.value = s.embedding_model ?? 'all-MiniLM-L6-v2'
    queryTranslation.value = s.query_translation ?? false
    showDebug.value = s.show_debug ?? false
    apiKey.value = s.api_key ?? ''
    baseUrl.value = s.base_url ?? ''

    // RAG quality
    minScore.value = s.min_score ?? 0.5
    enableReranking.value = s.enable_reranking ?? true
    maxContextTokens.value = s.max_context_tokens ?? 6000

    // Web search
    webSearchEnabled.value = s.web_search_enabled ?? false
    webSearchThreshold.value = s.web_search_threshold ?? 0.5
    webSearchMode.value = s.web_search_mode ?? 'fallback'
    webSearchApiKey.value = s.web_search_api_key ?? ''

    // Embedding keys
    embeddingApiKey.value = s.embedding_api_key ?? ''
    embeddingBaseUrl.value = s.embedding_base_url ?? ''
  }

  // load on init
  loadCurrent()

  // when active project changes, load that project's settings
  watch(activeProjectId, loadCurrent)

  function asPayload(): QuerySettings {
    return {
      k: k.value || 5,
      search_type: searchType.value,
      temperature: temperature.value,
      model: model.value,
      chunk_size: chunkSize.value || 1000,
      chunk_overlap: chunkOverlap.value || 150,
      embedding_model: embeddingModel.value || 'all-MiniLM-L6-v2',
      query_translation: queryTranslation.value,
      show_debug: showDebug.value,
      api_key: apiKey.value,
      base_url: baseUrl.value,

      // RAG quality
      min_score: minScore.value || 0.5,
      enable_reranking: enableReranking.value,
      max_context_tokens: maxContextTokens.value || 6000,

      // Web search
      web_search_enabled: webSearchEnabled.value,
      web_search_threshold: webSearchThreshold.value || 0.5,
      web_search_mode: webSearchMode.value,
      web_search_api_key: webSearchApiKey.value,

      // Embedding keys
      embedding_api_key: embeddingApiKey.value,
      embedding_base_url: embeddingBaseUrl.value,
    }
  }

  function persist() {
    allSettings.value[activeProjectId.value] = asPayload()
    saveMap(allSettings.value)
  }

  watch([
    k, searchType, temperature, model,
    chunkSize, chunkOverlap, embeddingModel,
    queryTranslation, showDebug,
    apiKey, baseUrl,
    minScore, enableReranking, maxContextTokens,
    webSearchEnabled, webSearchThreshold, webSearchMode, webSearchApiKey,
    embeddingApiKey, embeddingBaseUrl
  ], persist)

  return {
    k, searchType, temperature, model,
    chunkSize, chunkOverlap, embeddingModel,
    queryTranslation, showDebug,
    apiKey, baseUrl,
    minScore, enableReranking, maxContextTokens,
    webSearchEnabled, webSearchThreshold, webSearchMode, webSearchApiKey,
    embeddingApiKey, embeddingBaseUrl,
    asPayload,
  }
})
