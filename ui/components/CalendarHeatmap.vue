<template>
  <div class="relative w-full flex flex-col items-center">
    <svg
      :width="svgWidth"
      :height="svgHeight + 24"
      class="block"
      @mouseleave="hideTooltip"
    >
      <!-- Heatmap squares -->
      <g>
        <rect
          v-for="(day, idx) in days"
          :key="day.date"
          :x="getWeekIndex(day.date, daysArr[0].date) * (cellSize + cellGap) + leftMargin"
          :y="(6 - getDayOfWeek(day)) * (cellSize + cellGap)"
          :width="cellSize"
          :height="cellSize"
          :fill="getColor(day.count)"
          rx="3"
          ry="3"
          class="cursor-pointer transition-all duration-150"
          @mouseenter="showTooltip(day, $event)"
          @mouseleave="hideTooltip"
          @click="selectDay(day)"
        />
      </g>
      <!-- Month labels at the bottom -->
      <g>
        <text
          v-for="label in monthLabels"
          :key="label.name + label.x"
          :x="label.x"
          :y="svgHeight + 16"
          text-anchor="middle"
          class="fill-slate-500 dark:fill-slate-400 text-xs select-none"
        >
          {{ label.name }}
        </text>
      </g>
      <!-- Day of week labels on the left -->
      <g>
        <text
          v-for="(d, i) in daysOfWeek"
          :key="d"
          :x="leftMargin - 4"
          :y="i * (cellSize + cellGap) + cellSize / 1.5"
          text-anchor="end"
          class="fill-slate-500 dark:fill-slate-400 text-xs select-none"
        >
          {{ d }}
        </text>
      </g>
    </svg>
    <div
      v-if="tooltip.visible"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
      class="pointer-events-none absolute z-10 px-3 py-2 rounded shadow-lg text-xs bg-slate-800 dark:bg-slate-900 text-white whitespace-nowrap"
    >
      <span v-if="tooltip.day">
        <strong>{{ tooltip.day.date }}</strong><br />
        {{ tooltip.day.count }} post{{ tooltip.day.count === 1 ? '' : 's' }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Ref, PropType } from 'vue'
import { getWeekIndex } from './calendarUtils'
import { useDark } from '@vueuse/core'

interface HeatmapDay {
  date: string // 'YYYY-MM-DD'
  count: number
}

const props = defineProps({
  data: {
    type: Array as PropType<HeatmapDay[]>,
    required: true
  },
  year: {
    type: Number,
    required: false,
    default: () => new Date().getFullYear()
  },
  today: {
    type: String,
    required: false,
    default: () => new Date().toISOString().slice(0, 10)
  }
})

const cellSize = 16
const cellGap = 2
const daysInWeek = 7

const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

// Build a map for quick lookup
const dataMap = computed(() => {
  const map: Record<string, number> = {}
  for (const d of props.data) {
    map[d.date] = d.count
  }
  return map
})

// Get the last 52 weeks, always starting on a Sunday
function getLast52Weeks() {
  const days: { date: string; count: number }[] = [];
  const today = new Date(props.today + 'T00:00:00Z');

  // Find the most recent Sunday (today if today is Sunday)
  const lastSunday = new Date(today);
  lastSunday.setDate(today.getDate() - today.getDay());

  // Go back 51 more Sundays to get 52 weeks
  const firstSunday = new Date(lastSunday);
  firstSunday.setDate(lastSunday.getDate() - 7 * 51);

  // Fill days from firstSunday to lastSunday (inclusive)
  for (let i = 0; i < 52 * 7; i++) {
    const d = new Date(firstSunday);
    d.setDate(firstSunday.getDate() + i);
    const dateStr = d.toISOString().slice(0, 10);
    days.push({
      date: dateStr,
      count: dataMap.value[dateStr] || 0
    });
  }
  return days;
}

const days = computed(() => getLast52Weeks())

const daysArr = computed(() => days.value)

// Get day of week (0 = Sunday)
function getDayOfWeek(day: { date: string }) {
  return new Date(day.date + 'T00:00:00Z').getDay()
}

const leftMargin = 32

// Month labels logic
const monthLabels = computed(() => {
  const labels: { name: string; x: number }[] = []
  let lastMonth = ''
  let lastX = -Infinity
  let pendingLabel: { name: string; x: number } | null = null
  for (const day of days.value) {
    const dateObj = new Date(day.date)
    const month = dateObj.toLocaleString('default', { month: 'short' })
    if (month !== lastMonth) {
      // Center label under the week column
      const weekIdx = getWeekIndex(day.date, days.value[0].date)
      const x = weekIdx * (cellSize + cellGap) + cellSize / 2 + leftMargin
      if (x - lastX < 32 && labels.length > 0) {
        // Overlap: remove previous and keep this one (the more recent month)
        labels.pop()
      }
      labels.push({ name: month, x })
      lastX = x
      lastMonth = month
    }
  }
  return labels
})

const svgWidth = computed(() => {
  // Always 52 columns
  return leftMargin + 52 * (cellSize + cellGap)
})
const svgHeight = computed(() => daysInWeek * (cellSize + cellGap))

const isDark = useDark()

// Color scale (simple 5-step)
function getColor(count: number) {
  if (!count) return isDark.value ? '#1e293b' : '#e5e7eb'
  if (count < 2) return '#bbf7d0' // green-200
  if (count < 4) return '#4ade80' // green-400
  if (count < 7) return '#22c55e' // green-500
  return '#166534' // green-900
}

// Tooltip logic
const tooltip: Ref<{ visible: boolean; x: number; y: number; day: null | HeatmapDay }> = ref({ visible: false, x: 0, y: 0, day: null })
function showTooltip(day: HeatmapDay, evt: MouseEvent) {
  if (!day.date) return
  tooltip.value = {
    visible: true,
    x: evt.offsetX + 20,
    y: evt.offsetY,
    day
  }
}
function hideTooltip() {
  tooltip.value.visible = false
}

// Emit event on cell click
const emit = defineEmits(['select'])
function selectDay(day: HeatmapDay) {
  if (!day.date) return
  emit('select', day)
}
</script> 