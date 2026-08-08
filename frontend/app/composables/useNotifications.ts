import { createSharedComposable } from '@vueuse/core'
import type { Notifications } from '~/types/notification'

const _useNotifications = () => {
  const { get, put } = useApi()

  const notifications = ref<Notifications[]>([])
  const isSlideoverOpen = ref(false)
  const selectedNotification = ref<Notifications | null>(null)
  const isDetailModalOpen = ref(false)
  const loading = ref(false)

  const unreadCount = computed(() =>
    notifications.value.filter(n => !n.is_read).length
  )

  async function fetchNotifications() {
    try {
      loading.value = true
      const res = await get<Notifications[]>('/notifications')
      notifications.value = res
    } catch {
      // silently ignore
    } finally {
      loading.value = false
    }
  }

  async function markAsRead(notification: Notifications) {
    if (notification.is_read) return
    try {
      await put(`/notifications/${notification.id}`, { is_read: true })
      const idx = notifications.value.findIndex(n => n.id === notification.id)
      if (idx !== -1) {
        notifications.value[idx] = { ...notifications.value[idx]!, is_read: true }
      }
    } catch {
      // silently ignore
    }
  }

  function openDetail(notification: Notifications) {
    isSlideoverOpen.value = false
    selectedNotification.value = notification
    isDetailModalOpen.value = true
    markAsRead(notification)
  }

  function closeDetail() {
    isDetailModalOpen.value = false
    selectedNotification.value = null
  }

  return {
    notifications,
    unreadCount,
    isSlideoverOpen,
    selectedNotification,
    isDetailModalOpen,
    loading,
    fetchNotifications,
    markAsRead,
    openDetail,
    closeDetail
  }
}

export const useNotifications = createSharedComposable(_useNotifications)
