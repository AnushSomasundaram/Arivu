
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { generateStudyGuide, type StudyRequest, type StudyResponse, getErrorMessage } from '@/lib/api'
import { useToast } from '@/lib/toast'

export const useStudyStore = defineStore('study', () => {
    const loading = ref(false)
    const result = ref<StudyResponse | null>(null)
    const toast = useToast()

    async function generate(projectId: string, req: StudyRequest) {
        loading.value = true
        result.value = null
        try {
            const resp = await generateStudyGuide(projectId, req)
            result.value = resp
            toast.show('Study guide generated!', 'success')
        } catch (e: any) {
            toast.show(getErrorMessage(e) ?? 'Failed to generate', 'error')
        } finally {
            loading.value = false
        }
    }

    return { loading, result, generate }
})
