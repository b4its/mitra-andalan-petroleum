<script setup lang="ts">
definePageMeta({ layout: 'finance' })
</script>

<template>
  <UDashboardPanel id="delivery-order">
    <template #header>
      <UDashboardNavbar title="Delivery Order" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-4 lg:p-6">
        <FinanceDOData />
      </div>
    </template>
  </UDashboardPanel>
</template>
