<script setup lang="ts">
import type { Period, Range, Stat } from "~/types";

const props = defineProps<{
  period: Period;
  range: Range;
}>();

const baseStats = [
  {
    title: "Penawaran yang sudah dibuat",
    icon: "i-lucide-users",
    minValue: 50,
    maxValue: 75,
    minVariation: -15,
    maxVariation: 25,
    to: "/marketing/customer",
  },
  {
    title: "Penawaran yang belum disetujui",
    icon: "i-lucide-clock-fading",
    minValue: 50,
    maxValue: 75,
    minVariation: -10,
    maxVariation: 20,
    to: "/marketing/customer",
  },
  {
    title: "Purchase Order dari Customer",
    icon: "i-lucide-circle-dollar-sign",
    minValue: 50,
    maxValue: 75,
    minVariation: -20,
    maxVariation: 30,
    to: "/marketing/customer",
  },
  {
    title: "Purchase Order untuk logistik",
    icon: "i-lucide-shopping-cart",
    minValue: 50,
    maxValue: 75,
    minVariation: -5,
    maxVariation: 15,
    to: "/marketing/supplier",
  },
];

const { data: stats } = await useAsyncData<Stat[]>(
  "stats",
  async () => {
    return baseStats.map((stat): Stat => {
      const value = randomInt(stat.minValue, stat.maxValue);
      const variation = randomInt(stat.minVariation, stat.maxVariation);

      return {
        title: stat.title,
        icon: stat.icon,
        value: value,
        to: stat.to,
        variation,
      };
    });
  },
  {
    watch: [() => props.period, () => props.range],
    default: () => [],
  },
);
</script>

<template>
  <UPageGrid class="lg:grid-cols-4 gap-4 sm:gap-6 lg:gap-px">
    <UPageCard
      v-for="(stat, index) in stats"
      :key="index"
      :icon="stat.icon"
      :title="stat.title"
      :to="stat.to"
      variant="subtle"
      :ui="{
        container: 'gap-y-1.5',
        wrapper: 'items-start',
        leading:
          'p-2.5 rounded-full bg-primary/10 ring ring-inset ring-primary/25 flex-col',
        title: 'font-normal text-muted text-xs uppercase',
      }"
      class="lg:rounded-none first:rounded-l-lg last:rounded-r-lg hover:z-1"
    >
      <div class="flex items-center gap-2">
        <span class="text-2xl font-semibold text-highlighted">
          {{ stat.value }}
        </span>
      </div>
    </UPageCard>
  </UPageGrid>
</template>
