<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const open = ref(false)

const { user } = useAuth()
const isAdmin = computed(() => user.value?.role === 'admin')

const links = computed<NavigationMenuItem[][]>(() => {
  const items: NavigationMenuItem[] = []

  // Jika admin yang sedang mengakses halaman marketing, tambah link kembali ke admin
  if (isAdmin.value) {
    items.push({
      label: 'Kembali ke Admin',
      icon: 'i-lucide-arrow-left',
      to: '/admin',
      exact: true,
      onSelect: () => {
        open.value = false
      }
    })
  }

  items.push(
    {
      label: 'Beranda',
      icon: 'i-lucide-house',
      to: '/marketing',
      onSelect: () => {
        open.value = false
      }
    },
    {
      label: 'Customer',
      icon: 'i-lucide-users',

      defaultOpen: true,
      children: [
        {
          label: 'Rekap',
          to: '/marketing/customer',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Surat Penawaran Customer',
          to: '/marketing/customer/penawaran',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Purchase Order Customer',
          to: '/marketing/customer/po',
          onSelect: () => {
            open.value = false
          }
        }
      ]
    },
    {
      label: 'Supplier',
      icon: 'i-lucide-truck',

      defaultOpen: true,
      children: [
        {
          label: 'Rekap',
          to: '/marketing/supplier',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Purchase Order Supplier',
          to: '/marketing/supplier/po',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        }
      ]
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
