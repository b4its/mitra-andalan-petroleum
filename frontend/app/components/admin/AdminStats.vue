<script setup lang="ts">
defineProps<{
  stats: {
    title: string
    icon: string
    value: number | string
    to: string
  }[]
}>()

function displayValue(stat: { title: string, value: number | string }): string {
  if (stat.title === 'Total Revenue' && typeof stat.value === 'number') {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(stat.value)
  }
  return String(stat.value)
}
</script>

<template>
  <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
    <UCard
      v-for="(stat, index) in stats"
      :key="index"
      variant="subtle"
      class="hover:z-1"
    >
      <template #header>
        <div class="flex items-center gap-2">
          <div class="p-2.5 rounded-full bg-primary/10 ring ring-inset ring-primary/25">
            <UIcon :name="stat.icon" class="size-5 text-primary" />
          </div>
          <p class="truncate font-normal text-muted text-xs uppercase">
            {{ stat.title }}
          </p>
        </div>
      </template>
      <span class="text-2xl font-semibold text-highlighted">
        {{ displayValue(stat) }}
      </span>
    </UCard>
  </div>
</template>
