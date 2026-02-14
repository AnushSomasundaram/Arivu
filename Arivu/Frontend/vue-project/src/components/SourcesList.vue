<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { Source } from '@/lib/api'

defineProps<{ sources: Source[] }>()
const router = useRouter()

function viewSource(source: Source) {
  router.push({
    path: '/sources',
    query: {
      source_id: source.source_id,
      filename: source.filename,
      page: source.page?.toString(),
      snippet: source.snippet,
      content: source.content,
    },
  })
}
</script>

<template>
  <div v-if="sources.length" class="flex flex-col gap-2">
    <div
      v-for="(src, i) in sources"
      :key="src.source_id"
      class="cursor-pointer rounded-lg border border-gray-200 bg-white p-3 hover:border-gray-300 hover:shadow-sm transition-all"
      @click="viewSource(src)"
    >
      <div class="flex items-center gap-2 text-sm">
        <span class="font-medium text-gray-700">[{{ i + 1 }}] {{ src.filename }}</span>
        <span v-if="src.page != null" class="text-gray-400">· p.{{ src.page }}</span>
      </div>
      <p class="mt-1 text-xs leading-relaxed text-gray-500 line-clamp-3">{{ src.snippet }}</p>
    </div>
  </div>
  <p v-else class="text-sm text-gray-400">No sources available.</p>
</template>
