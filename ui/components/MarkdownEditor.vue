<template>
  <div class="editor-wrapper" :class="{ 'expanded': isExpanded }">
    <label v-if="label" class="block mb-2 font-medium" :class="{ 'hidden': isExpanded }">{{ label }}</label>
    <div class="editor-container">
      <Toolbar class="editor-toolbar">
        <template #start>
          <div class="flex gap-1">
            <Button
              v-tooltip.bottom="'Bold'"
              type="button"
              label="B"
              class="font-bold"
              @click="applyFormat('bold')"
              size="small"
              text
            />
            <Button
              v-tooltip.bottom="'Italic'"
              type="button"
              label="I"
              class="italic"
              @click="applyFormat('italic')"
              size="small"
              text
            />
            <Button
              v-tooltip.bottom="'Code'"
              type="button"
              icon="pi pi-code"
              @click="applyFormat('code')"
              size="small"
              text
            />
            <span class="border-r border-gray-300 dark:border-gray-600 mx-2"></span>
            <Button
              v-tooltip.bottom="'Heading 1'"
              type="button"
              label="H1"
              @click="applyFormat('h1')"
              size="small"
              text
            />
            <Button
              v-tooltip.bottom="'Heading 2'"
              type="button"
              label="H2"
              @click="applyFormat('h2')"
              size="small"
              text
            />
            <Button
              v-tooltip.bottom="'Heading 3'"
              type="button"
              label="H3"
              @click="applyFormat('h3')"
              size="small"
              text
            />
            <span class="border-r border-gray-300 dark:border-gray-600 mx-2"></span>
            <Button
              v-tooltip.bottom="'Link'"
              type="button"
              icon="pi pi-link"
              @click="applyFormat('link')"
              size="small"
              text
            />
            <Button
              v-tooltip.bottom="'Image'"
              type="button"
              icon="pi pi-image"
              @click="applyFormat('image')"
              size="small"
              text
            />
            <Button
              v-tooltip.bottom="'Code Block'"
              type="button"
              icon="pi pi-code"
              @click="applyFormat('codeblock')"
              size="small"
              text
            />
            <Button
              v-tooltip.bottom="'Unordered List'"
              type="button"
              icon="pi pi-list"
              @click="applyListFormat('unordered')"
              size="small"
              text
            />
            <Button
              v-tooltip.bottom="'Ordered List'"
              type="button"
              label="1."
              @click="applyListFormat('ordered')"
              size="small"
              text
            />
            <Button
              v-tooltip.bottom="'Checklist'"
              type="button"
              icon="pi pi-list-check"
              @click="applyListFormat('check')"
              size="small"
              text
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
      
      <div class="editor-scroll-area editor-content split-view"
           style="flex: 1 1 0%; height: 100%;"
           @dragover="handleDragOver"
           @dragleave="handleDragLeave"
           @drop="handleDrop"
           >
        <div class="editor-container-inner split-editor">
          <textarea
            ref="textarea"
            v-model="editorContent"
            class="editor-textarea"
            @dragover.prevent
            @scroll="handleEditorScroll"
            @keydown="handleEditorKeydown"
            @input="handleEditorInput"
            @paste="handlePaste"
          ></textarea>
          <pre class="editor-highlight"><code v-html="highlightedContent"></code></pre>
          <div v-if="isDragging && dragCursorPos !== null" class="drag-cursor-indicator" :style="dragCursorStyle"></div>
        </div>
        
        <MarkdownPreview
          ref="previewRef"
          :content="editorContent"
          class="editor-preview-absolute editor-preview-padded split-preview"
          @scroll.native="handlePreviewScroll"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import Button from 'primevue/button'
import Toolbar from 'primevue/toolbar'
import MarkdownPreview from './MarkdownPreview.vue'
import hljs from 'highlight.js/lib/core'
import markdown from 'highlight.js/lib/languages/markdown'
import { useAuthStore } from '@/stores/auth'
import type { CSSProperties } from 'vue'
import { uploadFilesWithAuth } from '@/composables/useFileUpload'

hljs.registerLanguage('markdown', markdown)

const props = defineProps<{
  modelValue: string
  label?: string
  postId?: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'file-upload', files: File[]): void
  (e: 'file-upload-error', message: string): void
}>()

// Editor state
const editorContent = ref('')
const isExpanded = ref(false)

// View mode can be 'edit', 'preview', or 'split'
const viewMode = ref('split')

// Add these refs and variables in the script section after other refs
const isScrollingEditor = ref(false)
const isScrollingPreview = ref(false)

// Add these refs at the top of the script
let isSyncingEditorScroll = false
let isSyncingPreviewScroll = false

// Drag-and-drop state
const isDragging = ref(false)
const dragCursorPos = ref<number | null>(null)

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
  if (!isExpanded.value && viewMode.value === 'split') {
    viewMode.value = 'edit'
  }
}

const previewRef = ref<any>(null)
const textarea = ref<HTMLTextAreaElement | null>(null)
let lastScrollPercent = 0

watch(viewMode, (newMode, oldMode) => {
  // Store scroll percent before toggling
  if (oldMode === 'edit') {
    // Going from edit to preview or split: store textarea scroll percent
    if (textarea.value) {
      lastScrollPercent = getScrollPercentage(textarea.value)
    }
  } else if (oldMode === 'preview' || oldMode === 'split') {
    // Going to edit: store preview scroll percent
    const previewEl = previewRef.value?.previewEl as HTMLElement | null
    if (previewEl) {
      lastScrollPercent = getScrollPercentage(previewEl)
    }
  }

  // After new view is rendered, set scroll position
  nextTick(() => {
    setTimeout(() => {
      if (newMode === 'preview' || newMode === 'split') {
        // Set preview scroll
        const previewEl = previewRef.value?.previewEl as HTMLElement | null
        if (previewEl) {
          setScrollFromPercentage(previewEl, lastScrollPercent)
        }
      }
      if (newMode === 'edit' || newMode === 'split') {
        // Set textarea scroll
        if (textarea.value) {
          setScrollFromPercentage(textarea.value, lastScrollPercent)
        }
      }
    }, 50)
  })
})

// Modify the handleEditorScroll function
const handleEditorScroll = (e: Event) => {
  if (isSyncingEditorScroll) {
    isSyncingEditorScroll = false
    return
  }
  console.log('Editor scroll event triggered')
  const target = e.target as HTMLTextAreaElement
  const highlight = target.nextElementSibling as HTMLElement
  if (highlight) {
    // Proportional scroll sync
    const percent = getScrollPercentage(target)
    highlight.scrollTop = percent * (highlight.scrollHeight - highlight.clientHeight)
  }
  
  const scrollPercentage = getScrollPercentage(target)
  console.log('Editor scroll percentage:', scrollPercentage)
  
  let previewEl = previewRef.value?.previewEl
  if (!previewEl && previewRef.value && previewRef.value.$el) {
    previewEl = previewRef.value.$el
    console.log('Using previewRef.value.$el as fallback:', previewEl)
  }
  if (previewEl) {
    console.log('Setting preview scroll on element:', previewEl)
    isSyncingPreviewScroll = true
    previewEl.scrollTop = scrollPercentage * (previewEl.scrollHeight - previewEl.clientHeight)
  } else {
    console.log('No preview element found!')
  }
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
    // Proportional scroll sync
    const percent = getScrollPercentage(target)
    highlight.scrollTop = percent * (highlight.scrollHeight - highlight.clientHeight)
  }
}

// Helper to get cursor position from mouse event
function getCursorPositionFromMouse(e: DragEvent) {
  if (!textarea.value) return 0
  const { top, left } = textarea.value.getBoundingClientRect()
  const y = e.clientY - top
  // Estimate line height
  const lineHeight = parseFloat(getComputedStyle(textarea.value).lineHeight || '20')
  const approxLine = Math.floor(y / lineHeight)
  // Find the character index at the start of that line
  const lines = editorContent.value.split('\n')
  let pos = 0
  for (let i = 0; i < approxLine && i < lines.length; i++) {
    pos += lines[i].length + 1 // +1 for newline
  }
  return Math.min(pos, editorContent.value.length)
}

function handleDragOver(e: DragEvent) {
  e.preventDefault()
  isDragging.value = true
  dragCursorPos.value = getCursorPositionFromMouse(e)
}

function handleDragLeave(e: DragEvent) {
  isDragging.value = false
  dragCursorPos.value = null
}

function insertMarkdownAtCursor(urlsMarkdown: string, insertPos: number) {
  let before = editorContent.value.slice(0, insertPos);
  let after = editorContent.value.slice(insertPos);
  const beforeChar = before.length > 0 ? before[before.length - 1] : '';
  const afterChar = after.length > 0 ? after[0] : '';

  // Find the start and end of the current line
  const lineStart = before.lastIndexOf('\n') + 1;
  const isBlankLine = editorContent.value.slice(lineStart, insertPos + (after.indexOf('\n') === -1 ? 0 : after.indexOf('\n'))).trim() === '' && (after.indexOf('\n') !== -1 || insertPos === editorContent.value.length);

  if (isBlankLine) {
    // Find the start of the previous line (above the blank line)
    const prevLineStart = editorContent.value.lastIndexOf('\n', lineStart - 2) + 1;
    const beforeLines = editorContent.value.slice(0, prevLineStart);
    // Find the end of the current line (either next newline or end of content)
    const afterLines = after.indexOf('\n') !== -1 ? editorContent.value.slice(insertPos + after.indexOf('\n')) : '';
    // Insert image, remove blank line above, add two blank lines below
    editorContent.value = beforeLines + urlsMarkdown + '\n\n' + afterLines.replace(/^\n+/, '');
    nextTick(() => {
      if (textarea.value) {
        textarea.value.selectionStart = textarea.value.selectionEnd = (beforeLines + urlsMarkdown + '\n\n').length;
        textarea.value.focus();
      }
    });
  } else {
    // Previous logic for non-blank lines
    let insertText = urlsMarkdown;
    if (beforeChar && beforeChar !== '\n') {
      insertText = '\n' + insertText;
    }
    if (afterChar && afterChar !== '\n') {
      insertText = insertText + '\n';
    }
    editorContent.value = before + insertText + after;
    nextTick(() => {
      if (textarea.value) {
        textarea.value.selectionStart = textarea.value.selectionEnd = (before + insertText).length;
        textarea.value.focus();
      }
    });
  }
}

async function handleDrop(e: DragEvent) {
  e.preventDefault();
  isDragging.value = false;
  const files = Array.from(e.dataTransfer?.files || []);

  // Early return if no files or postId
  if (!props.postId || files.length === 0) {
    emit('file-upload', files);
    if (!props.postId) {
      emit('file-upload-error', 'Please save the file before uploading attachments.');
    }
    return;
  }

  // Use the composable for upload
  const uploadedUrls = await uploadFilesWithAuth(files, props.postId);
  if (!uploadedUrls.length) return;

  // Insert at dragCursorPos or current cursor
  const insertPos = dragCursorPos.value ?? (textarea.value ? textarea.value.selectionStart : editorContent.value.length);
  const urlsMarkdown = uploadedUrls.map(url => `![](${url})`).join('\n');
  insertMarkdownAtCursor(urlsMarkdown, insertPos);
  dragCursorPos.value = null;
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
  let content = editorContent.value
  // Only add dummy line if content ends with a newline or is empty
  if (content === '' || content.endsWith('\n')) {
    content += '\u200B'
  }
  try {
    return hljs.highlight(content, { language: 'markdown' }).value
  } catch (error) {
    return content // fallback to plain text
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
    case 'image':
      replacement = '![](url)'
      cursorOffset = 5 // place cursor inside url
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
        // If no text was selected, place cursor at the url part for image
        if (format === 'image') {
          textarea.value.selectionStart = textarea.value.selectionEnd = start + 4 // after '![]('
        } else {
          textarea.value.selectionStart = textarea.value.selectionEnd = start + cursorOffset
        }
      }
      textarea.value.focus()
    }
  })
}

function applyListFormat(type: 'ordered' | 'unordered' | 'check') {
  if (!textarea.value) return;

  const start = textarea.value.selectionStart;
  const end = textarea.value.selectionEnd;
  const value = editorContent.value;

  // Find the start and end of the selection in terms of lines
  const before = value.slice(0, start);

  // Get the start index of the first selected line
  const lineStart = before.lastIndexOf('\n') + 1;

  // Get all lines in the selection
  const selectedText = value.slice(lineStart, end);
  const lines = selectedText.split('\n');

  // Helper to detect and replace list markers
  function formatLine(line: string, idx: number): string {
    // Remove existing list markers
    let newLine = line.replace(/^\s*([0-9]+\. |- \[.\] |- |\* )/, '');
    switch (type) {
      case 'unordered':
        return `- ${newLine}`;
      case 'ordered':
        return `${idx + 1}. ${newLine}`;
      case 'check':
        return `- [ ] ${newLine}`;
      default:
        return newLine;
    }
  }

  const formattedLines = lines.map(formatLine);
  const newText = value.slice(0, lineStart) + formattedLines.join('\n') + value.slice(end);

  editorContent.value = newText;

  // Restore selection
  nextTick(() => {
    if (textarea.value) {
      textarea.value.selectionStart = lineStart;
      textarea.value.selectionEnd = lineStart + formattedLines.join('\n').length;
      textarea.value.focus();
    }
  });
}

const handlePreviewScroll = (e: Event) => {
  if (isSyncingPreviewScroll) {
    // Ignore scroll events triggered by sync
    isSyncingPreviewScroll = false
    return
  }
  console.log('Preview scroll event triggered')
  const previewEl = e.target as HTMLElement
  const scrollPercentage = getScrollPercentage(previewEl)
  console.log('Preview scroll percentage:', scrollPercentage)
  
  if (textarea.value) {
    const maxScroll = textarea.value.scrollHeight - textarea.value.clientHeight
    isSyncingEditorScroll = true
    textarea.value.scrollTop = scrollPercentage * maxScroll
    // Sync highlight
    const highlight = textarea.value.nextElementSibling as HTMLElement
    if (highlight) {
      highlight.scrollTop = textarea.value.scrollTop
    }
  }
}

const dragCursorStyle = computed((): CSSProperties => {
  if (!textarea.value || dragCursorPos.value === null) return {}
  // Calculate line number and top offset
  const value = editorContent.value
  const before = value.slice(0, dragCursorPos.value)
  const line = before.split('\n').length - 1
  const lineHeight = parseFloat(getComputedStyle(textarea.value).lineHeight || '20')
  return {
    position: 'absolute',
    left: '0',
    right: '0',
    top: `${line * lineHeight}px`,
    height: '2px',
    background: 'var(--p-primary-500)',
    zIndex: 10
  }
})

function handlePaste(e: ClipboardEvent) {
  if (!textarea.value) return;
  const clipboardData = e.clipboardData;
  if (!clipboardData) return;

  const pastedText = clipboardData.getData('text');
  // Only match https URLs
  const urlPattern = /^https:\/\/[^\s]+$/i;

  const start = textarea.value.selectionStart;
  const end = textarea.value.selectionEnd;
  const selectedText = editorContent.value.substring(start, end);

  if (selectedText && urlPattern.test(pastedText.trim())) {
    // Replace selection with markdown link
    e.preventDefault();
    const replacement = `[${selectedText}](${pastedText.trim()})`;
    editorContent.value = editorContent.value.substring(0, start) + replacement + editorContent.value.substring(end);

    // Set cursor after the inserted link
    nextTick(() => {
      textarea.value!.selectionStart = textarea.value!.selectionEnd = start + replacement.length;
      textarea.value!.focus();
    });
  }
}
</script>

<style>
.editor-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;
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
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-content {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: var(--p-surface-50);
  height: 100%;
}
@media (prefers-color-scheme: dark) {
  .editor-content {
    background: var(--p-surface-900);
  }
}

.editor-scroll-area {
  height: 100%;
  display: flex;
  min-height: 0;
}

.editor-container-inner.split-editor,
.split-preview {
  height: 100%;
  min-height: 0;
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

/* All :deep(...) selectors have been removed from this global style block. */
</style>

<style scoped>
/* Import Highlight.js styles */
@import 'highlight.js/styles/github-dark.css';

/* Base styles for code blocks */
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

.split-view {
  display: flex;
  gap: 1rem;
  padding: 1rem;
}

.split-editor {
  position: relative !important;
  flex: 1;
  min-width: 0;
  border: 1px solid var(--p-content-border-color);
  border-radius: 0.5rem;
  background: var(--p-surface-50);
}

.split-preview {
  position: relative !important;
  flex: 1;
  min-width: 0;
  border: 1px solid var(--p-content-border-color);
  border-radius: 0.5rem;
  background: var(--p-surface-50);
}

@media (prefers-color-scheme: dark) {
  .split-editor,
  .split-preview {
    background: var(--p-surface-800);
  }
}

.drag-cursor-indicator {
  pointer-events: none;
  width: 100%;
  background: var(--p-primary-500);
  opacity: 0.7;
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