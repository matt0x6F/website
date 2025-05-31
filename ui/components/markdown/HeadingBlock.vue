<template>
  <component :is="tag" v-html="content"></component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ level: number, content: string }>()
const tag = computed(() => `h${props.level}`)
</script> 