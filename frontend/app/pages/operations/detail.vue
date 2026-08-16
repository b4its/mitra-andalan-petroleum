<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const route = useRoute()
const idLetter = route.params.id

const links = [
  [
    {
      label: 'Detail Surat Delivery Order',
      icon: 'i-lucide-truck',
      to: `/operations/detail/delivery-order-${idLetter}`
    }
  ]
] satisfies NavigationMenuItem[][]

definePageMeta({ layout: 'operations' })
</script>

<template>
  <UDashboardPanel id="delivery-order" :ui="{ body: 'lg:py-12' }">
    <template #header>
      <UDashboardNavbar :title="`Surat Delivery Order ${idLetter}`">
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
