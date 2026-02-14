<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import SidebarNav from './SidebarNav.vue'
import TopBar from './TopBar.vue'
import ToastHost from './ToastHost.vue'
import { useAppStore } from '@/stores/app'
import { useProjectsStore } from '@/stores/projects'

const collapsed = ref(false)
const app = useAppStore()
const projects = useProjectsStore()

onMounted(() => {
  app.startPolling()
  projects.load()
})
onUnmounted(() => app.stopPolling())

// reload projects when backend comes online
watch(() => app.backendOnline, (online) => {
  if (online) projects.load()
})
</script>

<template>
  <div class="flex h-screen overflow-hidden">
    <SidebarNav :collapsed="collapsed" @toggle="collapsed = !collapsed" />

    <div class="flex flex-1 flex-col overflow-hidden">
      <TopBar />

      <!-- Offline banner -->
      <div
        v-if="!app.backendOnline"
        class="bg-amber-50 px-4 py-2 text-center text-sm text-amber-800 border-b border-amber-200"
      >
        Backend is offline. Some features may be unavailable.
      </div>

      <main class="flex-1 overflow-y-auto">
        <slot />
      </main>
    </div>

    <ToastHost />
  </div>
</template>
