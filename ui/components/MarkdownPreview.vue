<template>
  <div class="preview-content prose prose-fullwidth dark:prose-invert" ref="previewEl">
    <template v-for="(block, i) in blocks" :key="i">
      <HeadingBlock v-if="block.type === 'heading'" :level="block.level" :content="block.content" />
      <ParagraphBlock v-else-if="block.type === 'paragraph'" :content="block.content" />
      <ListBlock v-else-if="block.type === 'list'" :ordered="block.ordered" :start="block.start" :items="block.items" />
      <BlockquoteBlock v-else-if="block.type === 'blockquote'" :blocks="block.content" />
      <CodeBlock v-else-if="block.type === 'code'" :lang="block.lang" :code="block.content" />
      <MermaidBlock v-else-if="block.type === 'mermaid'" :code="block.content" />
      <MarkdownTable v-else-if="block.type === 'table'" :columns="block.columns" :rows="block.rows" />
      <TaskListItem v-else-if="block.type === 'task'" :modelValue="block.modelValue" :label="block.label" />
      <OrderedList v-else-if="block.type === 'ordered_list'" :items="block.items" :start="block.start" />
      <section v-else v-html="block.html"></section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineExpose, getCurrentInstance } from 'vue'
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
import CodeBlock from '@/components/markdown/CodeBlock.vue'
import MarkdownTable from '@/components/markdown/MarkdownTable.vue'
import TaskListItem from '@/components/markdown/TaskListItem.vue'
import OrderedList from '@/components/markdown/OrderedList.vue'
import HeadingBlock from '@/components/markdown/HeadingBlock.vue'
import ParagraphBlock from '@/components/markdown/ParagraphBlock.vue'
import ListBlock from '@/components/markdown/ListBlock.vue'
import BlockquoteBlock from '@/components/markdown/BlockquoteBlock.vue'
import MermaidBlock from '@/components/markdown/MermaidBlock.vue'
import { MarkdownParser } from '@/services/MarkdownParser'
import type { PostDetails } from '@/lib/api'

const props = defineProps<{
  content: string,
  meta?: PostDetails | null
}>()
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
.prose-fullwidth {
  max-width: 100% !important;
}
</style>

<style scoped>
/* Highlight.js code block styles */
.hljs {
  background: var(--p-surface-50);
  color: var(--p-text-color);
  padding: 1em;
}

:deep(ol.unpadded-ol) {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
}
:deep(ul.unpadded-ul) {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
  padding-left: 0 !important;
}

@media (prefers-color-scheme: light) {
  .hljs {
    color: #1a1a1a;
  }
  .hljs-subst {
    color: #1a1a1a;
  }
  .hljs-emphasis {
    color: #1a1a1a;
    font-style: italic;
  }
  .hljs-strong {
    color: #1a1a1a;
    font-weight: bold;
  }
  .hljs-doctag,
  .hljs-keyword,
  .hljs-meta .hljs-keyword,
  .hljs-template-tag,
  .hljs-template-variable,
  .hljs-type,
  .hljs-variable.language_ {
    color: #d73a49;
  }
  .hljs-title,
  .hljs-title.class_,
  .hljs-title.class_.inherited__,
  .hljs-title.function_ {
    color: #6f42c1;
  }
  .hljs-attr,
  .hljs-attribute,
  .hljs-literal,
  .hljs-meta,
  .hljs-number,
  .hljs-operator,
  .hljs-selector-attr,
  .hljs-selector-class,
  .hljs-selector-id,
  .hljs-variable {
    color: #005cc5;
  }
  .hljs-string,
  .hljs-meta .hljs-string,
  .hljs-regexp {
    color: #032f62;
  }
  .hljs-built_in,
  .hljs-symbol {
    color: #e36209;
  }
  .hljs-comment,
  .hljs-code,
  .hljs-formula {
    color: #6a737d;
  }
  .hljs-name,
  .hljs-quote,
  .hljs-selector-pseudo,
  .hljs-selector-tag {
    color: #22863a;
  }
  .hljs-addition {
    color: #22863a;
    background-color: #f0fff4;
  }
  .hljs-deletion {
    color: #b31d28;
    background-color: #ffeef0;
  }
  .hljs-section {
    color: #005cc5;
    font-weight: bold;
  }
  .hljs-bullet {
    color: #735c0f;
  }
  .hljs-emphasis {
    color: #24292e;
    font-style: italic;
  }
  .hljs-strong {
    color: #24292e;
    font-weight: bold;
  }
}

@media (prefers-color-scheme: dark) {
  .hljs {
    color: #c9d1d9;
    background: var(--p-surface-800);
  }
  .hljs-doctag,
  .hljs-keyword,
  .hljs-meta .hljs-keyword,
  .hljs-template-tag,
  .hljs-template-variable,
  .hljs-type,
  .hljs-variable.language_ {
    color: #ff7b72;
  }
  .hljs-title,
  .hljs-title.class_,
  .hljs-title.class_.inherited__,
  .hljs-title.function_ {
    color: #d2a8ff;
  }
  .hljs-attr,
  .hljs-attribute,
  .hljs-literal,
  .hljs-meta,
  .hljs-number,
  .hljs-operator,
  .hljs-selector-attr,
  .hljs-selector-class,
  .hljs-selector-id,
  .hljs-variable {
    color: #79c0ff;
  }
  .hljs-string,
  .hljs-meta .hljs-string,
  .hljs-regexp {
    color: #a5d6ff;
  }
  .hljs-built_in,
  .hljs-symbol {
    color: #ffa657;
  }
  .hljs-comment,
  .hljs-code,
  .hljs-formula {
    color: #8b949e;
  }
  .hljs-name,
  .hljs-quote,
  .hljs-selector-pseudo,
  .hljs-selector-tag {
    color: #7ee787;
  }
  .hljs-subst {
    color: #c9d1d9;
  }
  .hljs-section {
    color: #1f6feb;
    font-weight: bold;
  }
  .hljs-bullet {
    color: #f2cc60;
  }
  .hljs-emphasis {
    color: #c9d1d9;
    font-style: italic;
  }
  .hljs-strong {
    color: #c9d1d9;
    font-weight: bold;
  }
  .hljs-addition {
    color: #aff5b4;
    background-color: #033a16;
  }
  .hljs-deletion {
    color: #ffdcd7;
    background-color: #67060c;
  }
}
</style>

<!--
  Styles for code blocks, prose, and code block header/actions should be provided globally or in the parent.
  You can move the relevant styles from MarkdownEditor.vue or BlogPostView.vue.
--> 