<script setup lang="ts">
definePageMeta({ layout: 'operations' })
</script>

<template>
  <UDashboardPanel id="operations-profile">
    <template #header>
      <UDashboardNavbar title="Profil">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-4 lg:p-6">
        <ProfilePageForm :show-toast-title="false" />
      </div>
    </template>
  </UDashboardPanel>
</template>
