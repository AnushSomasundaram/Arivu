<script setup lang="ts">
import { ref } from 'vue'
import type { RetrievalDebug, Source } from '@/lib/api'

defineProps<{
  debug?: RetrievalDebug
  sources?: Source[]
}>()

const expanded = ref(false)
</script>

<template>
  <div v-if="debug || sources?.length" class="mt-2">
    <button
      class="flex items-center gap-1 rounded px-2 py-1 text-xs text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
      @click="expanded = !expanded"
    >
      <svg
        class="h-3 w-3 transition-transform"
        :class="expanded ? 'rotate-90' : ''"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        stroke-width="2"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
      </svg>
      RAG Debug
    </button>

    <div
      v-if="expanded"
      class="mt-1.5 rounded-lg bg-gray-50 border border-gray-100 p-3 text-xs text-gray-600 space-y-2"
    >
      <!-- Retrieval method -->
      <div v-if="debug?.retrieval_method" class="flex gap-2">
        <span class="font-medium text-gray-500">Method:</span>
        <span>{{ debug.retrieval_method }}</span>
      </div>

      <!-- K -->
      <div v-if="debug?.k" class="flex gap-2">
        <span class="font-medium text-gray-500">k:</span>
        <span>{{ debug.k }}</span>
      </div>

      <!-- Rewritten query -->
      <div v-if="debug?.rewritten_query">
        <span class="font-medium text-gray-500">Rewritten query:</span>
        <p class="mt-0.5 rounded bg-white px-2 py-1 border border-gray-100 italic">
          {{ debug.rewritten_query }}
        </p>
      </div>

      <!-- Multi-queries -->
      <div v-if="debug?.queries?.length">
        <span class="font-medium text-gray-500">Sub-queries:</span>
        <ul class="mt-0.5 list-disc pl-4 space-y-0.5">
          <li v-for="(q, i) in debug.queries" :key="i">{{ q }}</li>
        </ul>
      </div>

      <!-- Retrieved chunks summary -->
      <div v-if="sources?.length">
        <span class="font-medium text-gray-500">Retrieved chunks ({{ sources.length }}):</span>
        <ul class="mt-0.5 space-y-0.5">
          <li
            v-for="(src, i) in sources"
            :key="src.source_id"
            class="flex items-center gap-2"
          >
            <span class="text-gray-400">[{{ i + 1 }}]</span>
            <span>{{ src.filename }}</span>
            <span v-if="src.page != null" class="text-gray-400">p.{{ src.page }}</span>
            <span v-if="src.score != null" class="ml-auto text-gray-400">
              score: {{ src.score.toFixed(3) }}
            </span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
