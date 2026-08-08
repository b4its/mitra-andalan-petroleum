<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { CashflowResponse, CashflowItem } from '~/types/accounting'

const { get } = useApi()

const dateFrom = ref('')
const dateTo = ref('')

const { data: cashflow, refresh, pending } = await useAsyncData(
  'accounting-cashflow',
  async () => {
    const params: Record<string, string> = {}
    if (dateFrom.value) params.date_from = dateFrom.value
    if (dateTo.value) params.date_to = dateTo.value
    return get<CashflowResponse>('/accounting/cashflow', params)
  },
  { default: () => null, server: false }
)

const columns: TableColumn<CashflowItem>[] = [
  {
    accessorKey: 'description',
    header: 'Deskripsi',
    cell: ({ row }) => {
      const desc = row.getValue('description') as string
      return h('span', { class: 'truncate block max-w-96' }, desc)
    }
  },
  {
    accessorKey: 'category',
    header: 'Kategori',
    cell: ({ row }) => {
      const cat = row.getValue('category') as string
      return h('span', { class: 'text-xs text-muted' }, cat)
    }
  },
  {
    accessorKey: 'amount',
    header: 'Jumlah',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => {
      const amount = Number(row.getValue('amount'))
      const color = amount >= 0 ? 'text-success' : 'text-error'
      return h('span', { class: `font-semibold ${color}` }, formatCurrency(amount))
    }
  }
]

definePageMeta({ layout: 'accounting' })
</script>

<template>
  <UDashboardPanel id="accounting-cashflow">
    <template #header>
      <UDashboardNavbar>
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">Rekap Arus Kas (Cashflow)</p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Laporan arus kas: operasi, investasi, dan pendanaan
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
            </div>
          </UCard>

          <template v-if="cashflow">
            <!-- Summary Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <UCard color="neutral" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">Saldo Awal</p>
                <p class="text-2xl font-bold">{{ formatCurrency(cashflow.opening_balance) }}</p>
              </UCard>
              <UCard color="success" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">Arus Kas Bersih</p>
                <p class="text-2xl font-bold" :class="cashflow.net_cashflow >= 0 ? 'text-success' : 'text-error'">
                  {{ formatCurrency(cashflow.net_cashflow) }}
                </p>
              </UCard>
              <UCard color="primary" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">Saldo Akhir</p>
                <p class="text-2xl font-bold">{{ formatCurrency(cashflow.closing_balance) }}</p>
              </UCard>
              <UCard color="info" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">Arus Kas Operasi</p>
                <p class="text-2xl font-bold" :class="cashflow.operating.total >= 0 ? 'text-success' : 'text-error'">
                  {{ formatCurrency(cashflow.operating.total) }}
                </p>
              </UCard>
            </div>

            <!-- Operating Cashflow -->
            <UCard>
              <template #header>
                <div class="flex items-center justify-between">
                  <span class="font-semibold">Arus Kas Operasi</span>
                  <span class="font-bold text-lg" :class="cashflow.operating.total >= 0 ? 'text-success' : 'text-error'">
                    {{ formatCurrency(cashflow.operating.total) }}
                  </span>
                </div>
              </template>
              <UTable
                :data="cashflow.operating.items"
                :columns="columns"
                :ui="{
                  base: 'table-fixed border-separate border-spacing-0',
                  thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
                  tbody: '[&>tr]:last:[&>td]:border-b-0',
                  th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
                  td: 'border-b border-default'
                }"
              />
              <p
                v-if="!cashflow.operating.items.length"
                class="py-6 text-center text-sm text-neutral-500"
              >
                Belum ada data arus kas operasi
              </p>
            </UCard>

            <!-- Investing & Financing -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <UCard>
                <template #header>
                  <div class="flex items-center justify-between">
                    <span class="font-semibold">Arus Kas Investasi</span>
                    <span class="font-bold text-lg">{{ formatCurrency(cashflow.investing.total) }}</span>
                  </div>
                </template>
                <p class="py-6 text-center text-sm text-neutral-500">
                  Belum ada data arus kas investasi
                </p>
              </UCard>
              <UCard>
                <template #header>
                  <div class="flex items-center justify-between">
                    <span class="font-semibold">Arus Kas Pendanaan</span>
                    <span class="font-bold text-lg">{{ formatCurrency(cashflow.financing.total) }}</span>
                  </div>
                </template>
                <p class="py-6 text-center text-sm text-neutral-500">
                  Belum ada data arus kas pendanaan
                </p>
              </UCard>
            </div>
          </template>

          <UAlert
            v-else-if="!pending"
            title="Pilih Periode"
            description="Gunakan filter tanggal di atas untuk menampilkan arus kas."
            icon="i-lucide-info"
            color="info"
            variant="soft"
          />
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>