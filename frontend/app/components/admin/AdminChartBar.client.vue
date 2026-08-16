<script setup lang="ts">
import { VisXYContainer, VisGroupedBar, VisAxis, VisTooltip } from '@unovis/vue'

defineProps<{
  data: {
    month: string
    offering_letters: number
    purchase_orders: number
    delivery_orders: number
    invoices: number
  }[]
}>()

const categories = ['offering_letters', 'purchase_orders', 'delivery_orders', 'invoices'] as const
const colors = ['var(--ui-primary)', 'var(--ui-info)', 'var(--ui-warning)', 'var(--ui-success)']
const labels: Record<string, string> = {
  offering_letters: 'Surat Penawaran',
  purchase_orders: 'Purchase Order',
  delivery_orders: 'Delivery Order',
  invoices: 'Invoice'
}

interface ChartDatum {
  month?: string
  offering_letters?: number
  purchase_orders?: number
  delivery_orders?: number
  invoices?: number
}

const xAccessor = (_d: ChartDatum, i: number) => i
const yAccessors = categories.map(cat => (d: ChartDatum) => (d[cat] as number) ?? 0)
const colorAccessor = (_d: ChartDatum, i: number) => colors[i % colors.length]

function tickFormat(d: ChartDatum): string {
  return d.month?.split(' ')[0] ?? ''
}

function tooltipTemplate(d: unknown, _i: number, cat: string): string {
  const label = labels[cat] || cat
  return `${label}: ${d}`
}
</script>

<template>
  <UCard :ui="{ body: 'px-0! pt-0! pb-3!' }">
    <template #header>
      <p class="text-xs text-muted uppercase mb-1.5">
        Tren Bulanan
      </p>
      <div class="flex flex-wrap gap-4 text-xs text-muted">
        <span v-for="(cat, i) in categories" :key="cat" class="flex items-center gap-1">
          <span class="inline-block size-2.5 rounded-full" :style="{ background: colors[i] }" />
          {{ labels[cat] }}
        </span>
      </div>
    </template>

    <VisXYContainer
      :data="data"
      :padding="{ top: 20, bottom: 20, left: 40, right: 16 }"
      :height="320"
      class="w-full"
    >
      <VisGroupedBar
        :x="xAccessor"
        :y="yAccessors"
        :color="colorAccessor"
        :bar-padding="0.1"
        :group-padding="0.2"
      />
      <VisAxis
        type="x"
        :x="xAccessor"
        :tick-format="tickFormat"
        :num-ticks="data.length"
      />
      <VisAxis type="y" :grid-line="true" />
      <VisTooltip :template="tooltipTemplate" />
    </VisXYContainer>
  </UCard>
</template>

<style scoped>
.unovis-xy-container {
  --vis-crosshair-line-stroke-color: var(--ui-primary);
  --vis-crosshair-circle-stroke-color: var(--ui-bg);
  --vis-axis-grid-color: var(--ui-border);
  --vis-axis-tick-color: var(--ui-border);
  --vis-axis-tick-label-color: var(--ui-text-dimmed);
  --vis-tooltip-background-color: var(--ui-bg);
  --vis-tooltip-border-color: var(--ui-border);
  --vis-tooltip-text-color: var(--ui-text-highlighted);
  --vis-grouped-bar-cursor: default;
}
</style>
