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
import MarkdownIt from 'markdown-it'
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

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang, ignoreIllegals: true }).value
      } catch (__) {}
    }
    return md.utils.escapeHtml(str)
  }
}).enable(['list']) // Ensure list plugin is enabled

interface Block {
  type: 'code' | 'table' | 'html' | 'task';
  [key: string]: any;
}

interface TableData {
  columns: { field: string; header: string }[];
  rows: Record<string, any>[];
}

// Helper functions for parsing specific block types
function parseCodeBlock(token: any): Block {
  const lang = token.info ? md.utils.unescapeAll(token.info).trim().split(/\s+/g)[0] : ''
  return {
    type: 'code',
    lang,
    content: encodeURIComponent(token.content)
  }
}

function parseTableData(tokens: any[], startIndex: number): { tableData: TableData; endIndex: number } {
  const columns: { field: string; header: string }[] = []
  const rows: Record<string, any>[] = []
  let i = startIndex + 1
  let headerCells: string[] = []

  // Parse header
  while (i < tokens.length && tokens[i].type !== 'thead_close') {
    if (tokens[i].type === 'th_open') {
      i++
      if (tokens[i].type === 'inline') {
        headerCells.push(tokens[i].content)
      }
    }
    i++
  }
  columns.push(...headerCells.map((header, idx) => ({ field: `col${idx}`, header })))

  // Parse rows
  while (i < tokens.length && tokens[i].type !== 'table_close') {
    if (tokens[i].type === 'tr_open') {
      const rowCells: string[] = []
      i++
      while (i < tokens.length && tokens[i].type !== 'tr_close') {
        if (tokens[i].type === 'td_open') {
          i++
          if (tokens[i].type === 'inline') {
            rowCells.push(tokens[i].content)
          }
        }
        i++
      }
      if (rowCells.length) {
        const row: Record<string, any> = {}
        rowCells.forEach((cell, idx) => {
          row[`col${idx}`] = cell
        })
        rows.push(row)
      }
    }
    i++
  }

  return {
    tableData: { columns, rows },
    endIndex: i
  }
}

function parseListContent(tokens: any[], startIndex: number, depth: number = 0): { html: string; endIndex: number; taskBlocks: Block[] } {
  const token = tokens[startIndex]
  const isOrdered = token.type === 'ordered_list_open'
  const start = isOrdered ? parseInt(token.info || '1', 10) : null
  let html = `<${isOrdered ? 'ol' : 'ul'} class="${isOrdered ? 'list-decimal unpadded-ol' : 'list-disc unpadded-ul'} ${depth === 0 ? 'list-outside' : ''}"${start ? ` start="${start}"` : ''}>`;
  let i = startIndex + 1
  const taskBlocks: Block[] = []

  while (i < tokens.length && tokens[i].type !== (isOrdered ? 'ordered_list_close' : 'bullet_list_close')) {
    if (tokens[i].type === 'list_item_open') {
      // Process list item content
      let j = i + 1
      let hasNestedList = false
      let isTask = false
      
      while (j < tokens.length && tokens[j].type !== 'list_item_close') {
        if (tokens[j].type === 'ordered_list_open' || tokens[j].type === 'bullet_list_open') {
          hasNestedList = true
          const { html: nestedHtml, endIndex, taskBlocks: nestedTasks } = parseListContent(tokens, j, depth + 1)
          html += nestedHtml
          taskBlocks.push(...nestedTasks)
          j = endIndex
        } else if (tokens[j].type === 'inline') {
          const match = tokens[j].content.trim().match(/^\[( |x|X)\]\s+(.*)$/)
          if (match) {
            isTask = true
            taskBlocks.push({
              type: 'task',
              modelValue: match[1].toLowerCase() === 'x',
              label: md.renderInline(match[2])
            })
          } else {
            html += '<li class="my-2">' + md.renderInline(tokens[j].content)
            if (!hasNestedList) {
              html += '</li>'
            }
          }
        }
        j++
      }
      
      if (hasNestedList && !isTask) {
        html += '</li>'
      }
      i = j
    }
    i++
  }

  html += `</${isOrdered ? 'ol' : 'ul'}>`
  return { html, endIndex: i, taskBlocks }
}

function parseBlocks(content: string): Block[] {
  const tokens = md.parse(content || '', {})
  const blocks: Block[] = []
  let i = 0

  while (i < tokens.length) {
    const token = tokens[i]

    if (token.type === 'fence') {
      blocks.push(parseCodeBlock(token))
      i++
    } else if (token.type === 'table_open') {
      const { tableData, endIndex } = parseTableData(tokens, i)
      blocks.push({ type: 'table', ...tableData })
      i = endIndex + 1
    } else if (token.type === 'ordered_list_open' || token.type === 'bullet_list_open') {
      const { html, endIndex, taskBlocks } = parseListContent(tokens, i, 0)
      if (html.includes('<li')) { // Only add the list if it has items
        blocks.push({ type: 'html', html })
      }
      blocks.push(...taskBlocks)
      i = endIndex + 1
    } else {
      // Collect consecutive non-special tokens into a single HTML block
      let html = ''
      while (i < tokens.length && 
             !['fence', 'table_open', 'ordered_list_open', 'bullet_list_open'].includes(tokens[i].type)) {
        html += md.renderer.render([tokens[i]], md.options, {})
        i++
      }
      if (html.trim()) {
        blocks.push({ type: 'html', html })
      }
    }
  }

  return blocks
}

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

watch(() => props.content, (val) => {
  blocks.value = parseBlocks(val || '')
}, { immediate: true })

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