<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'
import type { PurchaseOrdersDetails } from '~/types/marketing'

const route = useRoute()
const idPoLetter = route.params.id
const { get } = useApi()

const { data: purchaseOrderDetails, pending } = await useAsyncData('purchase-order-detail-supplier', async () => {
  const res = await get<PurchaseOrdersDetails>(`/purchase-orders/${idPoLetter}`)
  return res
})

const links = [
  [
    {
      label: 'Detail Purchase Order Supplier',
      icon: 'i-lucide-receipt-text',
      to: `/marketing/detail-supplier/po-supplier-${idPoLetter}`
    }
  ]
] satisfies NavigationMenuItem[][]

definePageMeta({ layout: 'marketing' })
</script>

<template>
  <UDashboardPanel id="po-supplier" :ui="{ body: 'lg:py-12' }">
    <template #header>
      <UDashboardNavbar :title="pending ? `Purchase Order Supplier (…)` : `Purchase Order Supplier (${purchaseOrderDetails?.po_number}) | ${purchaseOrderDetails?.supplier_name}`">
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
      <div v-if="pending" class="flex flex-col gap-4 w-full px-4 lg:px-6">
        <div class="space-y-3">
          <USkeleton v-for="i in 6" :key="i" class="h-12 rounded-lg" />
        </div>
      </div>
      <div v-else class="flex flex-col gap-4 sm:gap-6 lg:gap-12 w-full px-4 lg:px-6">
        <NuxtPage />
      </div>
    </template>
  </UDashboardPanel>
</template>
