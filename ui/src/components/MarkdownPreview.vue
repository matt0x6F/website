<template>
  <div ref="previewEl" class="preview-content prose dark:prose-invert" v-html="renderedHtml"></div>
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

const props = defineProps<{ content: string }>()
const renderedHtml = ref('')
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

// Add a class to pre elements for styling and add code block header/actions
md.renderer.rules.fence = (tokens, idx, options, env, slf) => {
  const token = tokens[idx]
  const info = token.info ? md.utils.unescapeAll(token.info).trim() : ''
  const lang = info ? info.split(/\s+/g)[0] : ''
  const highlighted = token.content && lang && hljs.getLanguage(lang)
    ? hljs.highlight(token.content, { language: lang, ignoreIllegals: true }).value
    : md.utils.escapeHtml(token.content)

  return `
    <div class="code-block-wrapper">
      <div class="code-block-header">
        <span class="code-block-lang">${lang}</span>
        <div class="code-block-actions">
          <button class="action-button collapse-button" title="Toggle code block">
            <svg class="collapse-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>
          <button class="action-button copy-button" data-code="${encodeURIComponent(token.content)}" title="Copy code">
            <svg class="copy-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
          </button>
        </div>
      </div>
      <pre class="hljs language-${lang}"><code class="language-${lang}">${highlighted}</code></pre>
    </div>
  `
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

function addCodeBlockHandlers() {
  // Copy button handlers
  document.querySelectorAll('.copy-button').forEach(button => {
    button.addEventListener('click', async (e) => {
      const target = e.currentTarget as HTMLButtonElement
      const code = decodeURIComponent(target.dataset.code || '')
      try {
        await navigator.clipboard.writeText(code)
        target.classList.add('success')
        setTimeout(() => target.classList.remove('success'), 2000)
      } catch (err) {
        target.classList.add('error')
        setTimeout(() => target.classList.remove('error'), 2000)
      }
    })
  })
  // Collapse button handlers
  document.querySelectorAll('.collapse-button').forEach(button => {
    button.addEventListener('click', (e) => {
      const target = e.currentTarget as HTMLButtonElement
      const wrapper = target.closest('.code-block-wrapper')
      const pre = wrapper?.querySelector('pre')
      if (wrapper && pre) {
        wrapper.classList.toggle('collapsed')
        const isCollapsed = wrapper.classList.contains('collapsed')
        if (isCollapsed) {
          pre.style.height = '0'
        } else {
          pre.style.height = pre.scrollHeight + 'px'
        }
      }
    })
  })
}

watch(() => props.content, (val) => {
  renderedHtml.value = md.render(val || '')
  setTimeout(addCodeBlockHandlers, 100)
}, { immediate: true })

onMounted(() => {
  loadTheme()
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', loadTheme)
  setTimeout(addCodeBlockHandlers, 100)
})
onUnmounted(() => {
  window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', loadTheme)
})
</script>

<!--
  Styles for code blocks, prose, and code block header/actions should be provided globally or in the parent.
  You can move the relevant styles from MarkdownEditor.vue or BlogPostView.vue.
--> 