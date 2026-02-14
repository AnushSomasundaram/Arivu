<script setup lang="ts">
import { ref } from 'vue'
import { useProjectsStore } from '@/stores/projects'

const emit = defineEmits<{ (e: 'close'): void }>()
const projects = useProjectsStore()

const editingId = ref<string | null>(null)
const editName = ref('')

function startRename(id: string, currentName: string) {
  editingId.value = id
  editName.value = currentName
}

function commitRename(id: string) {
  const trimmed = editName.value.trim()
  const project = projects.projects.find((p) => p.id === id)
  if (trimmed && project && trimmed !== project.name) {
    projects.update(id, { name: trimmed })
  }
  editingId.value = null
}

function confirmDelete(id: string, name: string) {
  if (confirm(`Delete project "${name}"? This cannot be undone.`)) {
    projects.remove(id)
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      @click.self="$emit('close')"
    >
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h3 class="text-lg font-semibold text-gray-800">Manage Projects</h3>
        <p class="mt-1 text-sm text-gray-500">Rename or delete your projects.</p>

        <ul class="mt-4 flex flex-col divide-y divide-gray-100">
          <li
            v-for="p in projects.projects"
            :key="p.id"
            class="flex items-center gap-2 py-2"
          >
            <!-- Editing mode -->
            <template v-if="editingId === p.id">
              <input
                v-model="editName"
                type="text"
                class="flex-1 rounded-lg border border-gray-300 px-2 py-1 text-sm outline-none focus:border-gray-500"
                autofocus
                @keydown.enter="commitRename(p.id)"
                @keydown.escape="editingId = null"
              />
              <button
                class="text-xs text-green-600 hover:text-green-800"
                @click="commitRename(p.id)"
              >
                Save
              </button>
              <button
                class="text-xs text-gray-400 hover:text-gray-600"
                @click="editingId = null"
              >
                Cancel
              </button>
            </template>

            <!-- Display mode -->
            <template v-else>
              <span class="flex-1 text-sm text-gray-700">
                {{ p.name }}
                <span
                  v-if="p.id === projects.activeProjectId"
                  class="ml-1.5 rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-medium text-blue-700"
                >
                  Active
                </span>
              </span>
              <button
                class="text-xs text-blue-600 hover:text-blue-800"
                @click="startRename(p.id, p.name)"
              >
                Rename
              </button>
              <button
                v-if="projects.projects.length > 1"
                class="text-xs text-red-500 hover:text-red-700"
                @click="confirmDelete(p.id, p.name)"
              >
                Delete
              </button>
            </template>
          </li>
        </ul>

        <div class="mt-4 flex justify-end">
          <button
            class="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 transition-colors"
            @click="$emit('close')"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
