<script setup lang="ts">
const { collapsed } = defineProps<{ collapsed?: boolean }>()

const { unreadCount, isSlideoverOpen, fetchNotifications } = useNotifications()

onMounted(() => fetchNotifications())
</script>

<template>
  <div class="flex flex-col gap-4">
    <UButton
      icon="i-lucide-bell"
      :label="collapsed ? undefined : 'Notifikasi'"
      color="neutral"
      variant="ghost"
      :square="collapsed"
      class="w-full justify-start"
      aria-label="Buka notifikasi"
      @click="isSlideoverOpen = true"
    >
      <template v-if="!collapsed" #trailing>
        <UBadge
          v-if="unreadCount"
          size="xs"
          color="error"
          variant="solid"
        >
          {{ unreadCount > 99 ? '99+' : unreadCount }}
        </UBadge>
      </template>
    </UButton>

    <NotificationsSlideover />
    <NotificationDetailModal />
  </div>
</template>
