<script setup lang="ts">
const router = useRouter()
const { selectedNotification, isDetailModalOpen, closeDetail } = useNotifications()

function handleView() {
  const to = selectedNotification.value?.to
  closeDetail()
  if (to) router.push(to)
}

const typeColor: Record<string, 'info' | 'success' | 'warning' | 'error'> = {
  info: 'info',
  success: 'success',
  warning: 'warning',
  error: 'error'
}
</script>

<template>
  <UModal
    v-model:open="isDetailModalOpen"
    :ui="{ footer: 'justify-end' }"
    @update:open="(val) => { if (!val) closeDetail() }"
  >
    <template #title>
      <div class="flex items-center gap-2">
        <UBadge
          v-if="selectedNotification"
          :color="typeColor[selectedNotification.type] ?? 'neutral'"
          variant="subtle"
          class="capitalize"
        >
          {{ selectedNotification.type }}
        </UBadge>
        <span>{{ selectedNotification?.title ?? 'Notifikasi' }}</span>
      </div>
    </template>

    <template #body>
      <div v-if="selectedNotification" class="space-y-3">
        <p class="text-sm leading-relaxed text-muted">
          {{ selectedNotification.message }}
        </p>
        <p class="text-xs text-dimmed">
          {{ selectedNotification.created_at ? formatDate(selectedNotification.created_at) : '' }}
        </p>
      </div>
    </template>

    <template #footer>
      <UButton color="neutral" variant="ghost" @click="closeDetail">
        Tutup
      </UButton>
      <UButton
        v-if="selectedNotification?.to"
        color="primary"
        icon="i-lucide-external-link"
        @click="handleView"
      >
        View
      </UButton>
    </template>
  </UModal>
</template>
