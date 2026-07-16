<script setup lang="ts">
import { sub } from "date-fns";
import type { DropdownMenuItem } from "@nuxt/ui";
import type { Period, Range } from "~/types";

const { isNotificationsSlideoverOpen } = useDashboard();

const items = [
  [
    {
      label: "New mail",
      icon: "i-lucide-send",
      to: "/inbox",
    },
    {
      label: "New customer",
      icon: "i-lucide-user-plus",
      to: "/customers",
    },
  ],
] satisfies DropdownMenuItem[][];

const range = shallowRef<Range>({
  start: sub(new Date(), { days: 14 }),
  end: new Date(),
});
const period = ref<Period>("daily");

definePageMeta({ layout: "operations" });
</script>

<template>
  <UDashboardPanel id="rekap">
    <template #header>
      <UDashboardNavbar
        title="Rekap Data Delivery Order"
        :ui="{ right: 'gap-3' }"
      >
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>

      <!-- <UDashboardToolbar>
        <template #left>
           NOTE: The `-ms-1` class is used to align with the `DashboardSidebarCollapse` button here. 
          <HomeDateRangePicker v-model="range" class="-ms-1" />

          <HomePeriodSelect v-model="period" :range="range" />
        </template>
      </UDashboardToolbar> -->
    </template>

    <template #body>
      <OperationsDOData />
    </template>
  </UDashboardPanel>
</template>
