import { ref } from 'vue'
import { defineStore } from 'pinia'
import {
  fetchFiles,
  uploadFiles as apiUpload,
  deleteFile as apiDelete,
  reindexFile as apiReindex,
  getErrorMessage,
  type FileRecord,
} from '@/lib/api'
import { useToast } from '@/lib/toast'
import { useProjectsStore } from './projects'
import { useSettingsStore } from './settings'

export const useFilesStore = defineStore('files', () => {
  const files = ref<FileRecord[]>([])
  const loading = ref(false)
  const uploading = ref(false)
  const error = ref<string | null>(null)

  const toast = useToast()

  function pid(): string {
    return useProjectsStore().activeProjectId
  }

  async function load(silent = false) {
    if (!silent) loading.value = true
    error.value = null
    try {
      const pidVal = pid()
      if (!pidVal) return
      files.value = await fetchFiles(pidVal)

      // If any files are processing, start polling
      const needsPolling = files.value.some(f =>
        ['queued', 'parsing', 'chunking', 'embedding', 'indexing'].includes(f.status)
      )
      if (needsPolling) {
        startPolling()
      } else {
        stopPolling()
      }
    } catch (e: any) {
      if (!silent) error.value = getErrorMessage(e) ?? 'Failed to load files'
    } finally {
      if (!silent) loading.value = false
    }
  }

  let pollInterval: any = null
  function startPolling() {
    if (pollInterval) return
    pollInterval = setInterval(() => {
      load(true)
    }, 3000)
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  async function upload(rawFiles: File[]) {
    uploading.value = true
    const settingsStore = useSettingsStore()
    const options = {
      embedding_api_key: settingsStore.embeddingApiKey,
      embedding_base_url: settingsStore.embeddingBaseUrl,
    }

    try {
      const result = await apiUpload(pid(), rawFiles, options)
      toast.show(`Uploaded ${result.uploaded.length} file(s)`, 'success')
      await load()
    } catch (e: any) {
      toast.show(getErrorMessage(e) ?? 'Upload failed', 'error')
    } finally {
      uploading.value = false
    }
  }

  async function remove(id: string) {
    try {
      await apiDelete(pid(), id)
      files.value = files.value.filter((f) => f.id !== id)
      toast.show('File deleted', 'success')
    } catch (e: any) {
      toast.show(getErrorMessage(e) ?? 'Delete failed', 'error')
    }
  }

  async function reindex(id: string) {
    try {
      await apiReindex(pid(), id)
      toast.show('Reindex started', 'success')
      await load()
    } catch (e: any) {
      toast.show(getErrorMessage(e) ?? 'Reindex failed', 'error')
    }
  }

  function reset() {
    files.value = []
    error.value = null
    stopPolling()
  }

  return { files, loading, uploading, error, load, upload, remove, reindex, reset }
})
