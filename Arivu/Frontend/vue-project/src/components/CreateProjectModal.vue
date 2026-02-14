<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  (e: 'create', name: string, embeddingModel: string): void
  (e: 'close'): void
}>()

const name = ref('')
const embeddingModel = ref('local:all-MiniLM-L6-v2')

const embeddingOptions = [
  { label: 'Local (Fast, Private)', value: 'local:all-MiniLM-L6-v2' },
  { label: 'OpenAI (High Quality)', value: 'openai:text-embedding-3-small' },
  { label: 'Ollama (Custom)', value: 'ollama:nomic-embed-text' },
]

function submit() {
  const trimmed = name.value.trim()
  if (!trimmed) return
  emit('create', trimmed, embeddingModel.value)
  name.value = ''
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      @click.self="$emit('close')"
      @keydown="onKeydown"
    >
      <div class="w-full max-w-sm rounded-xl bg-white p-6 shadow-xl">
        <h3 class="text-lg font-semibold text-gray-800">New Project</h3>
        <p class="mt-1 text-sm text-gray-500">
          Create an isolated workspace with its own documents, chat, and settings.
        </p>

        <div class="mt-4 space-y-4">
          <!-- Name -->
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Name</label>
            <input
              v-model="name"
              type="text"
              placeholder="Project name"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-500 transition-colors"
              autofocus
              @keydown.enter="submit"
            />
          </div>

          <!-- Embedding Model -->
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Embedding Model</label>
            <div class="relative">
              <select
                v-model="embeddingModel"
                class="w-full appearance-none rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-500 transition-colors"
              >
                <option v-for="opt in embeddingOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
              <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
            <p class="mt-1 text-[10px] text-gray-400">
              Cannot be changed after uploading documents.
            </p>
          </div>

        </div>

        <div class="mt-6 flex justify-end gap-2">
          <button
            class="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 transition-colors"
            @click="$emit('close')"
          >
            Cancel
          </button>
          <button
            class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-40 transition-colors"
            :disabled="!name.trim()"
            @click="submit"
          >
            Create
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
