<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const open = ref(false)

const links = [
  [
    {
      label: 'Dashboard',
      icon: 'i-lucide-house',
      to: '/accounting',
      exact: true,
      onSelect: () => {
        open.value = false
      }
    },
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
    },
    {
      label: 'Kas Harian',
      icon: 'i-lucide-wallet',
      to: '/accounting/kas-harian',
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
    },
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
      label: 'Chart of Accounts',
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
] satisfies NavigationMenuItem[][]
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
