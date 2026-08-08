<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const open = ref(false)

const { user } = useAuth()
const isAdmin = computed(() => user.value?.role === 'admin')

const links = computed<NavigationMenuItem[][]>(() => {
  const items: NavigationMenuItem[] = []

  // Jika admin yang sedang mengakses halaman finance, tambah link kembali ke admin
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
      to: '/finance',
      onSelect: () => {
        open.value = false
      }
    },
    {
      label: 'Data DO',
      icon: 'i-lucide-truck',
      to: '/finance/do',
      onSelect: () => {
        open.value = false
      }
    },
    {
      label: 'Manajemen Invoice',
      icon: 'i-lucide-receipt',
      defaultOpen: true,
      children: [
        {
          label: 'Pembuatan Invoice',
          to: '/finance/invoice/pembuatan-invoice',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Data Invoice Customer',
          to: '/finance/invoice/data-invoice-customer',
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
    </UDashboardSidebar>

    <slot />
  </UDashboardGroup>
</template>
