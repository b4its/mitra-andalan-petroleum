<script setup lang="ts">
import { sub } from 'date-fns'
import type { DropdownMenuItem } from '@nuxt/ui'
import type { Period, Range } from '~/types'
import type { Notifications } from '~/types/notification'

const { isNotificationsSlideoverOpen } = useDashboard()

const items = [
  [
    {
      label: 'New mail',
      icon: 'i-lucide-send',
      to: '/inbox'
    },
    {
      label: 'New customer',
      icon: 'i-lucide-user-plus',
      to: '/customers'
    }
  ]
] satisfies DropdownMenuItem[][]

const range = shallowRef<Range>({
  start: sub(new Date(), { days: 14 }),
  end: new Date()
})
const period = ref<Period>('daily')

const { get } = useApi()
const { data: financeNotif } = await useAsyncData(
  'notifications',
  async () => {
    const res = await get<Notifications[]>('/notifications')
    return res
  },
  { default: () => [] }
)

function setNotificationsSlideoverOpen(value: boolean) {
  isNotificationsSlideoverOpen.value = value
}

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
          <UTooltip text="Notifications" :shortcuts="['N']">
            <UButton
              color="neutral"
              variant="ghost"
              square
              @click="setNotificationsSlideoverOpen(true)"
            >
              <!-- <UChip color="error" inset> -->
              <UIcon name="i-lucide-bell" class="size-5 shrink-0" />
              <!-- </UChip> -->
            </UButton>
          </UTooltip>

          <UDropdownMenu :items="items">
            <UButton
              icon="i-lucide-plus"
              label="Aksi Cepat"
              size="md"
              class="rounded-full"
            />
          </UDropdownMenu>
        </template>
      </UDashboardNavbar>

      <!-- <UDashboardToolbar>
        <template #left>
           NOTE: The `-ms-1` class is used to align with the `DashboardSidebarCollapse` button here.
          <HomeDateRangePicker v-model="range" class="-ms-1" />

          <HomePeriodSelect v-model="period" :range="range" />
        </template>
      </UDashboardToolbar> -->
    </template>

    <template #body>
      <h1 class="text-3xl font-bold dark:text-neutral-50 text-neutral-900">
        Rekap Data Finance
      </h1>
      <FinanceStats :period="period" :range="range" />
      <!-- <HomeChart :period="period" :range="range" /> -->
      <!-- <FinanceTable :period="period" :range="range" /> -->
    </template>
  </UDashboardPanel>

  <NotificationsSlideover :notifications="financeNotif" />
</template>
