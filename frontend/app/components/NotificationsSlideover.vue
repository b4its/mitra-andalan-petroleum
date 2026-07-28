<script setup lang="ts">
const { notifications, isSlideoverOpen, openDetail, loading } = useNotifications()
</script>

<template>
  <USlideover v-model:open="isSlideoverOpen" title="Notifikasi">
    <template #body>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <UIcon name="i-lucide-loader" class="size-6 animate-spin text-muted" />
      </div>

      <div v-else-if="!notifications.length" class="flex flex-col items-center justify-center gap-3 py-12 text-center">
        <UIcon name="i-lucide-bell-off" class="size-10 text-muted" />
        <p class="text-sm text-muted">Tidak ada notifikasi</p>
      </div>

      <div v-else class="flex flex-col gap-1">
        <button
          v-for="notification in notifications"
          :key="notification.id"
          type="button"
          class="w-full rounded-lg px-3 py-3 text-left transition hover:bg-elevated/60 focus:outline-none focus:ring-2 focus:ring-primary"
          :class="{ 'opacity-60': notification.is_read }"
          @click="openDetail(notification)"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="flex items-center gap-2 min-w-0">
              <span
                v-if="!notification.is_read"
                class="mt-1 size-2 shrink-0 rounded-full bg-error"
              />
              <span
                v-else
                class="mt-1 size-2 shrink-0 rounded-full bg-transparent"
              />
              <p class="truncate text-sm font-medium text-highlighted">
                {{ notification.title }}
              </p>
            </div>
            <time class="shrink-0 text-xs text-muted">
              {{ notification.created_at ? formatDate(notification.created_at) : '' }}
            </time>
          </div>
          <p class="mt-1 pl-4 text-xs text-dimmed line-clamp-2">
            {{ notification.message }}
          </p>
        </button>
      </div>
    </template>
  </USlideover>
</template>
