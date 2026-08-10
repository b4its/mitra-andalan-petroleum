<script setup lang="ts">
import type { ExportColumn } from '~/composables/useExport'
import type { CostRecapResponse, CostRecapRow } from '~/types/accounting'

const { get } = useApi()
const { toCSV, toExcel, toPDF } = useExport()

const dateFrom = ref('')
const dateTo = ref('')
const expandedGroups = ref<Set<string>>(new Set())

const exportColumns: ExportColumn<CostRecapRow>[] = [
  { header: 'Tanggal', accessor: (row: CostRecapRow) => formatDate(row.entry_date) },
  { header: 'Deskripsi', accessor: (row: CostRecapRow) => row.description },
  { header: 'Akun', accessor: (row: CostRecapRow) => `${row.account_code} · ${row.account_name}` },
  { header: 'Jumlah', accessor: (row: CostRecapRow) => row.amount },
  { header: 'Referensi', accessor: (row: CostRecapRow) => row.reference ?? '-' }
]

function onExport(format: 'excel' | 'pdf' | 'csv') {
  if (!data.value) return
  const allRows = data.value.groups.flatMap(g => g.items)
  const filename = `rekap-biaya-${new Date().toISOString().slice(0, 10)}`
  const totals = [{ label: 'Total Biaya', value: data.value.total_cost }]
  if (format === 'excel') toExcel(filename, 'Rekap Biaya', exportColumns, allRows)
  else if (format === 'pdf') toPDF(filename, 'Rekap Biaya', exportColumns, allRows, { totals })
  else toCSV(filename, exportColumns, allRows)
}

const { data, refresh, pending } = await useAsyncData(
  'accounting-cost-recap',
  async () => {
    const params: Record<string, string> = {}
    if (dateFrom.value) params.date_from = dateFrom.value
    if (dateTo.value) params.date_to = dateTo.value
    return get<CostRecapResponse>('/accounting/cost-recap', params)
  },
  { default: () => null, server: false }
)

const totalCost = computed(() => data.value?.total_cost ?? 0)

function toggleGroup(code: string) {
  if (expandedGroups.value.has(code)) {
    expandedGroups.value.delete(code)
  } else {
    expandedGroups.value.add(code)
  }
}

definePageMeta({ layout: 'accounting' })
</script>

<template>
  <UDashboardPanel id="accounting-rekap-biaya">
    <template #header>
      <UDashboardNavbar>
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">
              Rekap Biaya
            </p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Seluruh biaya (expense) yang dikelompokkan per akun
            </p>
          </div>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-4 lg:p-6">
        <section class="flex flex-col lg:gap-4">
          <UCard>
            <div class="flex flex-wrap items-end gap-3">
              <UFormField label="Dari Tanggal">
                <UInput v-model="dateFrom" type="date" />
              </UFormField>
              <UFormField label="Sampai Tanggal">
                <UInput v-model="dateTo" type="date" />
              </UFormField>
              <UButton
                icon="i-lucide-search"
                :loading="pending"
                @click="() => refresh()"
              >
                Tampilkan
              </UButton>
              <UDropdownMenu
                :items="[
                  { type: 'label', label: 'Export Data' },
                  { type: 'separator' },
                  { label: 'Export to Excel', icon: 'i-lucide-file-spreadsheet', disabled: !data, onSelect: () => onExport('excel') },
                  { label: 'Export to PDF', icon: 'i-lucide-file-text', disabled: !data, onSelect: () => onExport('pdf') },
                  { label: 'Export to CSV', icon: 'i-lucide-file-down', disabled: !data, onSelect: () => onExport('csv') }
                ]"
              >
                <UButton
                  icon="i-lucide-download"
                  color="neutral"
                  variant="soft"
                  :disabled="!data"
                >
                  Export
                </UButton>
              </UDropdownMenu>
            </div>
          </UCard>

          <div v-if="pending" class="flex flex-col gap-4">
            <USkeleton class="h-20 rounded-lg" />
            <USkeleton v-for="i in 4" :key="i" class="h-28 rounded-lg" />
          </div>
          <template v-else-if="data">
            <UCard color="error" variant="subtle">
              <div class="flex items-center justify-between">
                <span class="text-sm text-neutral-500 dark:text-neutral-400">Total Biaya</span>
                <span class="text-2xl font-bold">{{ formatCurrency(totalCost) }}</span>
              </div>
            </UCard>

            <div class="flex flex-col gap-3">
              <UCard
                v-for="group in data.groups"
                :key="group.account_code"
              >
                <template #header>
                  <button
                    class="flex items-center justify-between w-full text-left"
                    @click="toggleGroup(group.account_code)"
                  >
                    <div class="flex items-center gap-2">
                      <UIcon
                        :name="expandedGroups.has(group.account_code) ? 'i-lucide-chevron-down' : 'i-lucide-chevron-right'"
                        class="size-4 text-muted"
                      />
                      <span class="font-medium">{{ group.account_code }} · {{ group.account_name }}</span>
                    </div>
                    <span class="font-bold text-error">{{ formatCurrency(group.total) }}</span>
                  </button>
                </template>

                <template v-if="expandedGroups.has(group.account_code)">
                  <div class="flex flex-col divide-y divide-default">
                    <div
                      v-for="item in group.items"
                      :key="item.id"
                      class="flex items-center justify-between py-2 text-sm"
                    >
                      <div class="min-w-0">
                        <p class="truncate max-w-96">
                          {{ item.description }}
                        </p>
                        <p class="text-xs text-neutral-500 dark:text-neutral-400">
                          {{ formatDate(item.entry_date) }}
                          <span v-if="item.reference">· {{ item.reference }}</span>
                        </p>
                      </div>
                      <span class="font-medium shrink-0">{{ formatCurrency(item.amount) }}</span>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <p class="text-sm text-neutral-500 py-1">
                    {{ group.items.length }} transaksi — klik untuk detail
                  </p>
                </template>
              </UCard>
            </div>

            <p
              v-if="!data.groups.length"
              class="py-6 text-center text-sm text-neutral-500"
            >
              Belum ada data biaya
            </p>
          </template>

          <UAlert
            v-else-if="!pending"
            title="Pilih Periode"
            description="Gunakan filter tanggal di atas untuk menampilkan rekap biaya."
            icon="i-lucide-info"
            color="info"
            variant="soft"
          />
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>
