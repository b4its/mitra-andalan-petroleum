<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";

const route = useRoute();
const idPoLetter = route.params.id;

const links = [
  [
    {
      label: "Detail Purchase Order Supplier",
      icon: "i-lucide-receipt-text",
      to: `/marketing/detail-supplier/po-supplier-${idPoLetter}`,
    },
  ],
] satisfies NavigationMenuItem[][];

definePageMeta({ layout: "marketing" });
</script>

<template>
  <UDashboardPanel id="po-supplier" :ui="{ body: 'lg:py-12' }">
    <template #header>
      <UDashboardNavbar :title="`Purchase Order Supplier ${idPoLetter}`"">
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
      <div class="flex flex-col gap-4 sm:gap-6 lg:gap-12 w-full">
        <NuxtPage />
      </div>
    </template>
  </UDashboardPanel>
</template>
