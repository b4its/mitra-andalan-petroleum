<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const links = [
  [
    {
      label: 'Rekap',
      icon: 'i-lucide-square-chart-gantt',
      to: '/marketing/customer',
      exact: true
    },
    {
      label: 'Surat Penawaran Customer',
      icon: 'i-lucide-file-user',
      to: '/marketing/customer/penawaran'
    },
    {
      label: 'Purchase Order Customer',
      icon: 'i-lucide-receipt-text',
      to: '/marketing/customer/po'
    }
  ]
] satisfies NavigationMenuItem[][]

definePageMeta({ layout: 'marketing' })
</script>

<template>
  <UDashboardPanel id="customer" :ui="{ body: 'lg:py-12' }">
    <template #header>
      <UDashboardNavbar title="Customer">
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
