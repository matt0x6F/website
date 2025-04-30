<template>
  <div class="preview-content prose dark:prose-invert">
    <template v-for="(block, i) in blocks" :key="i">
      <CodeBlock v-if="block.type === 'code'" :lang="block.lang" :code="block.content" />
      <MarkdownTable v-else-if="block.type === 'table'" :columns="block.columns" :rows="block.rows" />
      <TaskListItem v-else-if="block.type === 'task'" :modelValue="block.modelValue" :label="block.label" />
      <OrderedList v-else-if="block.type === 'ordered_list'" :items="block.items" :start="block.start" />
      <div v-else v-html="block.html"></div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, defineExpose } from 'vue'
import hljs from 'highlight.js/lib/core'
import markdown from 'highlight.js/lib/languages/markdown'
import javascript from 'highlight.js/lib/languages/javascript'
import typescript from 'highlight.js/lib/languages/typescript'
import python from 'highlight.js/lib/languages/python'
import bash from 'highlight.js/lib/languages/bash'
import xml from 'highlight.js/lib/languages/xml'
import css from 'highlight.js/lib/languages/css'
import sql from 'highlight.js/lib/languages/sql'
import json from 'highlight.js/lib/languages/json'
import yaml from 'highlight.js/lib/languages/yaml'
import go from 'highlight.js/lib/languages/go'
import rust from 'highlight.js/lib/languages/rust'
import githubLight from 'highlight.js/styles/github.css?raw'
import githubDarkDimmed from 'highlight.js/styles/github-dark-dimmed.css?raw'
import CodeBlock from './CodeBlock.vue'
import MarkdownTable from './MarkdownTable.vue'
import TaskListItem from './TaskListItem.vue'
import OrderedList from './OrderedList.vue'
import { MarkdownParser } from '../services/MarkdownParser'

const props = defineProps<{ content: string }>()
const blocks = ref<any[]>([])
const previewEl = ref<HTMLElement | null>(null)
defineExpose({ previewEl })

// Register languages
hljs.registerLanguage('markdown', markdown)
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('html', xml)
hljs.registerLanguage('css', css)
hljs.registerLanguage('sql', sql)
hljs.registerLanguage('json', json)
hljs.registerLanguage('yaml', yaml)
hljs.registerLanguage('go', go)
hljs.registerLanguage('rust', rust)

const parser = new MarkdownParser((str: string, lang: string): string => {
  if (lang && hljs.getLanguage(lang)) {
    try {
      return hljs.highlight(str, { language: lang, ignoreIllegals: true }).value
    } catch (__) {}
  }
  return parser.escapeHtml(str)
})

watch(() => props.content, (val) => {
  blocks.value = parser.parse(val || '')
}, { immediate: true })

function loadTheme() {
  const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches
  const themeContent = isDarkMode ? githubDarkDimmed : githubLight
  const existingTheme = document.getElementById('hljs-theme')
  if (existingTheme) existingTheme.remove()
  const style = document.createElement('style')
  style.id = 'hljs-theme'
  style.textContent = themeContent
  document.head.appendChild(style)
}

onMounted(() => {
  loadTheme()
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', loadTheme)
})

onUnmounted(() => {
  window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', loadTheme)
})
</script>

<style scoped>
.preview-content {
  /* Remove padding here */
  overflow-y: auto;
  height: 100%;
}
.no-prose-padding.prose {
  padding: 0 !important;
  margin: 0 !important;
}

.preview-content.prose :deep(ol.unpadded-ol) {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
}

/* Use higher specificity to override Tailwind prose styles */
.preview-content.prose :deep(ul.unpadded-ul) {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
  padding-left: 0 !important;
}
</style>

<!--
  Styles for code blocks, prose, and code block header/actions should be provided globally or in the parent.
  You can move the relevant styles from MarkdownEditor.vue or BlogPostView.vue.
--> 