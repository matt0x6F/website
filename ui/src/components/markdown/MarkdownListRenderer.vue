<template>
  <component :is="block.type" :class="listClass">
    <template v-for="(item, idx) in block.items" :key="idx">
      <li v-if="item.type === 'li'">
        <span v-html="item.content"></span>
        <template v-for="(child, cidx) in item.children || []" :key="cidx">
          <MarkdownListRenderer v-if="child.type === 'ul' || child.type === 'ol'" :block="child" :nested="true" />
        </template>
      </li>
      <li v-else-if="item.type === 'task'" class="task-list-item flex flex-col gap-2 min-h-[2rem]">
        <div class="flex items-center gap-2">
          <Checkbox :modelValue="item.checked" :binary="true" disabled class="mr-2" />
          <span class="task-label select-text prose dark:prose-invert" v-html="item.label"></span>
        </div>
        <template v-for="(child, cidx) in item.children || []" :key="cidx">
          <MarkdownListRenderer v-if="child.type === 'ul' || child.type === 'ol'" :block="child" :nested="true" />
        </template>
      </li>
    </template>
  </component>
</template>

<script setup lang="ts">
import { computed, defineProps } from 'vue'
import Checkbox from 'primevue/checkbox'
import TaskListItem from './TaskListItem.vue'
import MarkdownListRenderer from './MarkdownListRenderer.vue'

const props = defineProps<{ block: any, nested?: boolean }>()

const listClass = computed(() => {
  let base = ''
  if (props.block.type === 'ul') {
    base = 'list-disc unpadded-ul'
  } else if (props.block.type === 'ol') {
    base = 'list-decimal unpadded-ol'
  }
  if (props.nested) {
    base += ' nested-list'
  }
  return base
})
</script> 