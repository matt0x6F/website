<template>
  <div class="preview-content prose dark:prose-invert">
    <template v-for="(block, i) in blocks" :key="i">
      <CodeBlock v-if="block.type === 'code'" :lang="block.lang" :code="block.content" />
      <MarkdownTable v-else-if="block.type === 'table'" :columns="block.columns" :rows="block.rows" />
      <TaskListItem v-else-if="block.type === 'task'" :modelValue="block.checked" :label="block.label" />
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
})

function parseBlocks(content: string) {
  const tokens = md.parse(content || '', {})
  const blocks: any[] = []
  let i = 0
  while (i < tokens.length) {
    const token = tokens[i]
    if (token.type === 'fence') {
      // Code block
      const lang = token.info ? md.utils.unescapeAll(token.info).trim().split(/\s+/g)[0] : ''
      blocks.push({
        type: 'code',
        lang,
        content: encodeURIComponent(token.content)
      })
      i++
    } else if (token.type === 'table_open') {
      // Extract table data
      const columns: { field: string, header: string }[] = []
      const rows: Record<string, any>[] = []
      let headerCells: string[] = []
      let rowCells: string[] = []
      let fieldPrefix = 0
      i++
      while (i < tokens.length && tokens[i].type !== 'table_close') {
        if (tokens[i].type === 'thead_open') {
          i++
          while (i < tokens.length && tokens[i].type !== 'thead_close') {
            if (tokens[i].type === 'th_open') {
              i++
              if (tokens[i].type === 'inline') {
                headerCells.push(tokens[i].content)
              }
            }
            i++
          }
          // Set up columns
          columns.push(...headerCells.map((header, idx) => ({ field: `col${idx}`, header })))
        } else if (tokens[i].type === 'tr_open') {
          rowCells = []
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
        } else {
          i++
        }
      }
      blocks.push({ type: 'table', columns, rows })
      i++ // skip table_close
    } else if (token.type === 'list_item_open') {
      // Check for task list item
      let label = ''
      let checked = false
      let j = i + 1
      // Find the inline token inside the list item
      while (j < tokens.length && tokens[j].type !== 'list_item_close') {
        if (tokens[j].type === 'inline') {
          const content = tokens[j].content.trim()
          const match = content.match(/^\[( |x|X)\]\s+(.*)$/)
          if (match) {
            checked = match[1].toLowerCase() === 'x'
            // Render the remaining content as markdown to handle links and other formatting
            label = md.renderInline(match[2])
            blocks.push({ type: 'task', checked, label })
            // Skip to list_item_close
            while (i < tokens.length && tokens[i].type !== 'list_item_close') i++
            i++
            break
          }
        }
        j++
      }
      if (label === '') {
        // Not a task list item, fallback to HTML
        let html = ''
        while (i < tokens.length && tokens[i].type !== 'list_item_close') {
          html += md.renderer.render([tokens[i]], md.options, {})
          i++
        }
        if (html.trim()) {
          blocks.push({ type: 'html', html })
        }
        i++
      }
    } else {
      // Collect consecutive non-code tokens into a single HTML block
      let html = ''
      while (i < tokens.length && tokens[i].type !== 'fence' && tokens[i].type !== 'table_open' && tokens[i].type !== 'list_item_open') {
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

<style>
.preview-content {
  /* Remove padding here */
  overflow-y: auto;
  height: 100%;
}
.no-prose-padding.prose {
  padding: 0 !important;
  margin: 0 !important;
}
</style>

<!--
  Styles for code blocks, prose, and code block header/actions should be provided globally or in the parent.
  You can move the relevant styles from MarkdownEditor.vue or BlogPostView.vue.
--> 