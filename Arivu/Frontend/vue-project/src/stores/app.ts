import { ref } from 'vue'
import { defineStore } from 'pinia'
import { fetchHealth } from '@/lib/api'

export const useAppStore = defineStore('app', () => {
  const backendOnline = ref(false)
  const backendVersion = ref<string | undefined>()
  const checking = ref(false)

  let intervalId: ReturnType<typeof setInterval> | null = null

  async function checkHealth() {
    checking.value = true
    try {
      const data = await fetchHealth()
      backendOnline.value = data.ok
      backendVersion.value = data.version
    } catch {
      backendOnline.value = false
      backendVersion.value = undefined
    } finally {
      checking.value = false
    }
  }

  function startPolling(intervalMs = 15_000) {
    checkHealth()
    if (intervalId) clearInterval(intervalId)
    intervalId = setInterval(checkHealth, intervalMs)
  }

  function stopPolling() {
    if (intervalId) {
      clearInterval(intervalId)
      intervalId = null
    }
  }

  return { backendOnline, backendVersion, checking, checkHealth, startPolling, stopPolling }
})
