<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";

const route = useRoute();
const idInvoice = route.params.id;

const links = [
  [
    {
      label: "Detail Invoice Customer",
      icon: "i-lucide-receipt",
      to: `/finance/detail/invoice-${idInvoice}`,
    },
  ],
] satisfies NavigationMenuItem[][];

definePageMeta({ layout: "finance" });
</script>

<template>
  <UDashboardPanel id="detail-invoice" :ui="{ body: 'lg:py-12' }">
    <template #header>
      <UDashboardNavbar :title="`Invoice ${idInvoice}`"">
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
