<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";

const route = useRoute();
const idOfferingLetter = route.params.id;

const links = [
  [
    {
      label: "Revisi Surat Penawaran Customer",
      icon: "i-lucide-file-user",
      to: `/marketing/detail/revisi-surat-penawaran-${idOfferingLetter}`,
    },
    {
      label: "Detail Surat Penawaran Customer",
      icon: "i-lucide-receipt-text",
      to: `/marketing/detail/surat-penawaran-${idOfferingLetter}`,
    },
  ],
] satisfies NavigationMenuItem[][];

definePageMeta({ layout: "marketing" });
</script>

<template>
  <UDashboardPanel id="offering-letter" :ui="{ body: 'lg:py-12' }">
    <template #header>
      <UDashboardNavbar :title="`Surat Penawaran Customer ${idOfferingLetter}`"">
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
