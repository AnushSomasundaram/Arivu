<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useProjectsStore } from '@/stores/projects'

import { useToast } from '@/lib/toast'

const settings = useSettingsStore()
const projects = useProjectsStore()
const toast = useToast()

const showAdvanced = ref(false)

const ollamaModels = ['llama3', 'llama3.1', 'llama3.2', 'mistral', 'qwen2.5', 'phi3', 'gemma2']

const modelProvider = computed({
  get: () => settings.model.includes('gpt') || settings.model.includes('openai') ? 'openai' : 'ollama',
  set: (val: string) => {
    if (val === 'openai') settings.model = 'gpt-4o-mini'
    else settings.model = 'llama3'
  }
})

const embeddingModelOptions = [
  { label: 'Local (Fast) - all-MiniLM-L6-v2', value: 'local:all-MiniLM-L6-v2' },
  { label: 'Ollama', value: 'ollama:nomic-embed-text' },
  { label: 'OpenAI - text-embedding-3-small', value: 'openai:text-embedding-3-small' },
]

function saveSettings() {
  // Settings are auto-saved by the store watcher, but we provide feedback
  toast.show('Settings saved', 'success')
}

function updateEmbedding(event: Event) {
  const select = event.target as HTMLSelectElement
  const newVal = select.value
  if (projects.activeProject && newVal) {
    projects.update(projects.activeProject.id, { embedding_model: newVal })
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl px-6 py-8">
    <h2 class="text-2xl font-semibold text-gray-800">Settings</h2>
    <p class="mt-1 text-sm text-gray-500">
      Settings for <span class="font-medium">{{ projects.activeProject.name }}</span>. Changes are saved automatically per project.
    </p>

    <!-- Retrieval section -->
    <section class="mt-8">
      <h3 class="text-sm font-semibold uppercase tracking-wide text-gray-500">Retrieval</h3>

      <div class="mt-4 flex flex-col gap-5">
        <!-- Top-k -->
        <div>
          <label for="topK" class="block text-sm font-medium text-gray-700">
            Top-K results
          </label>
          <p class="text-xs text-gray-400">Number of chunks retrieved per query (1–20)</p>
          <input
            id="topK"
            v-model.number="settings.k"
            type="number"
            min="1"
            max="20"
            class="mt-1 w-24 rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
          />
        </div>

        <!-- Search type -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Search type</label>
          <div class="mt-2 flex gap-3">
            <button
              v-for="opt in (['similarity', 'mmr'] as const)"
              :key="opt"
              class="rounded-lg border px-4 py-2 text-sm font-medium transition-colors"
              :class="
                settings.searchType === opt
                  ? 'border-gray-900 bg-gray-900 text-white'
                  : 'border-gray-300 text-gray-600 hover:border-gray-400'
              "
              @click="settings.searchType = opt"
            >
              {{ opt.toUpperCase() }}
            </button>
          </div>
        </div>

        <!-- Query translation -->
        <div class="flex items-center gap-3">
          <label for="queryTranslation" class="text-sm font-medium text-gray-700">
            Query rewriting
          </label>
          <button
            id="queryTranslation"
            role="switch"
            :aria-checked="settings.queryTranslation"
            class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
            :class="settings.queryTranslation ? 'bg-gray-900' : 'bg-gray-300'"
            @click="settings.queryTranslation = !settings.queryTranslation"
          >
            <span
              class="inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform"
              :class="settings.queryTranslation ? 'translate-x-[18px]' : 'translate-x-[3px]'"
            />
          </button>
          <p class="text-xs text-gray-400">Expand/rewrite queries for better retrieval</p>
        </div>
      </div>
    </section>

    <!-- RAG Quality section -->
    <section class="mt-10">
      <h3 class="text-sm font-semibold uppercase tracking-wide text-gray-500">RAG Quality</h3>

      <div class="mt-4 flex flex-col gap-5">
        <!-- Reranking -->
        <div class="flex items-center gap-3">
          <label for="enableReranking" class="text-sm font-medium text-gray-700">
            Cross-encoder reranking
          </label>
          <button
            id="enableReranking"
            role="switch"
            :aria-checked="settings.enableReranking"
            class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
            :class="settings.enableReranking ? 'bg-gray-900' : 'bg-gray-300'"
            @click="settings.enableReranking = !settings.enableReranking"
          >
            <span
              class="inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform"
              :class="settings.enableReranking ? 'translate-x-[18px]' : 'translate-x-[3px]'"
            />
          </button>
          <p class="text-xs text-gray-400">Improves relevance ranking (adds ~100ms latency)</p>
        </div>

        <!-- Confidence threshold -->
        <div>
          <label for="minScore" class="block text-sm font-medium text-gray-700">
            Minimum confidence score: {{ settings.minScore.toFixed(2) }}
          </label>
          <p class="text-xs text-gray-400">Filter out low-confidence chunks (0 = no filtering)</p>
          <input
            id="minScore"
            v-model.number="settings.minScore"
            type="range"
            min="0"
            max="1"
            step="0.05"
            class="mt-2 w-full accent-gray-900"
          />
          <div class="flex justify-between text-xs text-gray-400">
            <span>0.0</span>
            <span>1.0</span>
          </div>
        </div>

        <!-- Max context tokens -->
        <div>
          <label for="maxContextTokens" class="block text-sm font-medium text-gray-700">
            Max context tokens
          </label>
          <p class="text-xs text-gray-400">
            Truncate context to prevent exceeding model limits (2000–10000)
          </p>
          <input
            id="maxContextTokens"
            v-model.number="settings.maxContextTokens"
            type="number"
            min="2000"
            max="10000"
            step="500"
            class="mt-1 w-32 rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
          />
        </div>
      </div>
    </section>

    <!-- Web Search section -->
    <section class="mt-10">
      <h3 class="text-sm font-semibold uppercase tracking-wide text-gray-500">Web Search</h3>
      <p class="mt-1 text-xs text-gray-500">
        Fallback to external web search when local documents are insufficient
      </p>

      <div class="mt-4 flex flex-col gap-5">
        <!-- Enable web search -->
        <div class="flex items-center gap-3">
          <label for="webSearchEnabled" class="text-sm font-medium text-gray-700">
            Enable web search
          </label>
          <button
            id="webSearchEnabled"
            role="switch"
            :aria-checked="settings.webSearchEnabled"
            class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
            :class="settings.webSearchEnabled ? 'bg-gray-900' : 'bg-gray-300'"
            @click="settings.webSearchEnabled = !settings.webSearchEnabled"
          >
            <span
              class="inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform"
              :class="settings.webSearchEnabled ? 'translate-x-[18px]' : 'translate-x-[3px]'"
            />
          </button>
          <p class="text-xs text-gray-400">Search web when local results are insufficient</p>
        </div>

        <div v-if="settings.webSearchEnabled" class="ml-4 flex flex-col gap-5 border-l-2 border-gray-200 pl-4">
          <!-- Search mode -->
          <div>
            <label class="block text-sm font-medium text-gray-700">Search mode</label>
            <div class="mt-2 flex gap-3">
              <button
                v-for="mode in (['fallback', 'augment'] as const)"
                :key="mode"
                class="rounded-lg border px-4 py-2 text-sm font-medium transition-colors"
                :class="
                  settings.webSearchMode === mode
                    ? 'border-gray-900 bg-gray-900 text-white'
                    : 'border-gray-300 text-gray-600 hover:border-gray-400'
                "
                @click="settings.webSearchMode = mode"
              >
                {{ mode.charAt(0).toUpperCase() + mode.slice(1) }}
              </button>
            </div>
            <p class="mt-1 text-xs text-gray-400">
              <span v-if="settings.webSearchMode === 'fallback'">
                Only search web when local results are missing or low confidence
              </span>
              <span v-else>
                Always augment local results with web search
              </span>
            </p>
          </div>

          <!-- Confidence threshold -->
          <div>
            <label for="webSearchThreshold" class="block text-sm font-medium text-gray-700">
              Web search confidence threshold: {{ settings.webSearchThreshold.toFixed(2) }}
            </label>
            <p class="text-xs text-gray-400">
              Trigger web search if best local score is below this (fallback mode only)
            </p>
            <input
              id="webSearchThreshold"
              v-model.number="settings.webSearchThreshold"
              type="range"
              min="0"
              max="1"
              step="0.05"
              class="mt-2 w-full accent-gray-900"
              :disabled="settings.webSearchMode === 'augment'"
            />
            <div class="flex justify-between text-xs text-gray-400">
              <span>0.0</span>
              <span>1.0</span>
            </div>
          </div>

          <!-- Tavily API key -->
          <div>
            <label for="webSearchApiKey" class="block text-sm font-medium text-gray-700">
              Tavily API Key
            </label>
            <p class="text-xs text-gray-400">
              Get your API key at
              <a
                href="https://tavily.com"
                target="_blank"
                class="text-blue-600 hover:underline"
              >
                tavily.com
              </a>
              (Leave empty to use backend default from .env)
            </p>
            <input
              id="webSearchApiKey"
              v-model="settings.webSearchApiKey"
              type="password"
              placeholder="Enter Tavily API key..."
              class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
            />
          </div>
        </div>
      </div>
    </section>

    <!-- Generation section -->
    <section class="mt-10">
      <h3 class="text-sm font-semibold uppercase tracking-wide text-gray-500">Generation</h3>

      <div class="mt-4 flex flex-col gap-5">
        <!-- Temperature -->
        <div>
          <label for="temp" class="block text-sm font-medium text-gray-700">
            Temperature: {{ settings.temperature.toFixed(2) }}
          </label>
          <p class="text-xs text-gray-400">Lower = more precise, Higher = more creative</p>
          <input
            id="temp"
            v-model.number="settings.temperature"
            type="range"
            min="0"
            max="1"
            step="0.05"
            class="mt-2 w-full accent-gray-900"
          />
          <div class="flex justify-between text-xs text-gray-400">
            <span>0.0</span>
            <span>1.0</span>
          </div>
        </div>

        <!-- Model Provider -->
        <div>
          <label for="model" class="block text-sm font-medium text-gray-700">Model</label>
          <select
            id="model"
            v-model="modelProvider"
            class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
          >
            <option value="openai">OpenAI</option>
            <option value="ollama">Ollama</option>
          </select>
        </div>

        <!-- OpenAI API Key -->
        <div v-if="modelProvider === 'openai'" class="pl-4 border-l-2 border-gray-200">
          <label for="apiKey" class="block text-sm font-medium text-gray-700">OpenAI API Key</label>
          <p class="text-xs text-gray-400">Leave empty to use backend default (from .env)</p>
          <input
            id="apiKey"
            v-model="settings.apiKey"
            type="password"
            placeholder="sk-..."
            class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
          />
        </div>

        <!-- Ollama Config -->
        <div v-if="modelProvider === 'ollama'" class="pl-4 border-l-2 border-gray-200 flex flex-col gap-3">
          <div>
            <label for="ollamaModel" class="block text-sm font-medium text-gray-700">Ollama Model</label>
            <select
              id="ollamaModel"
              v-model="settings.model"
              class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
            >
              <option v-for="m in ollamaModels" :key="m" :value="m">{{ m }}</option>
            </select>
          </div>
          <div>
            <label for="baseUrl" class="block text-sm font-medium text-gray-700">Ollama Base URL</label>
            <p class="text-xs text-gray-400">Default: http://localhost:11434</p>
            <input
              id="baseUrl"
              v-model="settings.baseUrl"
              type="text"
              placeholder="http://localhost:11434"
              class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
            />
          </div>
        </div>

      </div>
    </section>

    <!-- Debug section -->
    <section class="mt-10">
      <h3 class="text-sm font-semibold uppercase tracking-wide text-gray-500">Debug</h3>

      <div class="mt-4 flex items-center gap-3">
        <label for="showDebug" class="text-sm font-medium text-gray-700">
          Show RAG debug panel
        </label>
        <button
          id="showDebug"
          role="switch"
          :aria-checked="settings.showDebug"
          class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
          :class="settings.showDebug ? 'bg-gray-900' : 'bg-gray-300'"
          @click="settings.showDebug = !settings.showDebug"
        >
          <span
            class="inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform"
            :class="settings.showDebug ? 'translate-x-[18px]' : 'translate-x-[3px]'"
          />
        </button>
        <p class="text-xs text-gray-400">Show rewritten queries, scores, and retrieval details in chat</p>
      </div>
    </section>

    <!-- Advanced section -->
    <section class="mt-10 border-t border-gray-200 pt-6">
      <button
        class="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-800 transition-colors"
        @click="showAdvanced = !showAdvanced"
      >
        <svg
          class="h-4 w-4 transition-transform"
          :class="showAdvanced ? 'rotate-90' : ''"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
        </svg>
        Advanced Ingestion Settings
      </button>

      <div v-if="showAdvanced" class="mt-4 flex flex-col gap-5">
        <!-- Embedding model -->
        <div>
          <label for="embeddingModel" class="block text-sm font-medium text-gray-700">Embedding model</label>
          <p class="text-xs text-gray-400">Controls how documents are vectorized. Changing this may require re-ingesting documents.</p>
          <select
            id="embeddingModel"
            :value="projects.activeProject?.embedding_model"
            class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
            @change="updateEmbedding"
          >
            <option v-for="opt in embeddingModelOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>

        <!-- Dynamic Embedding Config -->
        <div v-if="projects.activeProject?.embedding_model?.includes('openai')" class="pl-4 border-l-2 border-gray-200">
             <label for="embeddingApiKey" class="block text-sm font-medium text-gray-700">Embedding API Key (OpenAI)</label>
             <p class="text-xs text-gray-400">Required if not set in backend .env</p>
             <input
               id="embeddingApiKey"
               v-model="settings.embeddingApiKey"
               type="password"
               placeholder="sk-..."
               class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
             />
        </div>

        <div v-if="projects.activeProject?.embedding_model?.includes('ollama')" class="pl-4 border-l-2 border-gray-200 flex flex-col gap-3">
             <div>
               <label for="ollamaModelName" class="block text-sm font-medium text-gray-700">Ollama Embedding Model</label>
               <select
                 id="ollamaModelName"
                 :value="projects.activeProject?.embedding_model?.replace('ollama:', '')"
                 class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
                 @change="(e: Event) => { const v = (e.target as HTMLSelectElement).value; if (v && projects.activeProject) projects.update(projects.activeProject.id, { embedding_model: 'ollama:' + v }) }"
               >
                 <option value="nomic-embed-text">nomic-embed-text</option>
                 <option value="mxbai-embed-large">mxbai-embed-large</option>
                 <option value="all-minilm">all-minilm</option>
                 <option value="snowflake-arctic-embed">snowflake-arctic-embed</option>
               </select>
             </div>
             <div>
               <label for="embeddingBaseUrl" class="block text-sm font-medium text-gray-700">Ollama Base URL</label>
               <p class="text-xs text-gray-400">Default: http://localhost:11434</p>
               <input
                 id="embeddingBaseUrl"
                 v-model="settings.embeddingBaseUrl"
                 type="text"
                 placeholder="http://localhost:11434"
                 class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
               />
             </div>
        </div>

        <!-- Chunk size -->
        <div>
          <label for="chunkSize" class="block text-sm font-medium text-gray-700">
            Chunk size
          </label>
          <p class="text-xs text-gray-400">Max characters per chunk (200–4000)</p>
          <input
            id="chunkSize"
            v-model.number="settings.chunkSize"
            type="number"
            min="200"
            max="4000"
            step="100"
            class="mt-1 w-28 rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
          />
        </div>

        <!-- Chunk overlap -->
        <div>
          <label for="chunkOverlap" class="block text-sm font-medium text-gray-700">
            Chunk overlap
          </label>
          <p class="text-xs text-gray-400">Overlap between adjacent chunks (0–500)</p>
          <input
            id="chunkOverlap"
            v-model.number="settings.chunkOverlap"
            type="number"
            min="0"
            max="500"
            step="10"
            class="mt-1 w-28 rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
          />
        </div>
      </div>
    </section>

    <div class="mt-8 flex justify-end border-t border-gray-200 pt-6">
      <button
        class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 transition-colors"
        @click="saveSettings"
      >
        Save Settings
      </button>
    </div>
  </div>
</template>
