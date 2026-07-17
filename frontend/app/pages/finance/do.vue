<script setup lang="ts">
definePageMeta({ layout: "finance" });
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
      <FinanceDOData />
    </template>
  </UDashboardPanel>
</template>
