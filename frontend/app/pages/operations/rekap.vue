<script setup lang="ts">
definePageMeta({ layout: "operations" });
</script>

<template>
  <UDashboardPanel id="rekap">
    <template #header>
      <UDashboardNavbar
        title="Rekap Data Delivery Order"
        :ui="{ right: 'gap-3' }"
      >
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <OperationsDOData />
    </template>
  </UDashboardPanel>
</template>
