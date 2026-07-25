<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";

const route = useRoute();
const toast = useToast();

const open = ref(false);

const links = [
  [
    {
      label: "Beranda",
      icon: "i-lucide-house",
      to: "/operations",
      onSelect: () => {
        open.value = false;
      },
    },
    {
      label: "Delivery Order",
      icon: "i-lucide-truck",
      to: "/operations/delivery-order",
      onSelect: () => {
        open.value = false;
      },
    },
    {
      label: "Rekap Data Delivery Order",
      icon: "i-lucide-square-chart-gantt",
      to: "/operations/rekap",
      onSelect: () => {
        open.value = false;
      },
    },
  ],
] satisfies NavigationMenuItem[][];
</script>

<template>
  <UDashboardGroup unit="rem">
    <UDashboardSidebar
      id="default"
      v-model:open="open"
      collapsible
      resizable
      class="bg-elevated/25"
      :ui="{ footer: 'lg:border-t lg:border-default' }"
    >
      <template #header="{ collapsed }">
        <UserMenu :collapsed="collapsed" />
      </template>

      <template #default="{ collapsed }">
        <UNavigationMenu
          :collapsed="collapsed"
          :items="links[0]"
          orientation="vertical"
          tooltip
          popover
        />
      </template>
    </UDashboardSidebar>

    <slot />
  </UDashboardGroup>
</template>
