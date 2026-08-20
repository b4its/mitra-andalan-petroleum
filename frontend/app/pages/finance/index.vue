<script setup lang="ts">
import { sub } from "date-fns";
import type { Period, RangeDate } from "~/types";

const range = shallowRef<RangeDate>({
  start: sub(new Date(), { days: 14 }),
  end: new Date(),
});
const period = ref<Period>("daily");

definePageMeta({ layout: "finance" });
</script>

<template>
  <UDashboardPanel id="home">
    <template #header>
      <UDashboardNavbar title="Beranda" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-4 lg:p-6 space-y-6">
        <h1 class="text-3xl font-bold dark:text-neutral-50 text-neutral-900">
          Rekap Data Finance
        </h1>
        <FinanceStats :period="period" :range="range" />
      </div>
    </template>
  </UDashboardPanel>
</template>
