<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const open = ref(false)

const { user } = useAuth()
const isAdmin = computed(() => user.value?.role === 'admin')

const links = computed<NavigationMenuItem[][]>(() => {
  const items: NavigationMenuItem[] = []

  // Jika admin yang sedang mengakses halaman operations, tambah link kembali ke admin
  if (isAdmin.value) {
    items.push({
      label: 'Kembali ke Admin',
      icon: 'i-lucide-arrow-left',
      to: '/admin',
      exact: true,
      onSelect: () => { open.value = false }
    })
  }

  items.push(
    {
      label: 'Beranda',
      icon: 'i-lucide-house',
      to: '/operations',
      onSelect: () => {
        open.value = false
      }
    },
    {
      label: 'Delivery Order',
      icon: 'i-lucide-truck',
      to: '/operations/delivery-order',
      onSelect: () => {
        open.value = false
      }
    },
    {
      label: 'Surat PO Transportir',
      icon: 'i-lucide-file-text',
      to: '/operations/po-transportir',
      onSelect: () => {
        open.value = false
      }
    },
    {
      label: 'Rekap Data Delivery Order',
      icon: 'i-lucide-square-chart-gantt',
      to: '/operations/rekap',
      onSelect: () => {
        open.value = false
      }
    }
  )

  return [items] satisfies NavigationMenuItem[][]
})
</script>

<template>
  <UDashboardGroup unit="rem">
    <UDashboardSidebar
      id="default"
      v-model:open="open"
      collapsible
      resizable
      class="bg-elevated/25"
      :ui="{ footer: 'lg:border-t lg:border-default' }"
    >
      <template #header="{ collapsed }">
        <UserMenu :collapsed="collapsed" />
      </template>

      <template #default="{ collapsed }">
        <UNavigationMenu
          :collapsed="collapsed"
          :items="links[0]"
          orientation="vertical"
          tooltip
          popover
        />
      </template>

      <template #footer="{ collapsed }">
        <SidebarNotifications :collapsed="collapsed" />
      </template>
    </UDashboardSidebar>

    <slot />
  </UDashboardGroup>
</template>
