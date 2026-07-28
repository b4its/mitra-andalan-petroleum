<script setup lang="ts">
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps<{
  labels: string[]
  data: number[]
  backgroundColor?: string[]
  title?: string
  height?: number
}>()

const isDark = ref(false)

const defaultColors = [
  'rgba(59, 130, 246, 0.8)',
  'rgba(16, 185, 129, 0.8)',
  'rgba(245, 158, 11, 0.8)',
  'rgba(239, 68, 68, 0.8)',
  'rgba(139, 92, 246, 0.8)'
]

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      data: props.data,
      backgroundColor: props.backgroundColor || defaultColors,
      borderColor: '#ffffff',
      borderWidth: 2,
      hoverOffset: 8
    }
  ]
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '55%',
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: {
        color: isDark.value ? '#94a3b8' : '#64748b',
        padding: 16,
        usePointStyle: true,
        pointStyle: 'circle'
      }
    },
    tooltip: {
      backgroundColor: isDark.value ? '#1e293b' : '#ffffff',
      titleColor: isDark.value ? '#f1f5f9' : '#0f172a',
      bodyColor: isDark.value ? '#cbd5e1' : '#334155',
      borderColor: isDark.value ? '#334155' : '#e2e8f0',
      borderWidth: 1,
      callbacks: {
        label: (ctx: any) => {
          const total = ctx.dataset.data.reduce((a: number, b: number) => a + b, 0)
          const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : '0'
          return ` ${ctx.label}: ${ctx.parsed} (${pct}%)`
        }
      }
    }
  }
}))
</script>

<template>
  <div :style="{ height: (height || 260) + 'px' }" class="w-full">
    <Doughnut :data="chartData" :options="chartOptions" />
  </div>
</template>
