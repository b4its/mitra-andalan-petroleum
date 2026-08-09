<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const open = ref(false)
const notificationsOpen = ref(false)

const { unreadCount, fetchNotifications } = useNotifications()

onMounted(() => fetchNotifications())

const links = [
  [
    {
      label: 'Dashboard',
      icon: 'i-lucide-house',
      to: '/admin',
      onSelect: () => {
        open.value = false
      }
    },
    {
      label: 'Marketing',
      icon: 'i-lucide-flag-triangle-right',
      defaultOpen: true,
      children: [
        {
          label: 'Rekap Keseluruhan',
          to: '/admin/marketing',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Halaman Marketing',
          icon: 'i-lucide-arrow-up-right',
          to: '/marketing',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        }
      ]
    },
    {
      label: 'Operations',
      icon: 'i-lucide-truck',
      defaultOpen: true,
      children: [
        {
          label: 'Rekap Keseluruhan',
          to: '/admin/operations',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Data Delivery Order',
          to: '/admin/data-do',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Halaman Operations',
          icon: 'i-lucide-arrow-up-right',
          to: '/operations',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        }
      ]
    },
    {
      label: 'Finance',
      icon: 'i-lucide-receipt-text',
      defaultOpen: true,
      children: [
        {
          label: 'Rekap Keseluruhan',
          to: '/admin/finance',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Halaman Finance',
          icon: 'i-lucide-arrow-up-right',
          to: '/finance',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        }
      ]
    },
    {
      label: 'Accounting',
      icon: 'i-lucide-book-open',
      defaultOpen: true,
      children: [
        {
          label: 'Rekap Keseluruhan',
          to: '/admin/accounting',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Halaman Accounting',
          icon: 'i-lucide-arrow-up-right',
          to: '/accounting',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        }
      ]
    },
    {
      label: 'Master Data',
      icon: 'i-lucide-database',
      defaultOpen: true,
      children: [
        {
          label: 'Customer',
          to: '/admin/customers',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Supplier',
          to: '/admin/suppliers',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        },
        {
          label: 'Database Konfigurasi',
          to: '/admin/database',
          exact: true,
          onSelect: () => {
            open.value = false
          }
        }
      ]
    },
    {
      label: 'Pengguna',
      icon: 'i-lucide-users',
      to: '/admin/users',
      onSelect: () => {
        open.value = false
      }
    },
    {
      label: 'Profil',
      icon: 'i-lucide-user',
      to: '/admin/profile',
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

      <template #footer="{ collapsed }">
        <UButton
          :icon="'i-lucide-bell'"
          :label="collapsed ? undefined : 'Notifikasi'"
          color="neutral"
          variant="ghost"
          :square="collapsed"
          class="w-full justify-start"
          @click="notificationsOpen = true"
        >
          <template v-if="!collapsed && unreadCount" #trailing>
            <UBadge size="xs" color="error" variant="solid">
              {{ unreadCount > 99 ? '99+' : unreadCount }}
            </UBadge>
          </template>
        </UButton>
      </template>
    </UDashboardSidebar>

    <slot />

    <AdminNotificationsModal v-model:open="notificationsOpen" />
  </UDashboardGroup>
</template>
