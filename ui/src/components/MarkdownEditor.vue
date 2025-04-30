<template>
  <div class="editor-wrapper" :class="{ 'expanded': isExpanded }">
    <label v-if="label" class="block mb-2 font-medium" :class="{ 'hidden': isExpanded }">{{ label }}</label>
    <div class="editor-container">
      <Toolbar class="editor-toolbar">
        <template #start>
          <div class="flex gap-1">
            <Button
              type="button"
              :icon="!showPreview ? 'pi pi-pencil' : 'pi pi-eye'"
              :label="!showPreview ? 'Edit' : 'Preview'"
              @click="showPreview = !showPreview"
              size="small"
              :outlined="true"
              :class="{ 'p-button-secondary': !showPreview }"
            />
            <span class="border-r border-gray-300 dark:border-gray-600 mx-2"></span>
            <Button
              v-tooltip.bottom="'Bold'"
              type="button"
              label="B"
              class="font-bold"
              @click="applyFormat('bold')"
              size="small"
              text
              :disabled="showPreview"
            />
            <Button
              v-tooltip.bottom="'Italic'"
              type="button"
              label="I"
              class="italic"
              @click="applyFormat('italic')"
              size="small"
              text
              :disabled="showPreview"
            />
            <Button
              v-tooltip.bottom="'Code'"
              type="button"
              icon="pi pi-code"
              @click="applyFormat('code')"
              size="small"
              text
              :disabled="showPreview"
            />
            <span class="border-r border-gray-300 dark:border-gray-600 mx-2"></span>
            <Button
              v-tooltip.bottom="'Heading 1'"
              type="button"
              label="H1"
              @click="applyFormat('h1')"
              size="small"
              text
              :disabled="showPreview"
            />
            <Button
              v-tooltip.bottom="'Heading 2'"
              type="button"
              label="H2"
              @click="applyFormat('h2')"
              size="small"
              text
              :disabled="showPreview"
            />
            <Button
              v-tooltip.bottom="'Heading 3'"
              type="button"
              label="H3"
              @click="applyFormat('h3')"
              size="small"
              text
              :disabled="showPreview"
            />
            <span class="border-r border-gray-300 dark:border-gray-600 mx-2"></span>
            <Button
              v-tooltip.bottom="'Link'"
              type="button"
              icon="pi pi-link"
              @click="applyFormat('link')"
              size="small"
              text
              :disabled="showPreview"
            />
            <Button
              v-tooltip.bottom="'Code Block'"
              type="button"
              icon="pi pi-code"
              @click="applyFormat('codeblock')"
              size="small"
              text
              :disabled="showPreview"
            />
          </div>
        </template>
        <template #end>
          <Button
            type="button"
            :icon="isExpanded ? 'pi pi-window-minimize' : 'pi pi-window-maximize'"
            @click="toggleExpanded"
            size="small"
            text
            severity="secondary"
            v-tooltip.bottom="isExpanded ? 'Minimize' : 'Maximize'"
          />
        </template>
      </Toolbar>
      
      <div class="editor-content">
        <div v-if="!showPreview" class="editor-container-inner">
          <textarea
            ref="textarea"
            v-model="editorContent"
            class="editor-textarea"
            @drop="handleDrop"
            @dragover.prevent
            @scroll="handleEditorScroll"
            @keydown="handleEditorKeydown"
            @input="handleEditorInput"
          ></textarea>
          <pre class="editor-highlight"><code v-html="highlightedContent"></code></pre>
        </div>
        
        <MarkdownPreview
          v-else
          ref="previewRef"
          :content="editorContent"
          class="editor-preview-absolute editor-preview-padded"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import Button from 'primevue/button'
import Toolbar from 'primevue/toolbar'
import MarkdownPreview from './MarkdownPreview.vue'
import hljs from 'highlight.js/lib/core'
import markdown from 'highlight.js/lib/languages/markdown'

hljs.registerLanguage('markdown', markdown)

const props = defineProps<{
  modelValue: string
  label?: string
  postId?: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'file-upload', files: File[]): void
}>()

// Editor state
const editorContent = ref('')
const showPreview = ref(false)
const isExpanded = ref(false)

// Add scroll position tracking
const lastEditorScrollPosition = ref(0)
const lastPreviewScrollPosition = ref(0)

// Initialize editor content when props change
watch(() => props.modelValue, (newValue) => {
  console.log('MarkdownEditor received new content:', newValue)
  if (newValue !== editorContent.value) {
    editorContent.value = newValue || ''
    console.log('MarkdownEditor content updated to:', editorContent.value)
  }
}, { immediate: true })

// Watch for content changes and emit updates
watch(editorContent, (newContent) => {
  console.log('Editor content changed:', newContent)
  if (newContent !== props.modelValue) {
    emit('update:modelValue', newContent)
    console.log('Emitted new content to parent')
  }
})

function toggleExpanded() {
  isExpanded.value = !isExpanded.value
}

const previewRef = ref<any>(null)
const textarea = ref<HTMLTextAreaElement | null>(null)
let lastScrollPercent = 0

watch(showPreview, (isPreview, wasPreview) => {
  // Store scroll percent before toggling
  if (isPreview) {
    // Going to preview: store textarea scroll percent
    if (textarea.value) {
      lastScrollPercent = getScrollPercentage(textarea.value)
    }
  } else {
    // Going to edit: store preview scroll percent
    const previewEl = previewRef.value?.previewEl as HTMLElement | null
    if (previewEl) {
      lastScrollPercent = getScrollPercentage(previewEl)
    }
  }

  // After new view is rendered, set scroll position
  nextTick(() => {
    setTimeout(() => {
      if (isPreview) {
        // Set preview scroll
        const previewEl = previewRef.value?.previewEl as HTMLElement | null
        if (previewEl) {
          setScrollFromPercentage(previewEl, lastScrollPercent)
        }
      } else {
        // Set textarea scroll
        if (textarea.value) {
          setScrollFromPercentage(textarea.value, lastScrollPercent)
        }
      }
    }, 50)
  })
})

const handleEditorScroll = (e: Event) => {
  const target = e.target as HTMLTextAreaElement
  const highlight = target.nextElementSibling as HTMLElement
  if (highlight) {
    highlight.scrollTop = target.scrollTop
  }
  lastEditorScrollPosition.value = getScrollPercentage(target)
}

const handleEditorKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Tab') {
    e.preventDefault()
    const target = e.target as HTMLTextAreaElement
    const start = target.selectionStart
    const end = target.selectionEnd
    const spaces = '  ' // 2 spaces for indentation
    
    editorContent.value = editorContent.value.substring(0, start) + spaces + editorContent.value.substring(end)
    
    // Move cursor after the inserted spaces
    nextTick(() => {
      target.selectionStart = target.selectionEnd = start + spaces.length
    })
  }
}

const handleEditorInput = (e: Event) => {
  const target = e.target as HTMLTextAreaElement
  const highlight = target.nextElementSibling as HTMLElement
  if (highlight) {
    highlight.scrollTop = target.scrollTop
  }
}

const handleDrop = async (e: DragEvent) => {
  e.preventDefault()
  
  if (!props.postId) {
    emit('file-upload', [])
    return
  }

  const files = Array.from(e.dataTransfer?.files || [])
  if (files.length > 0) {
    emit('file-upload', files)
  }
}

// Function to get scroll position as a percentage
function getScrollPercentage(element: HTMLElement) {
  const scrollHeight = element.scrollHeight - element.clientHeight
  if (scrollHeight <= 0) return 0
  return element.scrollTop / scrollHeight
}

// Function to set scroll position from a percentage
function setScrollFromPercentage(element: HTMLElement, percentage: number) {
  const scrollHeight = element.scrollHeight - element.clientHeight
  element.scrollTop = scrollHeight * percentage
}

const highlightedContent = computed(() => {
  if (!editorContent.value) return ''
  try {
    return hljs.highlight(editorContent.value, { language: 'markdown' }).value
  } catch (error) {
    return editorContent.value // fallback to plain text
  }
})

function applyFormat(format: string) {
  if (!textarea.value) return

  const start = textarea.value.selectionStart
  const end = textarea.value.selectionEnd
  const selectedText = editorContent.value.substring(start, end)
  let replacement = ''
  let cursorOffset = 0

  switch (format) {
    case 'bold':
      replacement = selectedText ? `**${selectedText}**` : '**bold text**'
      cursorOffset = selectedText ? 2 : 2
      break
    case 'italic':
      replacement = selectedText ? `*${selectedText}*` : '*italic text*'
      cursorOffset = selectedText ? 1 : 1
      break
    case 'code':
      replacement = selectedText ? '`' + selectedText + '`' : '`code`'
      cursorOffset = selectedText ? 1 : 1
      break
    case 'h1':
      replacement = `# ${selectedText || 'Heading 1'}`
      cursorOffset = 2
      break
    case 'h2':
      replacement = `## ${selectedText || 'Heading 2'}`
      cursorOffset = 3
      break
    case 'h3':
      replacement = `### ${selectedText || 'Heading 3'}`
      cursorOffset = 4
      break
    case 'link':
      if (selectedText) {
        replacement = `[${selectedText}](url)`
        cursorOffset = 1
      } else {
        replacement = '[link text](url)'
        cursorOffset = 1
      }
      break
    case 'codeblock':
      const language = 'language'
      if (selectedText) {
        replacement = `\`\`\`${language}\n${selectedText}\n\`\`\``
        cursorOffset = language.length + 4
      } else {
        replacement = `\`\`\`${language}\ncode here\n\`\`\``
        cursorOffset = language.length + 4
      }
      break
  }

  // Insert the replacement text
  editorContent.value = editorContent.value.substring(0, start) + replacement + editorContent.value.substring(end)

  // Set cursor position after the operation
  nextTick(() => {
    if (textarea.value) {
      if (selectedText) {
        // If there was selected text, place cursor at the end of the replacement
        textarea.value.selectionStart = textarea.value.selectionEnd = start + replacement.length
      } else {
        // If no text was selected, place cursor after the opening markdown
        textarea.value.selectionStart = textarea.value.selectionEnd = start + cursorOffset
      }
      textarea.value.focus()
    }
  })
}
</script>

<style>
.editor-wrapper {
  flex: 1;
  min-height: 600px;
  display: flex;
  flex-direction: column;
}

.editor-wrapper.expanded {
  position: fixed;
  top: 1.5rem;
  left: 1.5rem;
  right: 1.5rem;
  bottom: 1.5rem;
  z-index: 1000;
  margin: 0;
  height: auto;
  background: var(--p-surface-100);
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}

@media (prefers-color-scheme: dark) {
  .editor-wrapper.expanded {
    background: var(--p-surface-700);
  }
}

.editor-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--p-content-border-color);
  border-radius: 0.5rem;
  background: var(--p-surface-100);
  min-height: 0;
  overflow: hidden;
  padding: 0;
}

@media (prefers-color-scheme: dark) {
  .editor-container {
    background: var(--p-surface-700);
  }
}

.editor-content {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: var(--p-surface-50);
  min-height: 0;
}

@media (prefers-color-scheme: dark) {
  .editor-content {
    background: var(--p-surface-800);
  }
}

.editor-container-inner {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--p-surface-50);
}

@media (prefers-color-scheme: dark) {
  .editor-container-inner {
    background: var(--p-surface-800);
  }
}

.editor-textarea,
.editor-highlight {
  margin: 0;
  border: 0;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 1.5rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.875rem;
  line-height: 1.5rem;
  tab-size: 2;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
  overflow-x: hidden;
  overflow-y: auto;
}

.editor-textarea {
  z-index: 1;
  color: transparent;
  background: transparent;
  caret-color: var(--p-text-color);
  resize: none;
  -webkit-text-fill-color: transparent;
  outline: none;
}

.editor-textarea::selection {
  background: rgba(128, 203, 196, 0.2);
  color: transparent;
}

.editor-highlight {
  z-index: 0;
  pointer-events: none;
  padding-right: calc(1rem + 8px);
  color: var(--p-text-color);
}

.editor-highlight code {
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
  display: block;
}

/* Ensure consistent block spacing */
.editor-highlight p,
.editor-highlight pre,
.editor-highlight blockquote {
  margin: 0;
  padding: 0;
}

/* Highlight.js theme overrides for better visibility */
.editor-highlight .hljs-section {
  color: var(--p-primary-700);
  font-weight: bold;
}

.editor-highlight .hljs-bullet {
  color: var(--p-primary-600);
}

.editor-highlight .hljs-link {
  color: var(--p-primary-700);
  text-decoration: underline;
}

.editor-highlight .hljs-quote {
  color: var(--p-surface-700);
  font-style: italic;
}

.editor-highlight .hljs-strong {
  color: var(--p-primary-700);
  font-weight: bold;
}

.editor-highlight .hljs-emphasis {
  color: var(--p-primary-700);
  font-style: italic;
}

.editor-highlight .hljs-code {
  color: var(--p-primary-800);
}

@media (prefers-color-scheme: dark) {
  .editor-highlight .hljs-section {
    color: var(--p-primary-400);
  }

  .editor-highlight .hljs-bullet {
    color: var(--p-primary-300);
  }

  .editor-highlight .hljs-link {
    color: var(--p-primary-300);
  }

  .editor-highlight .hljs-quote {
    color: var(--p-surface-400);
  }

  .editor-highlight .hljs-strong {
    color: var(--p-primary-300);
  }

  .editor-highlight .hljs-emphasis {
    color: var(--p-primary-300);
  }

  .editor-highlight .hljs-code {
    color: var(--p-primary-400);
  }
}

.preview-content {
  padding: 1.5rem;
  overflow-y: auto;
  height: 100%;
}

/* Code block styles */
:deep(.hljs) {
  background: var(--p-surface-50);
  color: var(--p-text-color);
  padding: 1em;
}

@media (prefers-color-scheme: light) {
  :deep(.hljs) {
    background: var(--p-surface-50);
    color: var(--p-surface-900);
  }

  :deep(.hljs-keyword),
  :deep(.hljs-selector-tag),
  :deep(.hljs-title),
  :deep(.hljs-section) {
    color: #d73a49;
  }

  :deep(.hljs-string),
  :deep(.hljs-attr) {
    color: #032f62;
  }

  :deep(.hljs-number),
  :deep(.hljs-literal) {
    color: #005cc5;
  }

  :deep(.hljs-comment) {
    color: #6a737d;
  }

  :deep(.hljs-doctag) {
    color: #d73a49;
  }
}

@media (prefers-color-scheme: dark) {
  :deep(.hljs) {
    background: var(--p-surface-800);
    color: var(--p-surface-50);
  }

  :deep(.hljs-keyword),
  :deep(.hljs-selector-tag),
  :deep(.hljs-title),
  :deep(.hljs-section) {
    color: #ff7b72;
  }

  :deep(.hljs-string),
  :deep(.hljs-attr) {
    color: #a5d6ff;
  }

  :deep(.hljs-number),
  :deep(.hljs-literal) {
    color: #79c0ff;
  }

  :deep(.hljs-comment) {
    color: #8b949e;
  }

  :deep(.hljs-doctag) {
    color: #ff7b72;
  }
}

.editor-preview-absolute {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  height: 100%;
  width: 100%;
  overflow-y: auto;
  background: var(--p-surface-50);
}
@media (prefers-color-scheme: dark) {
  .editor-preview-absolute {
    background: var(--p-surface-800);
  }
}

.editor-preview-padded {
  padding: 1.5rem;
}
</style>

<style scoped>
/* Import Highlight.js styles */
@import 'highlight.js/styles/github-dark.css';

/* Base styles for code blocks */
.hljs {
  background: var(--p-surface-50);
  color: var(--p-text-color);
}

/* Light mode theme */
@media (prefers-color-scheme: light) {
  .hljs {
    color: #1a1a1a;  /* Darker base text color */
  }

  .hljs-subst {
    color: #1a1a1a;  /* Match base text color */
  }

  .hljs-emphasis {
    color: #1a1a1a;  /* Match base text color */
    font-style: italic;
  }

  .hljs-strong {
    color: #1a1a1a;  /* Match base text color */
    font-weight: bold;
  }

  /* Keep GitHub's syntax highlighting colors for specific elements */
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

/* Dark mode theme */
@media (prefers-color-scheme: dark) {
  .hljs {
    color: #c9d1d9;
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

.editor-toolbar {
  border-bottom: 1px solid var(--p-content-border-color);
  background: var(--p-surface-50);
  border-radius: 0.5rem 0.5rem 0 0;
  padding: 0.5rem;
}

@media (prefers-color-scheme: dark) {
  .editor-toolbar {
    background: var(--p-surface-800);
  }
}

.editor-toolbar :deep(.p-toolbar-group-start),
.editor-toolbar :deep(.p-toolbar-group-end) {
  gap: 0.25rem;
}

.editor-toolbar :deep(.p-button.p-button-text) {
  padding: 0.5rem;
  color: var(--p-text-color);
}

.editor-toolbar :deep(.p-button.p-button-text:hover) {
  background: var(--p-surface-200);
}

@media (prefers-color-scheme: dark) {
  .editor-toolbar :deep(.p-button.p-button-text) {
    color: var(--p-surface-100);
  }
  
  .editor-toolbar :deep(.p-button.p-button-text:hover) {
    background: var(--p-surface-700);
  }
}

.editor-toolbar :deep(.p-button.p-button-text:disabled) {
  opacity: 0.5;
  cursor: not-allowed;
}
</style> 