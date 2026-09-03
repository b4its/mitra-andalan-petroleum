<script setup lang="ts">
const { user, loadUser } = useAuth()

onMounted(() => {
  loadUser()
  // Cegah redirect ke `/undefined` bila role user tidak dikenal/korup.
  if (user.value?.role) {
    navigateTo(`/${user.value.role}`)
  } else {
    navigateTo('/login')
  }
})
</script>

<template>
  <UDashboardPanel id="root">
    <template #header>
      <UDashboardNavbar title="Beranda" :ui="{ right: 'gap-3' }" />
    </template>

    <template #body>
      <h1 class="text-3xl font-bold dark:text-neutral-50 text-neutral-900">
        Dashboard Mitra Andalan Petroleum
      </h1>
    </template>
  </UDashboardPanel>
</template>
