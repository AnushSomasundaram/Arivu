<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { ChatMessage } from '@/stores/chat'
import type { Source } from '@/lib/api'
import { useProjectsStore } from '@/stores/projects'
import ChatDebugPanel from './ChatDebugPanel.vue'

const props = defineProps<{ msg: ChatMessage }>()
const router = useRouter()
const projects = useProjectsStore()

function copyText() {
  navigator.clipboard.writeText(props.msg.content)
}

function viewSource(source: Source) {
  router.push({
    path: '/sources',
    query: {
      source_id: source.source_id,
      filename: source.filename,
      page: source.page?.toString(),
      snippet: source.snippet,
      content: source.content,
      chunk_index: source.chunk_index?.toString(),
      file_id: source.file_id,
      projectId: projects.activeProjectId,
    },
  })
}

import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import { computed } from 'vue'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {
        // ignore
      }
    }
    return '' // use external default escaping
  }
})

const renderedContent = computed(() => {
  return md.render(props.msg.content)
})
</script>

<template>
  <div
    class="flex gap-3"
    :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
  >
    <div
      class="max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed"
      :class="[
        msg.role === 'user'
          ? 'bg-gray-900 text-white'
          : msg.error
            ? 'bg-red-50 text-red-800 border border-red-200'
            : 'bg-white text-gray-800 border border-gray-200 shadow-sm',
      ]"
    >
      <!-- Message body -->
      <div class="prose-content" v-html="renderedContent"></div>

      <!-- Sources -->
      <div
        v-if="msg.sources?.length"
        class="mt-3 border-t border-gray-200 pt-3"
      >
        <p class="mb-1.5 text-xs font-semibold uppercase tracking-wide text-gray-500">
          Sources
        </p>
        <ul class="flex flex-col gap-1">
          <li v-for="(src, i) in msg.sources" :key="src.source_id">
            <button
              class="w-full rounded-lg px-3 py-2 text-left text-xs transition-colors"
              :class="[
                src.source_type === 'web'
                  ? 'bg-blue-50 hover:bg-blue-100'
                  : 'bg-gray-50 hover:bg-gray-100',
              ]"
              @click="viewSource(src)"
            >
              <!-- Source type indicator -->
              <span
                class="inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide"
                :class="src.source_type === 'web' ? 'text-blue-600' : 'text-gray-600'"
              >
                <svg
                  v-if="src.source_type === 'web'"
                  class="h-3 w-3"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"
                  />
                </svg>
                <svg
                  v-else
                  class="h-3 w-3"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                {{ src.source_type === 'web' ? 'Web' : 'Local' }}
              </span>

              <!-- Source title/filename -->
              <span
                class="ml-2 font-medium"
                :class="src.source_type === 'web' ? 'text-blue-700' : 'text-gray-700'"
              >
                [{{ i + 1 }}] {{ src.filename }}
              </span>

              <!-- Metadata -->
              <span v-if="src.page != null" class="text-gray-400"> · p.{{ src.page }}</span>
              <span v-if="src.score != null" class="text-gray-400">
                · {{ (src.score * 100).toFixed(0) }}%
              </span>

              <!-- URL for web sources -->
              <a
                v-if="src.source_type === 'web' && src.url"
                :href="src.url"
                target="_blank"
                class="mt-0.5 block truncate text-[10px] text-blue-500 hover:underline"
                @click.stop
              >
                {{ src.url }}
              </a>

              <!-- Snippet -->
              <p class="mt-0.5 line-clamp-2 text-gray-500">{{ src.snippet }}</p>
            </button>
          </li>
        </ul>
      </div>

      <!-- Actions + Debug -->
      <div
        v-if="msg.role === 'assistant' && !msg.error"
        class="mt-2"
      >
        <div class="flex gap-2">
          <button
            class="rounded px-2 py-1 text-xs text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
            @click="copyText"
          >
            Copy
          </button>
        </div>

        <ChatDebugPanel :debug="msg.debug" :sources="msg.sources" />
      </div>
    </div>
  </div>
</template>
