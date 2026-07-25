<script setup lang="ts">
import type { Notifications } from "~/types/notification";

const { isNotificationsSlideoverOpen } = useDashboard();
const { get } = useApi();

const { data: notifications } = await useAsyncData(
  "notifications",
  async () => {
    const res = await get<Notifications[]>("/notifications");
    return (res || []).map((notif: Notifications) => ({
      id: notif.id,
      sender: {
        name: notif.title,
        avatar: { src: "", alt: notif.title },
      },
      body: notif.message,
      date: notif.created_at,
    }));
  },
  { default: () => [] },
);
</script>

<template>
  <USlideover v-model:open="isNotificationsSlideoverOpen" title="Notifications">
    <template #body>
      <NuxtLink
        v-for="notification in notifications"
        :key="notification.id"
        to="#"
        class="px-3 py-2.5 rounded-md hover:bg-elevated/50 flex items-center gap-3 relative -mx-3 first:-mt-3 last:-mb-3"
      >
        <!-- <UChip color="error" :show="!!notification.unread" inset>
          <UAvatar :alt="notification.sender.name" size="md" />
        </UChip> -->

        <div @click="" class="text-sm flex-1">
          <p class="flex items-center justify-between">
            <span class="text-highlighted font-medium">{{
              notification.sender.name
            }}</span>
            <time
              :datetime="formatDate(notification.date)"
              class="text-muted text-xs"
            >
              {{ notification.date ? formatDate(notification.date) : "" }}
            </time>
          </p>
          <p class="text-dimmed">{{ notification.body }}</p>
        </div>
      </NuxtLink>
    </template>
  </USlideover>
</template>
