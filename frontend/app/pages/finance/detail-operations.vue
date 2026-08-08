<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const route = useRoute()
const idDoLetter = route.params.id

const links = [
  [
    {
      label: 'Detail Delivery Order',
      icon: 'i-lucide-receipt',
      to: `/finance/detail-operations/delivery-order-${idDoLetter}`
    }
  ]
] satisfies NavigationMenuItem[][]

definePageMeta({ layout: 'finance' })
</script>

<template>
  <UDashboardPanel id="detail-delivery-order" :ui="{ body: 'lg:py-12' }">
    <template #header>
      <UDashboardNavbar :title="`Delivery Order ${idDoLetter}`"">
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
