<template>
  <component
    :is="ordered ? 'ol' : 'ul'"
    :start="ordered ? start : undefined"
    :class="ordered ? 'list-inside pl-6 my-5' : 'list-outside pl-4 my-5'"
  >
    <template v-for="(item, i) in items" :key="i">
      <li v-if="item.type === 'list_item'">
        <span v-html="item.content"></span>
        <template v-if="item.children">
          <ListBlock v-for="(child, j) in item.children" :key="j" :ordered="child.ordered" :start="child.start" :items="child.items" />
        </template>
      </li>
      <li v-else-if="item.type === 'task'" class="no-marker">
        <TaskListItem :modelValue="item.checked" :label="item.label" :unordered="!ordered" />
      </li>
    </template>
  </component>
</template>

<script setup lang="ts">
import ListBlock from './ListBlock.vue'
import TaskListItem from './TaskListItem.vue'
const props = defineProps<{ ordered: boolean, start?: number, items: any[] }>()
</script>

<style scoped>
li.no-marker {
  list-style-type: none !important;
  display: flex;
  align-items: center;
}
</style> 