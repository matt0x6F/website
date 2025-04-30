<template>
  <div class="code-block-wrapper" :class="{ collapsed: isCollapsed }">
    <div class="code-block-header">
      <span class="code-block-lang">{{ lang }}</span>
      <div class="code-block-actions">
        <button
          class="action-button collapse-button"
          :title="isCollapsed ? 'Expand code block' : 'Collapse code block'"
          @click="toggleCollapse"
        >
          <svg class="collapse-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>
        <button
          class="action-button copy-button"
          :class="{ success: copySuccess, error: copyError }"
          :title="copySuccess ? 'Copied!' : (copyError ? 'Copy failed' : 'Copy code')"
          @click="copyCode"
        >
          <svg class="copy-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
        </button>
      </div>
    </div>
    <transition name="collapse"
      @before-enter="beforeEnter"
      @enter="enter"
      @after-enter="afterEnter"
      @before-leave="beforeLeave"
      @leave="leave"
      @after-leave="afterLeave"
    >
      <pre
        v-show="!isCollapsed"
        ref="preEl"
        class="hljs" :class="'language-' + lang"
        v-html="highlightedCode"
        style="margin: 0; padding: 1em; border-radius: 0 0 0.5em 0.5em; overflow: hidden;"
      ></pre>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import hljs from 'highlight.js/lib/core'
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
import markdown from 'highlight.js/lib/languages/markdown'

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

const props = defineProps<{ lang: string, code: string }>()
const isCollapsed = ref(false)
const copySuccess = ref(false)
const copyError = ref(false)
const preEl = ref<HTMLElement | null>(null)

const decodedCode = computed(() => decodeURIComponent(props.code))

const highlightedCode = computed(() => {
  if (props.lang && hljs.getLanguage(props.lang)) {
    try {
      return hljs.highlight(decodedCode.value, { language: props.lang, ignoreIllegals: true }).value
    } catch (e) {
      return hljs.highlightAuto(decodedCode.value).value
    }
  }
  return hljs.highlightAuto(decodedCode.value).value
})

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}

async function copyCode() {
  try {
    await navigator.clipboard.writeText(decodedCode.value)
    copySuccess.value = true
    copyError.value = false
    setTimeout(() => { copySuccess.value = false }, 2000)
  } catch {
    copyError.value = true
    copySuccess.value = false
    setTimeout(() => { copyError.value = false }, 2000)
  }
}

// Transition hooks for smooth height animation
function beforeEnter(el: Element) {
  const htmlEl = el as HTMLElement
  htmlEl.style.height = '0'
  htmlEl.style.transition = ''
}
function enter(el: Element, done: () => void) {
  const htmlEl = el as HTMLElement
  htmlEl.style.transition = 'height 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
  void htmlEl.offsetWidth // force reflow
  htmlEl.style.height = htmlEl.scrollHeight + 'px'
  htmlEl.addEventListener('transitionend', function handler(e) {
    if (e.propertyName === 'height') {
      htmlEl.removeEventListener('transitionend', handler)
      done()
    }
  })
}
function afterEnter(el: Element) {
  const htmlEl = el as HTMLElement
  htmlEl.style.height = ''
  htmlEl.style.transition = ''
}
function beforeLeave(el: Element) {
  const htmlEl = el as HTMLElement
  htmlEl.style.height = htmlEl.scrollHeight + 'px'
  htmlEl.style.transition = ''
}
function leave(el: Element, done: () => void) {
  const htmlEl = el as HTMLElement
  htmlEl.style.transition = 'height 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
  void htmlEl.offsetWidth // force reflow
  htmlEl.style.height = '0'
  htmlEl.addEventListener('transitionend', function handler(e) {
    if (e.propertyName === 'height') {
      htmlEl.removeEventListener('transitionend', handler)
      done()
    }
  })
}
function afterLeave(el: Element) {
  const htmlEl = el as HTMLElement
  htmlEl.style.height = ''
  htmlEl.style.transition = ''
}
</script>

<style scoped>
.collapse-enter-active, .collapse-leave-active {
  transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.collapse-enter-from, .collapse-leave-to {
  height: 0;
  overflow: hidden;
}
.collapse-enter-to, .collapse-leave-from {
  overflow: hidden;
}
</style> 