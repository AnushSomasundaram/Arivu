<script setup lang="ts">
import { useToast } from '@/lib/toast'

const { toasts, dismiss } = useToast()

const bg: Record<string, string> = {
  success: 'bg-green-600',
  error: 'bg-red-600',
  info: 'bg-blue-600',
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      <TransitionGroup name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          :class="[bg[t.type], 'flex items-center gap-3 rounded-lg px-4 py-3 text-sm text-white shadow-lg']"
        >
          <span class="flex-1">{{ t.message }}</span>
          <button
            class="text-white/70 hover:text-white"
            aria-label="Dismiss"
            @click="dismiss(t.id)"
          >
            ✕
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(40px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(40px);
}
</style>
