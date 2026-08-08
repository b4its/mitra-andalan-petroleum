<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { Notifications } from '~/types/notification'

const { get, put } = useApi()
const toast = useToast()

const { data: notifications, refresh, pending } = await useAsyncData(
  'accounting-notifications',
  () => get<Notifications[]>('/notifications', { role: 'accounting' }),
  { default: () => [], server: false }
)

const unreadCount = computed(() =>
  notifications.value.filter(n => !n.is_read).length
)

const typeBadge = (type: string) => {
  const colors: Record<string, string> = {
    info: 'info',
    warning: 'warning',
    success: 'success',
    error: 'error'
  }
  return colors[type] || 'neutral'
}

const typeIcon = (type: string) => {
  const icons: Record<string, string> = {
    info: 'i-lucide-info',
    warning: 'i-lucide-alert-triangle',
    success: 'i-lucide-check-circle',
    error: 'i-lucide-circle-x'
  }
  return icons[type] || 'i-lucide-bell'
}

async function markAsRead(notification: Notifications) {
  if (notification.is_read) return
  try {
    await put(`/notifications/${notification.id}`, { is_read: true })
    toast.add({
      title: 'Notifikasi ditandai dibaca',
      icon: 'i-lucide-check',
      color: 'success'
    })
    refresh()
  } catch (err: any) {
    toast.add({
      title: 'Gagal',
      description: err.message || 'Terjadi kesalahan',
      color: 'error'
    })
  }
}

async function markAllAsRead() {
  const unread = notifications.value.filter(n => !n.is_read)
  if (!unread.length) return
  try {
    await Promise.all(unread.map(n => put(`/notifications/${n.id}`, { is_read: true })))
    toast.add({
      title: 'Semua notifikasi ditandai dibaca',
      icon: 'i-lucide-check-check',
      color: 'success'
    })
    refresh()
  } catch (err: any) {
    toast.add({
      title: 'Gagal',
      description: err.message || 'Terjadi kesalahan',
      color: 'error'
    })
  }
}

definePageMeta({ layout: 'accounting' })
</script>

<template>
  <UDashboardPanel id="accounting-notifications">
    <template #header>
      <UDashboardNavbar>
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div class="flex items-center gap-3">
            <div>
              <p class="text-base font-semibold">Notifikasi</p>
              <p class="text-xs text-neutral-500 dark:text-neutral-400">
                Notifikasi khusus untuk role accounting
              </p>
            </div>
            <UBadge v-if="unreadCount" color="error" variant="solid" size="sm">
              {{ unreadCount }} belum dibaca
            </UBadge>
          </div>
        </template>
        <template #right>
          <UButton
            icon="i-lucide-check-check"
            color="primary"
            variant="soft"
            size="sm"
            :disabled="unreadCount === 0"
            @click="markAllAsRead"
          >
            Tandai Semua Dibaca
          </UButton>
          <UButton
            icon="i-lucide-refresh-cw"
            color="neutral"
            variant="ghost"
            size="sm"
            @click="() => refresh()"
          >
            Muat Ulang
          </UButton>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-4 lg:p-6">
        <section class="flex flex-col lg:gap-4">
          <!-- Skeleton -->
          <div v-if="pending" class="space-y-3">
            <USkeleton v-for="i in 5" :key="i" class="h-20 rounded-xl" />
          </div>

          <!-- Empty state -->
          <div
            v-else-if="!notifications.length"
            class="flex flex-col items-center justify-center gap-4 py-20"
          >
            <UIcon name="i-lucide-bell-off" class="size-16 text-muted" />
            <p class="text-lg font-medium text-muted">Tidak ada notifikasi</p>
            <p class="text-sm text-muted">
              Belum ada notifikasi untuk role accounting.
            </p>
          </div>

          <!-- Notification list -->
          <div v-else class="flex flex-col gap-2">
            <div
              v-for="notification in notifications"
              :key="notification.id"
              class="group relative flex items-start gap-4 rounded-xl border border-default bg-default p-4 transition hover:bg-elevated/50"
              :class="{ 'border-l-4 border-l-primary': !notification.is_read }"
            >
              <!-- Icon -->
              <div
                class="flex size-10 shrink-0 items-center justify-center rounded-lg"
                :class="{
                  'bg-info/10 text-info': notification.type === 'info',
                  'bg-warning/10 text-warning': notification.type === 'warning',
                  'bg-success/10 text-success': notification.type === 'success',
                  'bg-error/10 text-error': notification.type === 'error'
                }"
              >
                <UIcon :name="typeIcon(notification.type)" class="size-5" />
              </div>

              <!-- Content -->
              <div class="min-w-0 flex-1">
                <div class="flex items-start justify-between gap-2">
                  <div>
                    <p
                      class="text-sm font-medium"
                      :class="notification.is_read ? 'text-muted' : 'text-highlighted'"
                    >
                      {{ notification.title }}
                    </p>
                    <p class="mt-1 text-xs text-muted line-clamp-2">
                      {{ notification.message }}
                    </p>
                  </div>
                  <time class="shrink-0 text-xs text-muted">
                    {{ notification.created_at ? formatDate(notification.created_at) : '' }}
                  </time>
                </div>

                <!-- Footer -->
                <div class="mt-2 flex items-center gap-2">
                  <UBadge
                    v-if="notification.user_name"
                    variant="soft"
                    color="neutral"
                    size="xs"
                  >
                    {{ notification.user_name }}
                  </UBadge>
                  <UBadge
                    :color="typeBadge(notification.type)"
                    variant="soft"
                    size="xs"
                  >
                    {{ notification.type }}
                  </UBadge>
                  <span
                    v-if="notification.is_read"
                    class="text-xs text-muted"
                  >Dibaca</span>
                  <span
                    v-else
                    class="text-xs font-medium text-primary"
                  >Baru</span>
                </div>
              </div>

              <!-- Action -->
              <div class="shrink-0">
                <UButton
                  v-if="!notification.is_read"
                  icon="i-lucide-check"
                  size="sm"
                  color="neutral"
                  variant="ghost"
                  @click="markAsRead(notification)"
                >
                  Tandai Dibaca
                </UButton>
              </div>
            </div>
          </div>
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>