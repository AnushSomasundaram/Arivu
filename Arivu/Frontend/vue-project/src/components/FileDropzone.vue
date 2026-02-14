<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{ (e: 'files', files: File[]): void }>()

const dragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

function onDrop(e: DragEvent) {
  dragging.value = false
  const files = Array.from(e.dataTransfer?.files ?? [])
  if (files.length) emit('files', files)
}

function onPick(e: Event) {
  const input = e.target as HTMLInputElement
  const files = Array.from(input.files ?? [])
  if (files.length) emit('files', files)
  input.value = ''
}
</script>

<template>
  <div
    class="relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 transition-colors"
    :class="dragging ? 'border-blue-400 bg-blue-50' : 'border-gray-300 bg-gray-50 hover:border-gray-400'"
    @dragover.prevent="dragging = true"
    @dragleave.prevent="dragging = false"
    @drop.prevent="onDrop"
  >
    <p class="text-sm text-gray-500">
      Drag & drop files here, or
    </p>
    <button
      class="mt-2 rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 transition-colors"
      @click="fileInput?.click()"
    >
      Browse files
    </button>
    <input
      ref="fileInput"
      type="file"
      multiple
      class="hidden"
      @change="onPick"
    />
    <p class="mt-2 text-xs text-gray-400">PDF, TXT, CSV, DOCX, and more</p>
  </div>
</template>
