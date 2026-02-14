<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const filename = computed(() => (route.query.filename as string) ?? 'Unknown')
const page = computed(() => route.query.page as string | undefined)
const sourceId = computed(() => route.query.source_id as string | undefined)
const chunkIndex = computed(() => route.query.chunk_index as string | undefined)
const fileId = computed(() => route.query.file_id as string | undefined)
const projectId = computed(() => route.query.projectId as string | undefined)
const snippet = computed(() => (route.query.snippet as string) ?? '')
const content = computed(() => (route.query.content as string) ?? snippet.value)

function highlightSnippet(text: string, highlight: string): string {
  if (!highlight) return text
  const escaped = highlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(
    new RegExp(`(${escaped})`, 'gi'),
    '<mark class="bg-yellow-200 rounded px-0.5">$1</mark>',
  )
}

const rendered = computed(() => highlightSnippet(content.value, snippet.value))
</script>

<template>
  <div class="mx-auto max-w-3xl px-6 py-8">
    <!-- Back button -->
    <button
      class="mb-6 flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition-colors"
      @click="router.back()"
    >
      ← Back to chat
    </button>

    <!-- Metadata -->
    <div class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <h2 class="text-lg font-semibold text-gray-800">{{ filename }}</h2>
      <div class="mt-2 flex flex-wrap gap-2">
        <span v-if="page" class="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-600">
          Page {{ page }}
        </span>
        <span v-if="chunkIndex" class="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-600">
          Chunk #{{ chunkIndex }}
        </span>
        <span v-if="sourceId" class="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-600">
          ID: {{ sourceId }}
        </span>
        <span v-if="fileId" class="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-600">
          File: {{ fileId }}
        </span>
        <span v-if="projectId" class="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs text-blue-600">
          Project: {{ projectId }}
        </span>
      </div>

      <!-- Content -->
      <div
        class="mt-6 whitespace-pre-wrap rounded-lg bg-gray-50 p-4 text-sm leading-relaxed text-gray-700 border border-gray-100"
        v-html="rendered"
      />
    </div>

    <!-- Empty fallback -->
    <div
      v-if="!content"
      class="mt-8 text-center text-sm text-gray-400"
    >
      No source content available. Try clicking a source from a chat response.
    </div>
  </div>
</template>
