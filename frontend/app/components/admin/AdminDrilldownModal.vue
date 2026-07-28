<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'

const props = defineProps<{
  open: boolean
  metric?: { key: string, title: string, value: number, unit: string, description: string }
  dateFrom: string
  dateTo: string
}>()

const emit = defineEmits<{ 'update:open': [value: boolean] }>()

const page = ref(1)
const { get } = useApi()
const { data, pending, error, refresh } = await useAsyncData(
  () => `admin-drilldown-${props.metric?.key}-${props.dateFrom}-${props.dateTo}-${page.value}`,
  () => {
    if (!props.metric?.key) return Promise.resolve(null)
    return get<any>('/stats/admin/drilldown', {
      metric: props.metric.key,
      date_from: props.dateFrom,
      date_to: props.dateTo,
      page: page.value,
      page_size: 10
    })
  },
  { watch: [() => props.metric?.key, () => props.dateFrom, () => props.dateTo, page] }
)

watch(() => props.open, (open) => {
  if (open) {
    page.value = 1
    refresh()
  }
})

const columns: TableColumn<any>[] = [
  { accessorKey: 'title', header: 'Data' },
  { accessorKey: 'subtitle', header: 'Keterangan' },
  { accessorKey: 'status', header: 'Status' },
  {
    accessorKey: 'value',
    header: 'Nilai',
    cell: ({ row }) => formatNumber(row.getValue('value') || 0)
  },
  {
    accessorKey: 'created_at',
    header: 'Dibuat',
    cell: ({ row }) => row.getValue('created_at') ? formatDate(row.getValue('created_at')) : '-'
  }
]

function formatValue(value: number) {
  return props.metric?.unit === 'currency' ? formatCurrency(value) : formatNumber(value)
}
</script>

<template>
  <UModal :open="open" title="Rincian Perhitungan" @update:open="emit('update:open', $event)">
    <template #body>
      <div v-if="metric" class="space-y-5">
        <div class="rounded-lg bg-muted/50 p-4">
          <p class="text-sm text-muted">
            {{ metric.title }}
          </p>
          <p class="mt-1 text-2xl font-semibold">
            {{ formatValue(metric.value) }}
          </p>
          <p class="mt-2 text-sm text-muted">
            {{ metric.description }}
          </p>
          <p class="mt-2 text-xs text-muted">
            Periode: {{ formatDate(dateFrom) }} - {{ formatDate(dateTo) }}
          </p>
        </div>

        <UAlert
          v-if="error"
          color="error"
          title="Gagal memuat rincian"
          :description="error.message"
        />
        <div v-else-if="pending" class="space-y-3">
          <USkeleton class="h-10 w-full" />
          <USkeleton class="h-28 w-full" />
        </div>
        <template v-else>
          <div class="flex items-center justify-between text-sm">
            <span class="text-muted">{{ data?.description }}</span>
            <span class="font-medium">{{ data?.total || 0 }} record</span>
          </div>
          <UTable :data="data?.items || []" :columns="columns" />
          <UEmpty
            v-if="!data?.items?.length"
            icon="i-lucide-search-x"
            title="Tidak ada data"
            description="Tidak ada record pada filter aktif."
          />
          <div v-if="(data?.total || 0) > 10" class="flex justify-end">
            <UPagination v-model:page="page" :total="data.total" :items-per-page="10" />
          </div>
        </template>
      </div>
    </template>
  </UModal>
</template>
