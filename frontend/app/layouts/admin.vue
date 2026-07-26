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
      to: "/marketing",
      onSelect: () => {
        open.value = false;
      },
    },
    {
      label: "Marketing",
      icon: "i-lucide-flag-triangle-right",

      defaultOpen: true,
      children: [
        {
          label: "Rekap Keseluruhan",
          to: "/",
          exact: true,
          onSelect: () => {
            open.value = false;
          },
        },
        {
          label: "Data Surat Penawaran",
          to: "/",
          exact: true,
          onSelect: () => {
            open.value = false;
          },
        },
        {
          label: "Data Purchase Order Customer",
          to: "/",
          exact: true,
          onSelect: () => {
            open.value = false;
          },
        },
        {
          label: "Data Purchase Order Supplier",
          to: "/",
          exact: true,
          onSelect: () => {
            open.value = false;
          },
        },
      ],
    },
    {
      label: "Operations",
      icon: "i-lucide-truck",

      defaultOpen: true,
      children: [
        {
          label: "Rekap Keseluruhan",
          to: "/",
          exact: true,
          onSelect: () => {
            open.value = false;
          },
        },
        {
          label: "Data Delivery Order",
          to: "/",
          exact: true,
          onSelect: () => {
            open.value = false;
          },
        },
      ],
    },
    {
      label: "Finance",
      icon: "i-lucide-receipt-text",

      defaultOpen: true,
      children: [
        {
          label: "Rekap Keseluruhan",
          to: "/",
          exact: true,
          onSelect: () => {
            open.value = false;
          },
        },
        {
          label: "Data Invoice",
          to: "/",
          exact: true,
          onSelect: () => {
            open.value = false;
          },
        },
      ],
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

    <!-- <NotificationsSlideover /> -->
  </UDashboardGroup>
</template>
