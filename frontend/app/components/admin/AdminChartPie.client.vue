<script setup lang="ts">
import { VisSingleContainer, VisDonut, VisTooltip } from '@unovis/vue'

defineProps<{
  olDistribution: { label: string, value: number }[]
  poDistribution: { label: string, value: number }[]
  doDistribution: { label: string, value: number }[]
  invoiceDistribution: { label: string, value: number }[]
}>()

const colorPalette = [
  'var(--ui-primary)',
  'var(--ui-info)',
  'var(--ui-warning)',
  'var(--ui-success)',
  'var(--ui-error)'
]

interface ChartDatum {
  label?: string
  value?: number
}

function valueAccessor(d: ChartDatum): number {
  return d.value ?? 0
}

function colorAccessor(_d: ChartDatum, i: number): string {
  return colorPalette[i % colorPalette.length] ?? 'var(--ui-primary)'
}

function tooltipTemplate(d: ChartDatum): string {
  return `${d.label}: ${d.value}`
}

function totalSum(arr: ChartDatum[]): string {
  return String(arr.reduce((a: number, b: ChartDatum) => a + (b.value ?? 0), 0))
}
</script>

<template>
  <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
    <UCard>
      <template #header>
        <p class="text-xs text-muted uppercase">
          Status Surat Penawaran
        </p>
      </template>
      <VisSingleContainer :data="olDistribution" :height="240" :margin="{ top: 20, bottom: 20, left: 20, right: 20 }">
        <VisDonut
          :value="valueAccessor"
          :color="colorAccessor"
          :central-label="totalSum(olDistribution)"
          central-sub-label="Total"
          :arc-width="32"
        />
        <VisTooltip :template="tooltipTemplate" />
      </VisSingleContainer>
    </UCard>

    <UCard>
      <template #header>
        <p class="text-xs text-muted uppercase">
          Tipe Purchase Order
        </p>
      </template>
      <VisSingleContainer :data="poDistribution" :height="240" :margin="{ top: 20, bottom: 20, left: 20, right: 20 }">
        <VisDonut
          :value="valueAccessor"
          :color="colorAccessor"
          :central-label="totalSum(poDistribution)"
          central-sub-label="Total"
          :arc-width="32"
        />
        <VisTooltip :template="tooltipTemplate" />
      </VisSingleContainer>
    </UCard>

    <UCard>
      <template #header>
        <p class="text-xs text-muted uppercase">
          Status Delivery Order
        </p>
      </template>
      <VisSingleContainer :data="doDistribution" :height="240" :margin="{ top: 20, bottom: 20, left: 20, right: 20 }">
        <VisDonut
          :value="valueAccessor"
          :color="colorAccessor"
          :central-label="totalSum(doDistribution)"
          central-sub-label="Total"
          :arc-width="32"
        />
        <VisTooltip :template="tooltipTemplate" />
      </VisSingleContainer>
    </UCard>

    <UCard>
      <template #header>
        <p class="text-xs text-muted uppercase">
          Status Invoice
        </p>
      </template>
      <VisSingleContainer :data="invoiceDistribution" :height="240" :margin="{ top: 20, bottom: 20, left: 20, right: 20 }">
        <VisDonut
          :value="valueAccessor"
          :color="colorAccessor"
          :central-label="totalSum(invoiceDistribution)"
          central-sub-label="Total"
          :arc-width="32"
        />
        <VisTooltip :template="tooltipTemplate" />
      </VisSingleContainer>
    </UCard>
  </div>
</template>

<style scoped>
.unovis-single-container {
  --vis-donut-central-label-color: var(--ui-text-highlighted);
  --vis-donut-central-sub-label-color: var(--ui-text-dimmed);
  --vis-tooltip-background-color: var(--ui-bg);
  --vis-tooltip-border-color: var(--ui-border);
  --vis-tooltip-text-color: var(--ui-text-highlighted);
}
</style>
