<template>
  <blockquote>
    <template v-for="(block, i) in blocks" :key="i">
      <HeadingBlock v-if="block.type === 'heading'" :level="block.level" :content="block.content" />
      <ParagraphBlock v-else-if="block.type === 'paragraph'" :content="block.content" />
      <ListBlock v-else-if="block.type === 'list'" :ordered="block.ordered" :start="block.start" :items="block.items" />
      <BlockquoteBlock v-else-if="block.type === 'blockquote'" :blocks="block.content" />
      <!-- Add other block types as needed -->
    </template>
  </blockquote>
</template>

<script setup lang="ts">
import HeadingBlock from './HeadingBlock.vue'
import ParagraphBlock from './ParagraphBlock.vue'
import ListBlock from './ListBlock.vue'
import BlockquoteBlock from './BlockquoteBlock.vue'
const props = defineProps<{ blocks: any[] }>()
</script> 