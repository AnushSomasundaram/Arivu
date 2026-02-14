<script setup lang="ts">
import { ref } from 'vue'
import { useStudyStore } from '@/stores/study'
import { useProjectsStore } from '@/stores/projects'
import type { StudyMode } from '@/lib/api'

const study = useStudyStore()
const projects = useProjectsStore()

const mode = ref<StudyMode>('quiz')
const count = ref(10)
const topic = ref('')

function generate() {
  if (!projects.activeProjectId) return
  study.generate(projects.activeProjectId, {
    mode: mode.value,
    count: count.value,
    topic: topic.value || undefined
  })
}
</script>

<template>
  <div class="flex h-full">
    <!-- Sidebar Config -->
    <div class="w-80 border-r border-gray-200 bg-gray-50 p-6 flex flex-col gap-6 overflow-y-auto shrink-0">
      <div>
        <h2 class="text-lg font-semibold text-gray-800">Study Mode</h2>
        <p class="text-sm text-gray-500 mt-1">Generate learning materials from your documents.</p>
      </div>

      <!-- Form -->
      <div class="flex flex-col gap-4">
        <!-- Mode -->
        <div class="flex flex-col gap-1.5">
          <label class="text-sm font-medium text-gray-700">Mode</label>
          <select v-model="mode" class="rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500">
            <option value="quiz">Quiz</option>
            <option value="summary">Summary</option>
            <option value="flashcards">Flashcards</option>
          </select>
        </div>

        <!-- Count -->
        <div class="flex flex-col gap-1.5">
          <label class="text-sm font-medium text-gray-700">Item Count</label>
          <input type="number" v-model="count" min="1" max="50" class="rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500" />
        </div>

        <!-- Topic -->
        <div class="flex flex-col gap-1.5">
          <label class="text-sm font-medium text-gray-700">Focus Topic (Optional)</label>
          <input type="text" v-model="topic" placeholder="e.g. key concepts" class="rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500" />
        </div>

        <button 
          @click="generate" 
          :disabled="study.loading || !projects.activeProjectId"
          class="mt-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
        >
          {{ study.loading ? 'Generating...' : 'Generate Guide' }}
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 overflow-y-auto bg-white p-8">
       <div v-if="study.loading" class="flex flex-col items-center justify-center h-full text-gray-400">
          <div class="animate-spin h-8 w-8 border-4 border-gray-200 border-t-indigo-600 rounded-full mb-4"></div>
          <p>Analyzing documents...</p>
       </div>

       <div v-else-if="study.result" class="max-w-3xl mx-auto">
          <div class="prose prose-indigo max-w-none">
            <h1 class="capitalize mb-6 text-2xl font-bold text-gray-900">{{ study.result.mode }}</h1>
            <div class="whitespace-pre-wrap text-gray-800 leading-relaxed text-base">{{ study.result.content }}</div>
          </div>
          
          <!-- Sources -->
          <div v-if="study.result.sources.length" class="mt-12 pt-8 border-t border-gray-100">
            <h3 class="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-4">Sources Used</h3>
            <div class="grid grid-cols-1 gap-2">
               <div v-for="(src, i) in study.result.sources" :key="i" class="text-xs text-gray-500 bg-gray-50 p-2 rounded border border-gray-100 flex justify-between">
                  <span class="font-medium text-gray-700 truncate mr-2">{{ src.filename }}</span>
                  <span v-if="src.page" class="shrink-0">p. {{ src.page }}</span>
               </div>
            </div>
          </div>
       </div>

       <div v-else class="flex flex-col items-center justify-center h-full text-gray-400 text-center">
          <span class="text-4xl mb-4 block">🎓</span>
          <p class="text-lg font-medium text-gray-600">No study guide generated yet</p>
          <p class="text-sm mt-2">Select options on the left to start studying your documents.</p>
       </div>
    </div>
  </div>
</template>
