<script setup lang="ts">
import { Bar } from "vue-chartjs"
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js"

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const props = defineProps<{
  labels: string[]
  datasets: {
    label: string
    data: number[]
    backgroundColor?: string
    borderColor?: string
  }[]
  title?: string
  height?: number
}>()

const isDark = ref(false)

const chartData = computed(() => ({
  labels: props.labels,
  datasets: props.datasets.map((ds) => ({
    ...ds,
    backgroundColor: ds.backgroundColor || "rgba(59, 130, 246, 0.7)",
    borderColor: ds.borderColor || "rgb(59, 130, 246)",
    borderWidth: 1,
  })),
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: props.datasets.length > 1 },
    title: { display: false },
    tooltip: {
      backgroundColor: isDark.value ? "#1e293b" : "#ffffff",
      titleColor: isDark.value ? "#f1f5f9" : "#0f172a",
      bodyColor: isDark.value ? "#cbd5e1" : "#334155",
      borderColor: isDark.value ? "#334155" : "#e2e8f0",
      borderWidth: 1,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        stepSize: 1,
        color: isDark.value ? "#94a3b8" : "#64748b",
      },
      grid: { color: isDark.value ? "rgba(148,163,184,0.1)" : "rgba(100,116,139,0.1)" },
    },
    x: {
      ticks: { color: isDark.value ? "#94a3b8" : "#64748b" },
      grid: { display: false },
    },
  },
}))
</script>

<template>
  <div :style="{ height: (height || 280) + 'px' }" class="w-full">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>
