<template>
  <div class="mermaid-block">
    <div v-if="error" class="mermaid-error">{{ error }}</div>
    <div v-else ref="container" class="mermaid-graph"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import mermaid from 'mermaid'

const props = defineProps<{ code: string }>()
const container = ref<HTMLElement | null>(null)
const error = ref<string | null>(null)

function renderMermaid() {
  error.value = null
  if (!container.value) return
  // Clear previous content
  container.value.innerHTML = ''
  try {
    mermaid.parse(props.code) // Throws if invalid
    mermaid.render('mermaid-svg-' + Math.random().toString(36).slice(2, 10), props.code).then(({ svg }) => {
      if (container.value) container.value.innerHTML = svg
    }).catch(e => {
      error.value = 'Mermaid render error: ' + e.message
    })
  } catch (e: any) {
    error.value = 'Mermaid syntax error: ' + e.message
  }
}

watch(() => props.code, () => nextTick(renderMermaid))
onMounted(() => { nextTick(renderMermaid) })
</script>

<style scoped>
.mermaid-block {
  margin: 1em 0;
  overflow-x: auto;
  background: var(--p-surface-100, #f8fafc);
  border-radius: 0.5em;
  padding: 1em;
}
.mermaid-graph svg {
  width: 100%;
  height: auto;
  display: block;
}
.mermaid-error {
  color: #dc2626;
  font-size: 0.95em;
  font-family: monospace;
  background: #fee2e2;
  border-radius: 0.25em;
  padding: 0.5em;
}
</style> 