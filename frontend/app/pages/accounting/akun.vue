<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { ExportColumn } from '~/composables/useExport'
import type { AccountingAccount, AccountType } from '~/types/accounting'

const { get, post, put } = useApi()
const toast = useToast()
const loading = ref(false)
const search = ref('')
const debouncedSearch = refDebounced(search, 300)
const typeFilter = ref('')
const { toCSV, toExcel, toPDF } = useExport()

const exportColumns: ExportColumn<AccountingAccount>[] = [
  { header: 'Kode', accessor: (row: AccountingAccount) => row.code },
  { header: 'Nama Akun', accessor: (row: AccountingAccount) => row.name },
  {
    header: 'Jenis',
    accessor: (row: AccountingAccount) => typeLabel(row.type)
  },
  {
    header: 'Status',
    accessor: (row: AccountingAccount) =>
      row.is_active ? 'Aktif' : 'Nonaktif'
  },
  {
    header: 'Deskripsi',
    accessor: (row: AccountingAccount) => row.description ?? ''
  }
]

function onExport(format: 'excel' | 'pdf' | 'csv') {
  const filename = `chart-of-accounts-${new Date().toISOString().slice(0, 10)}`
  if (format === 'excel')
    toExcel(filename, 'Bagan Akun', exportColumns, accounts.value)
  else if (format === 'pdf')
    toPDF(filename, 'Bagan Akun', exportColumns, accounts.value, {
      subtitle: 'Daftar akun untuk jurnal umum'
    })
  else toCSV(filename, exportColumns, accounts.value)
}

const { data: accounts, refresh, pending } = await useAsyncData(
  'accounting-accounts',
  async () => {
    const params: Record<string, string | number | boolean> = {
      include_inactive: true
    }
    if (debouncedSearch.value) params.search = debouncedSearch.value
    if (typeFilter.value && typeFilter.value !== 'all') params.type = typeFilter.value
    const res = await get<AccountingAccount[]>('/accounting/accounts', params)
    return res
  },
  { default: () => [], watch: [debouncedSearch, typeFilter], server: false }
)

// ── Pagination (5 per halaman) ────────────────────────────────
const page = ref(1)
const PAGE_SIZE = 5
const pagedAccounts = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE
  return accounts.value.slice(start, start + PAGE_SIZE)
})
watch([debouncedSearch, typeFilter], () => {
  page.value = 1
})

type BadgeColor = 'error' | 'primary' | 'secondary' | 'success' | 'info' | 'warning' | 'neutral'

const typeOptions: { label: string, value: string, color: BadgeColor }[] = [
  { label: 'Semua Jenis', value: 'all', color: 'neutral' },
  { label: 'Aset', value: 'asset', color: 'info' },
  { label: 'Kewajiban', value: 'liability', color: 'warning' },
  { label: 'Ekuitas', value: 'equity', color: 'primary' },
  { label: 'Pendapatan', value: 'revenue', color: 'success' },
  { label: 'Beban', value: 'expense', color: 'error' }
]

const typeLabel = (type: string) =>
  typeOptions.find(o => o.value === type)?.label ?? type
const typeColor = (type: string) =>
  typeOptions.find(o => o.value === type)?.color ?? 'primary'

const columns: TableColumn<AccountingAccount>[] = [
  {
    accessorKey: 'code',
    header: 'Kode',
    cell: ({ row }) => `${row.getValue('code')}`
  },
  {
    accessorKey: 'name',
    header: 'Nama Akun',
    cell: ({ row }) => `${row.getValue('name')}`
  },
  {
    accessorKey: 'type',
    header: 'Jenis',
    meta: {
      class: { th: 'text-center', td: 'text-center' }
    },
    cell: ({ row }) => {
      const type = row.getValue('type') as AccountType
      return h(
        resolveComponent('UBadge'),
        { variant: 'soft', color: typeColor(type), class: 'capitalize' },
        () => typeLabel(type)
      )
    }
  },
  {
    accessorKey: 'is_active',
    header: 'Status',
    meta: {
      class: { th: 'text-center', td: 'text-center' }
    },
    cell: ({ row }) => {
      const active = row.getValue('is_active') as boolean
      return h(
        resolveComponent('UBadge'),
        { variant: 'soft', color: active ? 'success' : 'neutral' },
        () => (active ? 'Aktif' : 'Nonaktif')
      )
    }
  },
  {
    id: 'actions',
    header: 'Aksi'
  }
]

// ── Form ──────────────────────────────────────────────────────

const modalOpen = ref(false)
const editingId = ref<string | null>(null)
const detailModalOpen = ref(false)
const detailLoading = ref(false)
const detailData = ref<Record<string, unknown> | null>(null)

interface AccountDetail {
  id: string
  code: string
  name: string
  type: string
  description: string | null
  is_active: boolean
  total_debit: number
  total_credit: number
  balance: number
  journal_count: number
  recent_journals: Array<{
    id: string
    entry_number: string
    entry_date: string
    description: string
    debit: number
    credit: number
  }>
}

async function openDetail(account: AccountingAccount) {
  detailLoading.value = true
  detailModalOpen.value = true
  try {
    const data = await get<AccountDetail>(`/accounting/accounts/${account.id}/detail`)
    detailData.value = data as unknown as Record<string, unknown>
  } catch {
    toast.add({
      title: 'Gagal',
      description: 'Gagal memuat detail akun',
      icon: 'i-lucide-alert-triangle',
      color: 'error'
    })
    detailModalOpen.value = false
  } finally {
    detailLoading.value = false
  }
}

const form = reactive({
  code: '',
  name: '',
  type: 'asset' as AccountType,
  description: '',
  is_active: true
})

function openCreate() {
  editingId.value = null
  form.code = ''
  form.name = ''
  form.type = 'asset'
  form.description = ''
  form.is_active = true
  modalOpen.value = true
}

function openEdit(account: AccountingAccount) {
  editingId.value = account.id
  form.code = account.code
  form.name = account.name
  form.type = account.type
  form.description = account.description ?? ''
  form.is_active = account.is_active
  modalOpen.value = true
}

async function onSubmit() {
  try {
    if (loading.value) return
    loading.value = true

    const body = {
      code: form.code.trim(),
      name: form.name.trim(),
      type: form.type,
      description: form.description.trim() || null,
      is_active: form.is_active
    }

    if (editingId.value) {
      await put(`/accounting/accounts/${editingId.value}`, body)
      toast.add({
        title: 'Berhasil',
        description: 'Akun berhasil diperbarui',
        icon: 'i-lucide-check-circle',
        color: 'success'
      })
    } else {
      await post('/accounting/accounts', body)
      toast.add({
        title: 'Berhasil',
        description: 'Akun berhasil dibuat',
        icon: 'i-lucide-check-circle',
        color: 'success'
      })
    }

    modalOpen.value = false
    refresh()
  } catch (err) {
    toast.add({
      title: 'Gagal',
      description: err instanceof Error ? err.message : 'Terjadi kesalahan',
      icon: 'i-lucide-alert-triangle',
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}

definePageMeta({ layout: 'accounting' })
</script>

<template>
  <UDashboardPanel id="accounting-akun">
    <template #header>
      <UDashboardNavbar :ui="{ right: 'gap-2' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">
              Bagan Akun
            </p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Daftar akun untuk jurnal umum
            </p>
          </div>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-4 lg:p-6">
        <section class="flex flex-col lg:gap-4">
          <div class="flex flex-col gap-3">
            <div class="flex flex-wrap items-end gap-3">
              <UInput
                v-model="search"
                icon="i-lucide-search"
                placeholder="Cari kode atau nama akun..."
                class="w-full sm:w-64"
              />
              <USelect
                v-model="typeFilter"
                :items="typeOptions"
                value-key="value"
                placeholder="Filter jenis"
                class="w-full sm:w-40"
              />
            </div>
            <div class="flex flex-wrap justify-end gap-2">
              <UDropdownMenu
                :items="[
                  { type: 'label', label: 'Ekspor Data' },
                  { type: 'separator' },
                  {
                    label: 'Ekspor ke Excel',
                    icon: 'i-lucide-file-spreadsheet',
                    onSelect: () => onExport('excel')
                  },
                  {
                    label: 'Ekspor ke PDF',
                    icon: 'i-lucide-file-text',
                    onSelect: () => onExport('pdf')
                  },
                  {
                    label: 'Ekspor ke CSV',
                    icon: 'i-lucide-file-down',
                    onSelect: () => onExport('csv')
                  }
                ]"
              >
                <UButton
                  icon="i-lucide-download"
                  color="neutral"
                  variant="soft"
                >
                  Export
                </UButton>
              </UDropdownMenu>
              <UButton icon="i-lucide-plus" color="primary" @click="openCreate">
                Tambah Akun
              </UButton>
            </div>
          </div>

          <UCard>
            <div v-if="pending" class="divide-y divide-default">
              <USkeleton v-for="i in 5" :key="i" class="my-3 h-12 rounded-lg" />
            </div>
            <UTable
              v-else
              :data="pagedAccounts"
              :columns="columns"
              :ui="{
                base: 'table-fixed border-separate border-spacing-0',
                thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
                tbody: '[&>tr]:last:[&>td]:border-b-0',
                th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
                td: 'border-b border-default'
              }"
            >
              <template #actions-cell="{ row }">
                <div class="flex items-center gap-1">
                  <UButton
                    icon="i-lucide-eye"
                    size="sm"
                    color="primary"
                    variant="ghost"
                    @click="openDetail(row.original)"
                  >
                    Detail
                  </UButton>
                  <UButton
                    icon="i-lucide-pencil"
                    size="sm"
                    color="neutral"
                    variant="ghost"
                    @click="openEdit(row.original)"
                  >
                    Edit
                  </UButton>
                </div>
              </template>
            </UTable>
            <div
              v-if="accounts.length > PAGE_SIZE"
              class="flex justify-end border-t border-default pt-4 px-4"
            >
              <UPagination
                v-model="page"
                :items-per-page="PAGE_SIZE"
                :total="accounts.length"
              />
            </div>
          </UCard>

          <UModal v-model:open="modalOpen" :ui="{ content: 'max-w-lg' }">
            <template #title>
              <h3 class="font-semibold">
                {{ editingId ? "Ubah Akun" : "Tambah Akun" }}
              </h3>
            </template>

            <template #body>
              <div class="space-y-4">
                <UFormField label="Kode Akun" required>
                  <UInput v-model="form.code" placeholder="Contoh: 1100" />
                </UFormField>
                <UFormField label="Nama Akun" required>
                  <UInput v-model="form.name" placeholder="Contoh: Kas" />
                </UFormField>
                <UFormField label="Jenis Akun" required>
                  <USelect
                    v-model="form.type"
                    :items="typeOptions"
                    value-key="value"
                  />
                </UFormField>
                <UFormField label="Deskripsi">
                  <UTextarea v-model="form.description" />
                </UFormField>
                <UCheckbox v-model="form.is_active" label="Akun aktif" />
              </div>
            </template>

            <template #footer>
              <div class="flex justify-end gap-2">
                <UButton
                  :loading="loading"
                  icon="i-lucide-save"
                  @click="onSubmit"
                >
                  Simpan
                </UButton>

                <UButton
                  color="neutral"
                  variant="ghost"
                  @click="modalOpen = false"
                >
                  Batal
                </UButton>
              </div>
            </template>
          </UModal>

          <UModal v-model:open="detailModalOpen" :ui="{ content: 'max-w-4xl' }">
            <template #title>
              <h3 class="font-semibold">
                Detail Akun
              </h3>
            </template>

            <template #body>
              <div v-if="detailLoading" class="space-y-3">
                <USkeleton v-for="i in 5" :key="i" class="h-8 rounded-lg" />
              </div>
              <div v-else-if="detailData" class="space-y-6">
                <!-- Info Akun -->
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <UCard :ui="{ body: 'py-3' }">
                    <p class="text-xs text-neutral-500">
                      Kode
                    </p>
                    <p class="text-lg font-bold">
                      {{ detailData.code }}
                    </p>
                  </UCard>
                  <UCard :ui="{ body: 'py-3' }">
                    <p class="text-xs text-neutral-500">
                      Nama Akun
                    </p>
                    <p class="text-lg font-bold truncate">
                      {{ detailData.name }}
                    </p>
                  </UCard>
                  <UCard :ui="{ body: 'py-3' }">
                    <p class="text-xs text-neutral-500">
                      Jenis
                    </p>
                    <UBadge variant="soft" :color="typeColor(detailData.type as string)" class="capitalize mt-1">
                      {{ typeLabel(detailData.type as string) }}
                    </UBadge>
                  </UCard>
                  <UCard :ui="{ body: 'py-3' }">
                    <p class="text-xs text-neutral-500">
                      Status
                    </p>
                    <UBadge variant="soft" :color="detailData.is_active ? 'success' : 'neutral'" class="mt-1">
                      {{ detailData.is_active ? 'Aktif' : 'Nonaktif' }}
                    </UBadge>
                  </UCard>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <UCard color="info" variant="subtle" :ui="{ body: 'py-3' }">
                    <p class="text-xs text-neutral-500">
                      Total Debit
                    </p>
                    <p class="text-xl font-bold">
                      {{ formatCurrency(detailData.total_debit as number) }}
                    </p>
                  </UCard>
                  <UCard color="warning" variant="subtle" :ui="{ body: 'py-3' }">
                    <p class="text-xs text-neutral-500">
                      Total Kredit
                    </p>
                    <p class="text-xl font-bold">
                      {{ formatCurrency(detailData.total_credit as number) }}
                    </p>
                  </UCard>
                  <UCard color="primary" variant="subtle" :ui="{ body: 'py-3' }">
                    <p class="text-xs text-neutral-500">
                      Saldo
                    </p>
                    <p class="text-xl font-bold">
                      {{ formatCurrency(detailData.balance as number) }}
                    </p>
                  </UCard>
                </div>

                <div v-if="detailData.description" class="text-sm">
                  <span class="font-medium">Deskripsi:</span>
                  {{ detailData.description }}
                </div>

                <!-- Recent Journals -->
                <div>
                  <div class="flex items-center justify-between mb-3">
                    <p class="text-sm font-medium">
                      Jurnal Terkait ({{ detailData.journal_count }} baris)
                    </p>
                  </div>
                  <UTable
                    v-if="(detailData.recent_journals as Array<unknown>).length > 0"
                    :data="detailData.recent_journals as Array<Record<string, unknown>>"
                    :columns="[
                      { accessorKey: 'entry_number', header: 'Nomor Jurnal' },
                      { accessorKey: 'entry_date',
                        header: 'Tanggal',
                        cell: ({ row }) => formatDate(row.getValue('entry_date') as string) },
                      { accessorKey: 'description', header: 'Deskripsi' },
                      { accessorKey: 'debit',
                        header: 'Debit',
                        cell: ({ row }) => formatCurrency(row.getValue('debit') as number) },
                      { accessorKey: 'credit',
                        header: 'Kredit',
                        cell: ({ row }) => formatCurrency(row.getValue('credit') as number) }
                    ]"
                  />
                  <p v-else class="text-sm text-neutral-500">
                    Belum ada jurnal untuk akun ini.
                  </p>
                </div>
              </div>
            </template>

            <template #footer>
              <div class="flex justify-end">
                <UButton
                  color="neutral"
                  variant="ghost"
                  @click="detailModalOpen = false"
                >
                  Tutup
                </UButton>
              </div>
            </template>
          </UModal>
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>
