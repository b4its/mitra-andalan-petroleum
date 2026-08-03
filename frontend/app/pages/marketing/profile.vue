<script setup lang="ts">
definePageMeta({ layout: 'marketing' })
</script>

<template>
  <UDashboardPanel id="marketing-profile">
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
