<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";
import type { PoTransportirsDetails } from "~/types/operations";

const route = useRoute();
const idPoTransportLetter = route.params.id;
const { get } = useApi();

const { data: poData, pending } =
  await useAsyncData<PoTransportirsDetails | null>(
    "po-transportir-details",
    async () => {
      const res = await get<PoTransportirsDetails>(
        `/po-transportir/${idPoTransportLetter}`,
      );
      return res;
    },
    { default: () => null, server: false },
  );

const details = computed<PoTransportirsDetails["details"] | null>(
  () => poData.value?.details ?? null,
);

const links = [
  [
    {
      label: "Detail PO Transportir",
      icon: "i-lucide-warehouse",
      to: `/operations/detail-transport/po-transportir-${idPoTransportLetter}`,
    },
  ],
] satisfies NavigationMenuItem[][];

definePageMeta({ layout: "operations" });
</script>

<template>
  <UDashboardPanel id="po-transport" :ui="{ body: 'lg:py-12' }">
    <template #header>
      <UDashboardNavbar
        :title="`PO Transportir (${details?.poTransportNumber})`"
      >
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>

      <UDashboardToolbar>
        <!-- NOTE: The `-mx-1` class is used to align with the `DashboardSidebarCollapse` button here. -->
        <UNavigationMenu :items="links" highlight class="-mx-1 flex-1" />
      </UDashboardToolbar>
    </template>

    <template #body>
      <div class="flex flex-col gap-4 sm:gap-6 lg:gap-12 w-full px-4 lg:px-6">
        <NuxtPage />
      </div>
    </template>
  </UDashboardPanel>
</template>
