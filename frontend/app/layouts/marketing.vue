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
      label: "Customer",
      icon: "i-lucide-users",

      defaultOpen: true,
      children: [
        {
          label: "Rekap",
          to: "/marketing/customer",
          exact: true,
          onSelect: () => {
            open.value = false;
          },
        },
        {
          label: "Surat Penawaran Customer",
          to: "/marketing/customer/penawaran",
          exact: true,
          onSelect: () => {
            open.value = false;
          },
        },
        {
          label: "Purchase Order Customer",
          to: "/marketing/customer/po",
          onSelect: () => {
            open.value = false;
          },
        },
      ],
    },
    {
      label: "Supplier",
      icon: "i-lucide-truck",

      defaultOpen: true,
      children: [
        {
          label: "Rekap",
          to: "/marketing/supplier",
          exact: true,
        },
        {
          label: "PO Supplier",
          to: "/marketing/supplier/po",
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

    <NotificationsSlideover />
  </UDashboardGroup>
</template>
