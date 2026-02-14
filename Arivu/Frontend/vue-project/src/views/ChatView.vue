<script setup lang="ts">
import { ref, nextTick, watch, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useAppStore } from '@/stores/app'
import { useProjectsStore } from '@/stores/projects'
import ChatMessage from '@/components/ChatMessage.vue'
import logoUrl from '@/assets/arivu-logo.png'

const chat = useChatStore()
const app = useAppStore()
const projects = useProjectsStore()

const input = ref('')
const messagesEl = ref<HTMLElement | null>(null)

// History Loading
onMounted(() => {
  if (projects.activeProjectId) {
    chat.loadHistory(projects.activeProjectId)
  }
})

watch(
  () => projects.activeProjectId,
  (newId) => {
    if (newId) {
      chat.loadHistory(newId)
    }
  },
)

function scrollToBottom() {
  nextTick(() => {
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  })
}

watch(() => chat.messages.length, scrollToBottom)

function handleSend() {
  const q = input.value.trim()
  if (!q || chat.querying) return
  // Optimistic UI updates happen in store.send
  input.value = ''
  chat.send(q)
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
</script>

<template>
  <div class="flex h-full flex-col">
    <!-- Messages area -->
    <div ref="messagesEl" class="flex-1 overflow-y-auto px-4 py-6">
      <!-- Empty state -->
      <div
        v-if="chat.messages.length === 0"
        class="flex h-full flex-col items-center justify-center text-center"
      >
        <img :src="logoUrl" alt="Arivu" class="mb-4 h-36 w-36 rounded-2xl object-contain" />
        <h2 class="text-xl font-semibold text-gray-700">Ask Arivu anything</h2>
        <p class="mt-1 max-w-sm text-sm text-gray-400">
          Your questions will be answered using the documents you've uploaded.
          Head to Documents to add files first.
        </p>
      </div>

      <!-- Message list -->
      <div v-else class="mx-auto flex max-w-3xl flex-col gap-4">
        <ChatMessage v-for="msg in chat.messages" :key="msg.id" :msg="msg" />

        <!-- Typing indicator -->
        <div v-if="chat.querying" class="flex justify-start">
          <div class="flex items-center gap-2 rounded-2xl border border-gray-200 bg-white px-4 py-3 shadow-sm">
            <span class="inline-block h-2 w-2 animate-pulse rounded-full bg-gray-400" />
            <span class="inline-block h-2 w-2 animate-pulse rounded-full bg-gray-400 [animation-delay:150ms]" />
            <span class="inline-block h-2 w-2 animate-pulse rounded-full bg-gray-400 [animation-delay:300ms]" />
          </div>
        </div>
      </div>
    </div>

    <!-- Input area -->
    <div class="border-t border-gray-200 bg-white px-4 py-3">
      <div class="mx-auto flex max-w-3xl items-end gap-3">
        <textarea
          v-model="input"
          rows="1"
          class="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-3 text-sm outline-none transition-colors focus:border-gray-500 focus:ring-1 focus:ring-gray-500 disabled:bg-gray-100"
          placeholder="Ask a question…"
          :disabled="!app.backendOnline || chat.querying"
          @keydown="onKeydown"
        />
        <button
          class="rounded-xl bg-gray-900 px-5 py-3 text-sm font-medium text-white transition-colors hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-40"
          :disabled="!input.trim() || !app.backendOnline || chat.querying"
          @click="handleSend"
        >
          Send
        </button>
      </div>
      <p v-if="!app.backendOnline" class="mt-1 text-center text-xs text-amber-600">
        Backend is offline — sending is disabled.
      </p>
    </div>
  </div>
</template>
