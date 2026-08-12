<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const open = ref(false)

const { user } = useAuth()

const isAdmin = computed(() => user.value?.role === 'admin')

const links = computed<NavigationMenuItem[][]>(() => {
  const items: NavigationMenuItem[] = []

  // Jika admin yang sedang mengakses halaman accounting, tambah link kembali ke admin
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
      label: 'Dashboard',
      icon: 'i-lucide-house',
      to: '/accounting',
      exact: true,
      onSelect: () => { open.value = false }
    },
    {
      label: 'Laporan Keuangan',
      icon: 'i-lucide-file-bar-chart',
      defaultOpen: true,
      children: [
        {
          label: 'Neraca',
          icon: 'i-lucide-scale',
          to: '/accounting/neraca',
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Rekap Cashflow',
          icon: 'i-lucide-arrow-left-right',
          to: '/accounting/rekap-cashflow',
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Rekap Biaya',
          icon: 'i-lucide-receipt',
          to: '/accounting/rekap-biaya',
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Rekap Monitoring',
          icon: 'i-lucide-monitor',
          to: '/accounting/rekap-monitoring',
          onSelect: () => {
            open.value = false
          }
        }
      ]
    },
    {
      label: 'Jurnal & Buku Besar',
      icon: 'i-lucide-book-open-text',
      defaultOpen: true,
      children: [
        {
          label: 'Jurnal Umum',
          icon: 'i-lucide-book-open',
          to: '/accounting/jurnal-umum',
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Buku Besar',
          icon: 'i-lucide-book-copy',
          to: '/accounting/buku-besar',
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Kas Harian',
          icon: 'i-lucide-wallet',
          to: '/accounting/kas-harian',
          onSelect: () => {
            open.value = false
          }
        }
      ]
    },
    {
      label: 'Analisis Keuangan',
      icon: 'i-lucide-chart-column',
      defaultOpen: true,
      children: [
        {
          label: 'Pemasukan',
          icon: 'i-lucide-trending-up',
          to: '/accounting/pemasukan',
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Pengeluaran',
          icon: 'i-lucide-trending-down',
          to: '/accounting/pengeluaran',
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Rekap Bunga Bank',
          icon: 'i-lucide-percent',
          to: '/accounting/rekap-bunga-bank',
          onSelect: () => {
            open.value = false
          }
        }
      ]
    },
    {
      label: 'Pengaturan',
      icon: 'i-lucide-cog',
      defaultOpen: true,
      children: [
        {
          label: 'Bagan Akun',
          icon: 'i-lucide-list-tree',
          to: '/accounting/akun',
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Profil',
          icon: 'i-lucide-user',
          to: '/accounting/profile',
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

    <UDashboardPanel id="accounting-main">
      <template #header>
        <UDashboardNavbar :ui="{ right: 'gap-2' }" />
      </template>

      <template #body>
        <slot />
      </template>
    </UDashboardPanel>
  </UDashboardGroup>
</template>
