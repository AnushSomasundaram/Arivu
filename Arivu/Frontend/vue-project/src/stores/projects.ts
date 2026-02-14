import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import {
  fetchProjects,
  createProjectApi,
  updateProjectApi,
  deleteProjectApi,
  getErrorMessage,
  type Project,
  type ProjectUpdate,
} from '@/lib/api'
import { useToast } from '@/lib/toast'

const STORAGE_KEY = 'arivu-active-project'
const DEFAULT_PROJECT: Project = { id: 'default', name: 'Default', embedding_model: 'local:all-MiniLM-L6-v2' }

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref<Project[]>([DEFAULT_PROJECT])
  const activeProjectId = ref<string>(localStorage.getItem(STORAGE_KEY) ?? DEFAULT_PROJECT.id)
  const loading = ref(false)

  const toast = useToast()

  const activeProject = computed(
    () => projects.value.find((p) => p.id === activeProjectId.value) ?? DEFAULT_PROJECT,
  )

  function persistActiveId() {
    localStorage.setItem(STORAGE_KEY, activeProjectId.value)
  }

  function setActiveProject(id: string) {
    activeProjectId.value = id
    persistActiveId()
  }

  async function load() {
    loading.value = true
    try {
      const remote = await fetchProjects()
      projects.value = remote.length ? remote : [DEFAULT_PROJECT]
      // if stored active id doesn't exist in list, reset to first
      if (!projects.value.some((p) => p.id === activeProjectId.value)) {
        activeProjectId.value = projects.value[0]!.id
        persistActiveId()
      }
    } catch {
      // backend offline — keep local default
      if (!projects.value.length) {
        projects.value = [DEFAULT_PROJECT]
      }
    } finally {
      loading.value = false
    }
  }

  async function create(name: string, embeddingModel: string) {
    try {
      const p = await createProjectApi(name, '', embeddingModel)
      projects.value.push(p)
      setActiveProject(p.id)
      toast.show(`Project "${name}" created`, 'success')
    } catch (e: any) {
      toast.show(getErrorMessage(e) ?? 'Failed to create project', 'error')
    }
  }

  async function update(id: string, data: ProjectUpdate) {
    try {
      const updated = await updateProjectApi(id, data)
      const idx = projects.value.findIndex((p) => p.id === id)
      if (idx !== -1) projects.value[idx] = updated
      toast.show('Project updated', 'success')
    } catch (e: any) {
      toast.show(getErrorMessage(e) ?? 'Update failed', 'error')
    }
  }

  async function remove(id: string) {
    try {
      await deleteProjectApi(id)
      projects.value = projects.value.filter((p) => p.id !== id)
      // if deleted project was active, switch to first available or default
      if (activeProjectId.value === id) {
        const next = projects.value[0] ?? DEFAULT_PROJECT
        if (!projects.value.length) projects.value = [DEFAULT_PROJECT]
        setActiveProject(next.id)
      }
      toast.show('Project deleted', 'success')
    } catch (e: any) {
      toast.show(getErrorMessage(e) ?? 'Delete failed', 'error')
    }
  }

  return {
    projects,
    activeProjectId,
    activeProject,
    loading,
    load,
    create,
    update,
    remove,
    setActiveProject,
  }
})
