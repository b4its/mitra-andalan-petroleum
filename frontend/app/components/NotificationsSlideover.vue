<script setup lang="ts">
import type { Notifications } from "~/types/notification";

defineProps<{
  notifications: Notifications[];
}>();

const { isNotificationsSlideoverOpen } = useDashboard();
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
              notification.title
            }}</span>
            <time
              :datetime="formatDate(notification.created_at)"
              class="text-muted text-xs"
            >
              {{
                notification.created_at
                  ? formatDate(notification.created_at)
                  : ""
              }}
            </time>
          </p>
          <p class="text-dimmed">{{ notification.message }}</p>
        </div>
      </NuxtLink>
    </template>
  </USlideover>
</template>
