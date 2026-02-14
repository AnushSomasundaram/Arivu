<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useFilesStore } from '@/stores/files'
import { useAppStore } from '@/stores/app'
import { useProjectsStore } from '@/stores/projects'
import FileDropzone from '@/components/FileDropzone.vue'
import FileTable from '@/components/FileTable.vue'

const files = useFilesStore()
const app = useAppStore()
const projects = useProjectsStore()

onMounted(() => {
  if (app.backendOnline) files.load()
})

// reload files when switching projects
watch(() => projects.activeProjectId, () => {
  files.reset()
  if (app.backendOnline) files.load()
})

function onFilesDropped(raw: File[]) {
  files.upload(raw)
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-6 py-8">
    <h2 class="text-2xl font-semibold text-gray-800">Documents</h2>
    <p class="mt-1 text-sm text-gray-500">
      Upload and manage files for <span class="font-medium">{{ projects.activeProject.name }}</span>.
    </p>

    <!-- Upload zone -->
    <div class="mt-6">
      <FileDropzone @files="onFilesDropped" />
      <div v-if="files.uploading" class="mt-3 flex items-center gap-2 text-sm text-gray-500">
        <span class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-gray-400 border-t-transparent" />
        Uploading…
      </div>
    </div>

    <!-- File table -->
    <div class="mt-8">
      <!-- Loading state -->
      <div v-if="files.loading" class="flex items-center gap-2 text-sm text-gray-400">
        <span class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-gray-400 border-t-transparent" />
        Loading files…
      </div>

      <!-- Error state -->
      <div
        v-else-if="files.error"
        class="rounded-xl border border-red-200 bg-red-50 px-4 py-6 text-center text-sm text-red-600"
      >
        {{ files.error }}
        <button
          class="ml-2 underline hover:text-red-800"
          @click="files.load()"
        >
          Retry
        </button>
      </div>

      <!-- Empty state -->
      <div
        v-else-if="files.files.length === 0"
        class="rounded-xl border border-dashed border-gray-300 bg-gray-50 px-4 py-12 text-center"
      >
        <div class="text-3xl mb-2">📁</div>
        <p class="text-sm font-medium text-gray-600">No documents yet</p>
        <p class="mt-1 text-xs text-gray-400">Upload files above to get started.</p>
      </div>

      <!-- Table -->
      <FileTable
        v-else
        :files="files.files"
        @delete="files.remove"
        @reindex="files.reindex"
      />
    </div>
  </div>
</template>
