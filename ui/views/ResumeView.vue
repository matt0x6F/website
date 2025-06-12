<template>
  <div class="relative">
    <!-- Download Button -->
    <button
      @click="downloadPDF"
      class="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
      aria-label="Download Resume as PDF"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        fill="currentColor"
        class="bi bi-download"
        viewBox="0 0 16 16"
      >
        <path
          d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5"
        />
        <path
          d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708z"
        />
      </svg>
    </button>

    <div id="content" v-if="resume">
      <h1 class="text-4xl font-bold mb-4">Resume</h1>
      <p class="mt-2 flex items-center gap-4">
        <span class="flex items-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            fill="currentColor"
            class="bi bi-github mr-1"
            viewBox="0 0 16 16"
          >
            <path
              d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8"
            />
          </svg>
          <a
            :href="resume.githubUrl"
            target="_blank"
            class="hover:underline"
            >github.com/matt0x6f</a
          >
        </span>
        <span class="flex items-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            fill="currentColor"
            class="bi bi-globe mr-1"
            viewBox="0 0 16 16"
          >
            <path d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8m7.5-6.923c-.67.204-1.335.82-1.887 1.855A7.97 7.97 0 0 0 5.145 4H7.5zM4.09 4a9.267 9.267 0 0 1 .64-1.539 6.7 6.7 0 0 1 .597-.933A7.025 7.025 0 0 0 2.255 4zm-.582 3.5c.03-.877.138-1.718.312-2.5H1.674a6.958 6.958 0 0 0-.656 2.5zM4.847 5a12.5 12.5 0 0 0-.338 2.5H7.5V5zM8.5 5v2.5h2.99a12.495 12.495 0 0 0-.337-2.5zM4.51 8.5a12.5 12.5 0 0 0 .337 2.5H7.5V8.5zm3.99 0V11h2.653c.187-.765.306-1.608.338-2.5zM5.145 12c.138.386.295.744.468 1.068.552 1.035 1.218 1.65 1.887 1.855V12zm.182 2.472a6.696 6.696 0 0 1-.597-.933A9.268 9.268 0 0 1 4.09 12H2.255a7.024 7.024 0 0 0 3.072 2.472M3.82 11a13.652 13.652 0 0 1-.312-2.5h-2.49c.062.89.291 1.733.656 2.5zm6.853 3.472A7.024 7.024 0 0 0 13.745 12H11.91a9.27 9.27 0 0 1-.64 1.539 6.688 6.688 0 0 1-.597.933M8.5 12v2.923c.67-.204 1.335-.82 1.887-1.855.173-.324.33-.682.468-1.068zm3.68-1h2.146c.365-.767.594-1.61.656-2.5h-2.49a13.65 13.65 0 0 1-.312 2.5zm2.802-3.5a6.959 6.959 0 0 0-.656-2.5H12.18c.174.782.282 1.623.312 2.5zM11.27 2.461c.247.464.462.98.64 1.539h1.835a7.024 7.024 0 0 0-3.072-2.472c.218.284.418.598.597.933zM10.855 4a7.966 7.966 0 0 0-.468-1.068C9.835 1.897 9.17 1.282 8.5 1.077V4z"/>
          </svg>
          <a
            :href="resume.websiteUrl"
            target="_blank"
            class="hover:underline"
            >ooo-yay.com</a
          >
        </span>
      </p>
      <p class="mt-4">
        {{ resume.bio }}
      </p>

      <section class="mt-8">
        <h2 class="text-xl font-semibold mb-4">Proficiencies</h2>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4"> 
          <Card v-for="proficiency in resume.proficiencies" :key="proficiency.category">
            <template #title>
              {{ proficiency.category }}
            </template>
            <template #content>
              <ul class="grid grid-cols-2 gap-x-4 list-disc list-inside">
                <li v-for="item in proficiency.items" :key="item">{{ item }}</li>
              </ul>
            </template>
          </Card>
        </div> 
      </section>

      <section class="mt-8">
        <h2 class="text-xl font-semibold mb-4">Experience</h2>
        
        <Card v-for="experience in resume.experiences" :key="experience.title" class="mb-4">
          <template #title>
            {{ experience.title }}
          </template>
          <template #subtitle>
            {{ experience.company }} | {{ formatDate(experience.startDate) }} - {{ experience.isCurrent ? 'Present' : formatDate(experience.endDate) }}
          </template>
          <template #content>
            <div class="mt-4">
              <h4 class="text-sm font-medium text-gray-900">Achievements</h4>
              <div class="mt-2 prose prose-sm max-w-none">
                <Markdown :content="experience.achievements" />
              </div>
            </div>
          </template>
        </Card>

        <Card>
          <template #content>
            <p class="text-xs text-center">References available upon request</p>
          </template>
        </Card>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import Card from 'primevue/card';
import { onMounted, ref } from 'vue'
import type { ResumeSchema } from '~/lib/api'
import Markdown from '~/components/MarkdownPreview.vue'
import { ResumeApi } from '~/lib/api'

const resume = ref<ResumeSchema | null>(null)
const api = useApiClient(ResumeApi)

const downloadPDF = () => {
  window.print();
};

const formatDate = (date: Date | null | undefined) => {
  if (!date) return ''
  return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
}

onMounted(async () => {
  document.title = 'Resume – ooo-yay.com'
  try {
    resume.value = await api.apiGetResume()
  } catch (error) {
    console.error('Failed to fetch resume:', error)
  }
})
</script>

<style scoped>
:deep(.p-card) {
  height: 100%;
  overflow: hidden;
}

:deep(.p-card-body) {
  background: #fff;
  height: 100%;
}
@media (prefers-color-scheme: dark) {
  :deep(.p-card-body) {
    background: #1f2937;
  }
}

:deep(.p-card-content) {
  padding-top: 0;
}

:deep(.p-card-content ul) {
  margin: 0;
  padding: 0;
}

:deep(.p-card-content li) {
  margin-bottom: 0.5rem;
}

/* Add styles to hide the button when printing */
@media print {
  .absolute.top-4.right-4 {
    display: none;
  }
}
</style>
