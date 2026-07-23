<script setup lang="ts">
const { isNotificationsSlideoverOpen } = useDashboard()
const { get } = useApi()

const { data: notifications } = await useAsyncData("notifications", async () => {
  const res = await get<{ id: string; title: string; message: string; type: string; created_at: string }[]>("/notifications")
  return (res || []).map((n: any) => ({
    id: n.id,
    unread: true,
    sender: { name: n.title, avatar: { src: "", alt: n.title } },
    body: n.message,
    date: n.created_at,
  }))
}, { default: () => [] })
</script>

<template>
  <USlideover
    v-model:open="isNotificationsSlideoverOpen"
    title="Notifications"
  >
    <template #body>
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="px-3 py-2.5 rounded-md hover:bg-elevated/50 flex items-center gap-3 relative -mx-3 first:-mt-3 last:-mb-3"
      >
        <UChip color="error" :show="!!notification.unread" inset>
          <UAvatar
            :alt="notification.sender.name"
            size="md"
          />
        </UChip>

        <div class="text-sm flex-1">
          <p class="flex items-center justify-between">
            <span class="text-highlighted font-medium">{{ notification.sender.name }}</span>
            <time :datetime="notification.date" class="text-muted text-xs">
              {{ notification.date ? new Date(notification.date).toLocaleDateString() : '' }}
            </time>
          </p>
          <p class="text-dimmed">{{ notification.body }}</p>
        </div>
      </div>
    </template>
  </USlideover>
</template>
