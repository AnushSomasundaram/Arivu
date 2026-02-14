<script setup lang="ts">
import { useAppStore } from '@/stores/app'

const app = useAppStore()
</script>

<template>
  <header
    class="flex h-14 items-center justify-between border-b border-gray-200 bg-white px-6"
  >
    <h1 class="text-lg font-semibold text-gray-800">Arivu</h1>

    <div class="flex items-center gap-2 text-sm">
      <span
        class="inline-block h-2 w-2 rounded-full"
        :class="app.backendOnline ? 'bg-green-500' : 'bg-red-400'"
      />
      <span :class="app.backendOnline ? 'text-green-700' : 'text-red-500'">
        Backend: {{ app.backendOnline ? 'Connected' : 'Disconnected' }}
      </span>
    </div>
  </header>
</template>
