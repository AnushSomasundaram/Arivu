
<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import { useFilesStore } from '@/stores/files'
import CreateProjectModal from './CreateProjectModal.vue'
import ConfirmDialog from './ConfirmDialog.vue'
import logoUrl from '@/assets/arivu-logo.png'

defineProps<{ collapsed: boolean }>()
defineEmits<{ (e: 'toggle'): void }>()

const projects = useProjectsStore()
const files = useFilesStore()
const showCreate = ref(false)

// Delete confirmation state
const showDeleteConfirm = ref(false)
const projectToDelete = ref<{id: string, name: string} | null>(null)

function switchProject(id: string) {
  projects.setActiveProject(id)
  files.reset()
}

function handleCreate(name: string, embeddingModel: string) {
  projects.create(name, embeddingModel)
  showCreate.value = false
}

function requestDelete(id: string, name: string) {
  projectToDelete.value = { id, name }
  showDeleteConfirm.value = true
}

function confirmDelete() {
  if (projectToDelete.value) {
    projects.remove(projectToDelete.value.id)
    projectToDelete.value = null
  }
  showDeleteConfirm.value = false
}

const navLinks = [
  { to: '/chat', label: 'Chat', icon: '💬' },
  { to: '/documents', label: 'Documents', icon: '📄' },
] as const
</script>

<template>
  <aside
    class="flex flex-col bg-gray-900 text-gray-100 transition-all duration-200 border-r border-gray-800"
    :class="collapsed ? 'w-16' : 'w-64'"
  >
    <!-- Brand -->
    <div class="flex h-14 items-center gap-2 px-4 shrink-0">
      <img :src="logoUrl" alt="Arivu" class="h-8 w-8 rounded object-contain" />
      <span v-if="!collapsed" class="text-lg font-bold tracking-wide">Arivu</span>
    </div>

    <!-- New Project Button -->
    <div class="px-2 mt-2 mb-1 shrink-0">
      <button
        @click="showCreate = true"
        class="flex w-full items-center gap-2 rounded-lg border border-gray-700 p-2 text-sm text-gray-200 hover:bg-gray-800 transition-colors"
        :class="collapsed ? 'justify-center' : ''"
      >
        <span class="text-xl leading-none">+</span>
        <span v-if="!collapsed">New project</span>
      </button>
    </div>

    <!-- Main Navigation (Chat/Docs) -->
    <nav class="flex flex-col gap-1 px-2 mt-2 shrink-0">
      <RouterLink
        v-for="link in navLinks"
        :key="link.to"
        :to="link.to"
        class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-gray-800"
        active-class="bg-gray-800 text-white"
        :title="collapsed ? link.label : ''"
      >
        <span class="text-base">{{ link.icon }}</span>
        <span v-if="!collapsed">{{ link.label }}</span>
      </RouterLink>
    </nav>

    <!-- Projects List -->
    <div class="flex-1 overflow-y-auto mt-4 px-2 min-h-0">
      <div v-if="!collapsed" class="px-2 pb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
        Your Projects
      </div>
      
      <div class="flex flex-col gap-0.5">
        <div
          v-for="p in projects.projects"
          :key="p.id"
          class="group relative flex items-center justify-between rounded-lg px-3 py-2 text-sm transition-colors cursor-pointer"
          :class="[
            p.id === projects.activeProjectId 
              ? 'bg-gray-800 text-white' 
              : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
          ]"
          :title="collapsed ? p.name : ''"
          @click="switchProject(p.id)"
        >
          <div class="flex items-center gap-3 overflow-hidden">
            <span v-if="collapsed" class="text-xs font-bold shrink-0">{{ p.name.charAt(0).toUpperCase() }}</span>
            <span v-else class="truncate">{{ p.name }}</span>
          </div>

          <!-- Delete Button -->
          <button
            v-if="!collapsed"
            class="hidden group-hover:block rounded p-1 text-gray-500 hover:bg-gray-700 hover:text-red-400"
            title="Delete project"
            @click.stop="requestDelete(p.id, p.name)"
          >
            <!-- Trash Icon -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
              <path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Bottom Section (Settings & Collapse) -->
    <div class="mt-auto border-t border-gray-800 p-2 shrink-0 flex flex-col gap-1">
      <RouterLink
        to="/settings"
        class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-400 transition-colors hover:bg-gray-800 hover:text-gray-100"
        active-class="bg-gray-800 !text-white"
        :title="collapsed ? 'Settings' : ''"
      >
        <span class="text-base">⚙️</span>
        <span v-if="!collapsed">Settings</span>
      </RouterLink>

      <button
        class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-gray-500 hover:bg-gray-800 hover:text-gray-300 transition-colors"
        @click="$emit('toggle')"
        :title="collapsed ? 'Expand' : 'Collapse'"
      >
        <span>{{ collapsed ? '→' : '←' }}</span>
        <span v-if="!collapsed">Collapse sidebar</span>
      </button>
    </div>

    <!-- Modals -->
    <CreateProjectModal
      v-if="showCreate"
      @create="handleCreate"
      @close="showCreate = false"
    />
    
    <ConfirmDialog
      v-if="showDeleteConfirm"
      title="Delete Project?"
      :message="`Are you sure you want to delete '${projectToDelete?.name}'? All documents and chats in this project will be permanently removed.`"
      confirm-text="Delete"
      type="danger"
      @confirm="confirmDelete"
      @cancel="showDeleteConfirm = false"
    />
  </aside>
</template>

