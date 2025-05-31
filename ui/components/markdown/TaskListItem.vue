<template>
  <div
    class="task-list-item flex items-center gap-2"
    :class="[{ checked: modelValueProxy }, unordered ? 'ml-[-1.25em]' : '']"
  >
    <Checkbox v-model="modelValueProxy" :inputId="inputId" :binary="true" disabled />
    <label :for="inputId" class="task-label select-text prose dark:prose-invert" v-html="label"></label>
  </div>
</template>

<script setup lang="ts">
import { computed, defineProps, defineEmits } from 'vue'
import Checkbox from 'primevue/checkbox'

const props = defineProps({
  modelValue: { type: Boolean, required: true },
  label: { type: String, default: '' },
  inputId: { type: String, default: () => `task-checkbox-${Math.random().toString(36).slice(2, 10)}` },
  unordered: { type: Boolean, default: false }
})
const emit = defineEmits(['update:modelValue'])

const modelValueProxy = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val)
})
</script>

<style scoped>
.task-list-item {
  /* Add spacing and alignment */
  min-height: 2rem;
}

.task-label {
  user-select: text;
  word-break: break-word;
  transition: color 0.2s;
}

/* Reset prose margins for inline content */
:deep(.prose) {
  margin: 0;
  padding: 0;
}

:deep(.prose p) {
  margin: 0;
}

:deep(.prose a) {
  text-decoration: underline;
}

:deep(.p-checkbox .p-checkbox-input:checked ~ .p-checkbox-box),
:deep(.p-checkbox .p-checkbox-input:checked:disabled ~ .p-checkbox-box),
:deep(.p-checkbox .p-checkbox-input:checked[disabled] ~ .p-checkbox-box) {
  border-color: #059669 !important;
  background: #059669 !important;
}
:deep(.p-checkbox .p-checkbox-input:checked ~ .p-checkbox-box .p-checkbox-icon),
:deep(.p-checkbox .p-checkbox-input:checked:disabled ~ .p-checkbox-box .p-checkbox-icon),
:deep(.p-checkbox .p-checkbox-input:checked[disabled] ~ .p-checkbox-box .p-checkbox-icon) {
  color: #fff !important;
}
</style> 