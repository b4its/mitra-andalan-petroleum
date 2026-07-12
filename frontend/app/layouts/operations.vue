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
      to: "/finance",
      onSelect: () => {
        open.value = false;
      },
    },
    {
      label: "Manajemen Harga",
      icon: "i-lucide-banknote",
      defaultOpen: true,
      children: [
        {
          label: "Harga Solar",
          to: "/finance/harga/solar",
          exact: true,
          onSelect: () => {
            open.value = false;
          },
        },
        {
          label: "Harga Pengiriman",
          to: "/finance/harga/pengiriman",
          onSelect: () => {
            open.value = false;
          },
        },
      ],
    },
    {
      label: "Customer",
      icon: "i-lucide-users",

      defaultOpen: true,
      children: [
        {
          label: "Penawaran Customer",
          to: "/finance/customer/penawaran",
          exact: true,
          onSelect: () => {
            open.value = false;
          },
        },
        {
          label: "PO Customer",
          to: "/finance/customer/po",
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
          label: "PO Supplier",
          to: "/finance/supplier/po",
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
