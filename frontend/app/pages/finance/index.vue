<script setup lang="ts">
import { sub } from 'date-fns'
import type { Period, Range } from '~/types'

const range = shallowRef<Range>({
  start: sub(new Date(), { days: 14 }),
  end: new Date()
})
const period = ref<Period>('daily')

const { isSlideoverOpen, unreadCount, fetchNotifications } = useNotifications()

onMounted(() => fetchNotifications())

definePageMeta({ layout: 'finance' })
</script>

<template>
  <UDashboardPanel id="home">
    <template #header>
      <UDashboardNavbar title="Beranda" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UTooltip text="Notifikasi">
            <UButton
              color="neutral"
              variant="ghost"
              square
              aria-label="Buka notifikasi"
              @click="isSlideoverOpen = true"
            >
              <div class="relative">
                <UIcon name="i-lucide-bell" class="size-5 shrink-0" />
                <span
                  v-if="unreadCount > 0"
                  class="absolute -right-2 -top-2 flex min-w-[1.1rem] items-center justify-center rounded-full bg-error px-1 py-px text-[10px] font-bold leading-none text-white"
                >
                  {{ unreadCount > 99 ? '99+' : unreadCount }}
                </span>
              </div>
            </UButton>
          </UTooltip>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <h1 class="text-3xl font-bold dark:text-neutral-50 text-neutral-900">
        Rekap Data Finance
      </h1>
      <FinanceStats :period="period" :range="range" />
    </template>
  </UDashboardPanel>

  <NotificationsSlideover />
  <NotificationDetailModal />
</template>
