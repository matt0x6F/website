<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">Resume Editor</h1>

    <div v-if="resume" class="space-y-8">
      <!-- Basic Info -->
      <Card>
        <template #title>Basic Information</template>
        <template #content>
          <div class="space-y-4">
            <div>
              <label for="name" class="block text-sm font-medium text-gray-700">Name</label>
              <InputText
                id="name"
                v-model="resume.name"
                class="mt-1 block w-full"
              />
            </div>
            <div>
              <label for="bio" class="block text-sm font-medium text-gray-700">Bio</label>
              <Textarea
                id="bio"
                v-model="resume.bio"
                rows="4"
                class="mt-1 block w-full"
              />
            </div>
            <div>
              <label for="githubUrl" class="block text-sm font-medium text-gray-700">GitHub URL</label>
              <InputText
                id="githubUrl"
                v-model="resume.githubUrl"
                class="mt-1 block w-full"
              />
            </div>
            <div>
              <label for="websiteUrl" class="block text-sm font-medium text-gray-700">Website URL</label>
              <InputText
                id="websiteUrl"
                v-model="resume.websiteUrl"
                class="mt-1 block w-full"
              />
            </div>
          </div>
        </template>
      </Card>

      <!-- Proficiencies -->
      <ProficiencyEditor v-model="resume.proficiencies" />

      <!-- Experience -->
      <Card>
        <template #title>Experience</template>
        <template #content>
          <div class="space-y-6">
            <div v-for="(experience, index) in resume.experiences" :key="index" class="border rounded-lg p-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div class="form-group">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Title</label>
                  <InputText
                    v-model="experience.title"
                    class="w-full"
                  />
                </div>
                <div class="form-group">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Company</label>
                  <InputText
                    v-model="experience.company"
                    class="w-full"
                  />
                </div>
                <div class="form-group">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
                  <Calendar
                    v-model="experience.startDate"
                    dateFormat="yy-mm-dd"
                    class="w-48"
                    :showIcon="true"
                  />
                </div>
                <div class="form-group" v-if="!experience.isCurrent">
                  <label class="block text-sm font-medium text-gray-700 mb-2">End Date</label>
                  <Calendar
                    v-model="experience.endDate"
                    dateFormat="yy-mm-dd"
                    class="w-48"
                    :showIcon="true"
                  />
                </div>
                <div class="form-group">
                  <label class="flex items-center">
                    <input
                      v-model="experience.isCurrent"
                      type="checkbox"
                      class="rounded border-gray-300 text-emerald-600 shadow-sm focus:border-emerald-500 focus:ring-emerald-500"
                    />
                    <span class="ml-2 text-sm text-gray-700">Current Position</span>
                  </label>
                </div>
              </div>
              <div class="form-group">
                <label class="block text-sm font-medium text-gray-700 mb-2">Achievements (Markdown)</label>
                <Textarea
                  v-model="experience.achievements"
                  rows="6"
                  class="w-full"
                  autoResize
                />
              </div>
              <button
                @click="removeExperience(index)"
                class="mt-2 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                Remove Experience
              </button>
            </div>
            <button
              @click="addExperience"
              class="mt-2 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-emerald-700 bg-emerald-100 hover:bg-emerald-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500"
            >
              Add Experience
            </button>
          </div>
        </template>
      </Card>

      <!-- Save Button -->
      <div class="flex justify-end">
        <button
          @click="saveResume"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500"
        >
          Save Resume
        </button>
      </div>
    </div>

    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { ResumeSchema, ProficiencySchema, ExperienceSchema } from '~/lib/api'
import { ResumeApi } from '~/lib/api'
import { useApiClient } from '~/composables/useApiClient'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Calendar from 'primevue/calendar'
import MultiSelect from 'primevue/multiselect'
import Chips from 'primevue/chips'
import ProficiencyEditor from '~/components/ProficiencyEditor.vue'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

interface ProficiencyForm {
  category: string
  items: string[]
}

const api = useApiClient(ResumeApi)
const resume = ref<(ResumeSchema & { proficiencies: ProficiencyForm[] }) | null>(null)
const toast = useToast()

const formatDateForInput = (date: Date | null | undefined) => {
  if (!date) return null
  return new Date(date)
}

const parseDate = (date: Date | null | undefined) => {
  if (!date) return null
  return date
}

const addExperience = () => {
  if (!resume.value) return
  resume.value.experiences.push({
    title: '',
    company: '',
    startDate: new Date(),
    endDate: null,
    isCurrent: false,
    achievements: ''
  })
}

const removeExperience = (index: number) => {
  if (!resume.value) return
  resume.value.experiences.splice(index, 1)
}

const saveResume = async () => {
  if (!resume.value) return
  try {
    // Ensure dates are properly formatted before saving
    const resumeToSave: ResumeSchema = {
      ...resume.value,
      experiences: resume.value.experiences.map(exp => ({
        ...exp,
        startDate: parseDate(exp.startDate) || new Date(),
        endDate: exp.isCurrent ? null : parseDate(exp.endDate)
      })),
      proficiencies: resume.value.proficiencies.map(prof => ({
        category: prof.category,
        items: prof.items
      }))
    }
    await api.apiUpdateResume({ resumeSchema: resumeToSave })
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Resume saved successfully',
      life: 3000
    })
  } catch (error) {
    console.error('Failed to save resume:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save resume',
      life: 3000
    })
  }
}

onMounted(async () => {
  try {
    const data = await api.apiGetResume()
    // Format dates for input fields
    resume.value = {
      ...data,
      experiences: data.experiences.map(exp => ({
        ...exp,
        startDate: formatDateForInput(exp.startDate) as unknown as Date,
        endDate: formatDateForInput(exp.endDate) as unknown as Date
      })),
      proficiencies: data.proficiencies.map(prof => ({
        category: prof.category,
        items: prof.items
      }))
    }
  } catch (error) {
    console.error('Failed to fetch resume:', error)
  }
})
</script>
