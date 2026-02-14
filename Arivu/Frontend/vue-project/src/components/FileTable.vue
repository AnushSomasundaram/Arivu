<script setup lang="ts">
import type { FileRecord, FileStatus } from '@/lib/api'

defineProps<{ files: FileRecord[] }>()
const emit = defineEmits<{
  (e: 'delete', id: string): void
  (e: 'reindex', id: string): void
}>()

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

const statusStyle: Record<FileStatus, string> = {
  queued: 'bg-gray-100 text-gray-600',
  parsing: 'bg-blue-100 text-blue-700',
  chunking: 'bg-blue-100 text-blue-700',
  embedding: 'bg-purple-100 text-purple-700',
  indexing: 'bg-yellow-100 text-yellow-700',
  indexed: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
}

const processingStatuses: FileStatus[] = ['queued', 'parsing', 'chunking', 'embedding', 'indexing']

function isProcessing(status: FileStatus): boolean {
  return processingStatuses.includes(status)
}

function statusLabel(status: FileStatus): string {
  const labels: Record<FileStatus, string> = {
    queued: 'Queued',
    parsing: 'Parsing',
    chunking: 'Chunking',
    embedding: 'Embedding',
    indexing: 'Indexing',
    indexed: 'Indexed',
    failed: 'Failed',
  }
  return labels[status] ?? status
}
</script>

<template>
  <div class="overflow-x-auto rounded-xl border border-gray-200 bg-white">
    <table class="w-full text-left text-sm">
      <thead class="bg-gray-50 text-xs uppercase tracking-wide text-gray-500">
        <tr>
          <th class="px-4 py-3">Filename</th>
          <th class="px-4 py-3">Type</th>
          <th class="px-4 py-3">Size</th>
          <th class="px-4 py-3">Status</th>
          <th class="px-4 py-3">Chunks</th>
          <th class="px-4 py-3">Created</th>
          <th class="px-4 py-3 text-right">Actions</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-100">
        <tr v-for="file in files" :key="file.id" class="hover:bg-gray-50 transition-colors">
          <td class="px-4 py-3 font-medium text-gray-800">{{ file.filename }}</td>
          <td class="px-4 py-3 text-gray-500">{{ file.mime_type ?? file.filename.split('.').pop() }}</td>
          <td class="px-4 py-3 text-gray-500">{{ formatBytes(file.size_bytes) }}</td>
          <td class="px-4 py-3">
            <div class="flex flex-col gap-1.5 min-w-[120px]">
              <div class="flex items-center justify-between gap-2">
                <span
                  class="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wider"
                  :class="statusStyle[file.status] ?? 'bg-gray-100 text-gray-600'"
                >
                  <span
                    v-if="isProcessing(file.status)"
                    class="inline-block h-2 w-2 animate-spin rounded-full border-2 border-current border-t-transparent opacity-60"
                  />
                  {{ statusLabel(file.status) }}
                </span>
                <span v-if="isProcessing(file.status) && file.progress !== undefined" class="text-[10px] tabular-nums font-semibold text-gray-400">
                  {{ file.progress }}%
                </span>
              </div>
              
              <!-- Progress Bar -->
              <div v-if="isProcessing(file.status)" class="h-1 w-full overflow-hidden rounded-full bg-gray-100">
                <div 
                  class="h-full bg-blue-500 transition-all duration-500 ease-out"
                  :style="{ width: `${file.progress ?? 0}%` }"
                />
              </div>
            </div>
          </td>
          <td class="px-4 py-3 text-gray-500">
            <template v-if="file.chunk_count != null">
              {{ file.chunk_count }}
              <span
                v-if="file.added_chunks != null || file.skipped_chunks != null"
                class="block text-[10px] text-gray-400 leading-tight"
              >
                <span v-if="file.added_chunks != null">+{{ file.added_chunks }} added</span>
                <span v-if="file.skipped_chunks != null"> · {{ file.skipped_chunks }} skipped</span>
              </span>
            </template>
            <template v-else>—</template>
          </td>
          <td class="px-4 py-3 text-gray-500">{{ formatDate(file.created_at) }}</td>
          <td class="px-4 py-3 text-right">
            <button
              class="mr-2 text-xs text-blue-600 hover:text-blue-800 transition-colors disabled:opacity-40"
              :disabled="isProcessing(file.status)"
              @click="emit('reindex', file.id)"
            >
              Reindex
            </button>
            <button
              class="text-xs text-red-500 hover:text-red-700 transition-colors disabled:opacity-40"
              :disabled="isProcessing(file.status)"
              @click="emit('delete', file.id)"
            >
              Delete
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
