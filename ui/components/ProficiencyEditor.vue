<template>
  <Card>
    <template #title>Proficiencies</template>
    <template #content>
      <div class="space-y-4">
        <div v-for="(proficiency, index) in proficiencies" :key="index" class="flex gap-4 items-start">
          <div class="flex-1">
            <InputText
              v-model="proficiency.category"
              placeholder="Category"
              class="w-full"
            />
          </div>
          <div class="flex-1">
            <Chips
              v-model="proficiency.items"
              placeholder="Type and press Enter to add items"
              class="w-full"
              :allowDuplicate="false"
              :addOnBlur="true"
              :addOnTab="true"
            />
          </div>
          <button
            @click="removeProficiency(index)"
            class="p-2 text-red-600 hover:text-red-800"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
        <button
          @click="addProficiency"
          class="mt-2 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-emerald-700 bg-emerald-100 hover:bg-emerald-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500"
        >
          Add Proficiency
        </button>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Chips from 'primevue/chips'

interface Proficiency {
  category: string
  items: string[]
}

const props = defineProps<{
  modelValue: Proficiency[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: Proficiency[]): void
}>()

const proficiencies = ref<Proficiency[]>(props.modelValue)

watch(proficiencies, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })

watch(() => props.modelValue, (newValue) => {
  proficiencies.value = newValue
}, { deep: true })

const addProficiency = () => {
  proficiencies.value.push({
    category: '',
    items: []
  })
}

const removeProficiency = (index: number) => {
  proficiencies.value.splice(index, 1)
}
</script> 