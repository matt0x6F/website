<template>
  <ol class="list-decimal list-inside pl-6 my-5" :start="start">
    <template v-for="(item, i) in items" :key="i">
      <li class="my-2" v-html="item.content"></li>
    </template>
  </ol>
</template>

<script setup lang="ts">
defineProps<{
  items: { content: string }[];
  start?: number;
}>();
</script>

<style lang="postcss">
/* Handle nested lists - these styles can't be done with single Tailwind classes */
.list-decimal ol {
  @apply list-[lower-alpha] mt-2 mb-2;
}

.list-decimal ol ol {
  @apply list-[lower-roman];
}
</style> 