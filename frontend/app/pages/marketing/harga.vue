<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";

const links = [
  [
    {
      label: "Rekap",
      icon: "i-lucide-square-chart-gantt",
      to: "/marketing/harga",
      exact: true,
    },
    {
      label: "Harga Solar",
      icon: "i-lucide-fuel",
      to: "/marketing/harga/solar",
    },
    {
      label: "Harga Pengiriman",
      icon: "i-lucide-truck",
      to: "/marketing/harga/pengiriman",
    },
  ],
] satisfies NavigationMenuItem[][];

definePageMeta({ layout: "marketing" });
</script>

<template>
  <UDashboardPanel id="manajemen-harga" :ui="{ body: 'lg:py-12' }">
    <template #header>
      <UDashboardNavbar title="Manajemen Harga">
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
      <div
        class="flex flex-col gap-4 sm:gap-6 lg:gap-12 w-full lg:max-w-7xl mx-auto"
      >
        <NuxtPage />
      </div>
    </template>
  </UDashboardPanel>
</template>
