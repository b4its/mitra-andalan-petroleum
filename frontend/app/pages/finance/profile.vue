<script setup lang="ts">
definePageMeta({ layout: 'finance' })
</script>

<template>
  <UDashboardPanel id="finance-profile">
    <template #header>
      <UDashboardNavbar title="Profil">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-4 lg:p-6">
        <ProfilePageForm />
      </div>
    </template>
  </UDashboardPanel>
</template>
