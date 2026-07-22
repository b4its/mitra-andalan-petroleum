<script setup lang="ts">
const { user, loadUser } = useAuth();

onMounted(() => {
  loadUser();
  if (user.value) {
    navigateTo(`/${user.value.role}`);
  } else {
    navigateTo("/login");
  }
});
</script>

<template>
  <UDashboardPanel id="root">
    <template #header>
      <UDashboardNavbar title="Beranda" :ui="{ right: 'gap-3' }">
      </UDashboardNavbar>
    </template>

    <template #body>
      <h1 class="text-3xl font-bold dark:text-neutral-50 text-neutral-900">
        Dashboard Mitra Andalan Petroleum
      </h1>
    </template>
  </UDashboardPanel>
</template>
