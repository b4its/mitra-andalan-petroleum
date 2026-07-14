<script setup lang="ts">
import { sub } from "date-fns";
import type { Period, Range } from "~/types";

const range = shallowRef<Range>({
  start: sub(new Date(), { days: 14 }),
  end: new Date(),
});
const period = ref<Period>("daily");

definePageMeta({ layout: "marketing" });
</script>

<template>
  <h1 class="text-3xl font-bold text-neutral-50">
    Rekap Histori Surat Penawaran Customer
  </h1>
  <MarketingOLData :period="period" :range="range" />
</template>
