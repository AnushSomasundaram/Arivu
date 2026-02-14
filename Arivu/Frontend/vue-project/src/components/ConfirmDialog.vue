<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

const props = withDefaults(
  defineProps<{
    title?: string
    message: string
    confirmText?: string
    cancelText?: string
    type?: 'danger' | 'info'
  }>(),
  {
    title: 'Confirm',
    confirmText: 'Confirm',
    cancelText: 'Cancel',
    type: 'info',
  },
)

const emit = defineEmits<{
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('cancel')
}

// Focus trap-ish
onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm transition-opacity"
      @click.self="$emit('cancel')"
    >
      <div
        class="w-full max-w-sm scale-100 transform rounded-xl bg-white p-6 shadow-2xl transition-all"
        role="dialog"
        aria-modal="true"
      >
        <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
        
        <p class="mt-2 text-sm text-gray-500 leading-relaxed">
          {{ message }}
        </p>

        <div class="mt-6 flex justify-end gap-3">
          <button
            class="rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-300 transition-colors"
            @click="$emit('cancel')"
          >
            {{ cancelText }}
          </button>
          
          <button
            class="rounded-lg px-4 py-2 text-sm font-bold text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors"
            :class="[
              type === 'danger' 
                ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500' 
                : 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
            ]"
            @click="$emit('confirm')"
          >
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
