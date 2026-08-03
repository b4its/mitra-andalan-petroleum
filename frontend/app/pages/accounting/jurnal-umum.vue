<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { ExportColumn } from '~/composables/useExport'
import type {
  AccountingAccount,
  AccountingJournal,
  AccountingJournalPost
} from '~/types/accounting'

const { get, post } = useApi()
const toast = useToast()
const loading = ref(false)
const search = ref('')
const debouncedSearch = refDebounced(search, 300)

const { toCSV, toExcel, toPDF } = useExport()

const exportColumns: ExportColumn[] = [
  { header: 'Nomor Jurnal', accessor: (row: AccountingJournal) => row.entry_number },
  { header: 'Tanggal', accessor: (row: AccountingJournal) => formatDate(row.entry_date) },
  { header: 'Deskripsi', accessor: (row: AccountingJournal) => row.description },
  { header: 'Nominal', accessor: (row: AccountingJournal) => totalDebit(row) }
]

function onExport(format: 'excel' | 'pdf' | 'csv') {
  const filename = `jurnal-umum-${new Date().toISOString().slice(0, 10)}`
  if (format === 'excel') toExcel(filename, 'Jurnal Umum', exportColumns, journals.value)
  else if (format === 'pdf') toPDF(filename, 'Jurnal Umum', exportColumns, journals.value, { subtitle: 'Catatan transaksi keuangan (debit & kredit)' })
  else toCSV(filename, exportColumns, journals.value)
}

const { data: journals, refresh } = await useAsyncData(
  'accounting-journals',
  async () => {
    const params: Record<string, string | number> = { page: 1, page_size: 50 }
    if (debouncedSearch.value) params.search = debouncedSearch.value
    const res = await get<{ items: AccountingJournal[] }>(
      '/accounting/journal',
      params
    )
    return res.items
  },
  { default: () => [], watch: [debouncedSearch], server: false }
)

const { data: accounts } = await useAsyncData(
  'accounting-accounts-options',
  () => get<AccountingAccount[]>('/accounting/accounts'),
  { default: () => [], server: false }
)

const accountItems = computed(() =>
  accounts.value.map(account => ({
    label: `${account.code} · ${account.name}`,
    value: account.id
  }))
)

const totalDebit = (journal: AccountingJournal) =>
  journal.lines.reduce((sum, line) => sum + (line.debit || 0), 0)

const columns: TableColumn<AccountingJournal>[] = [
  {
    accessorKey: 'entry_number',
    header: 'Nomor Jurnal',
    cell: ({ row }) => `${row.getValue('entry_number')}`
  },
  {
    accessorKey: 'entry_date',
    header: 'Tanggal',
    meta: {
      class: { th: 'text-center', td: 'text-center' }
    },
    cell: ({ row }) => `${formatDate(row.getValue('entry_date'))}`
  },
  {
    accessorKey: 'description',
    header: 'Deskripsi',
    cell: ({ row }) => {
      const desc = row.getValue('description') as string
      return h(
        'div',
        { class: 'flex flex-col gap-1' },
        [
          h('span', { class: 'truncate max-w-64' }, desc),
          h(
            'span',
            { class: 'text-xs text-neutral-500 dark:text-neutral-400' },
            row.original.lines
              .map(line => line.account_code)
              .join(', ')
          )
        ]
      )
    }
  },
  {
    accessorKey: 'amount',
    header: 'Nominal',
    meta: {
      class: { th: 'text-right', td: 'text-right' }
    },
    cell: ({ row }) => `${formatCurrency(totalDebit(row.original))}`
  },
  {
    id: 'actions',
    header: 'Aksi'
  }
]

// ── Form ──────────────────────────────────────────────────────

const modalOpen = ref(false)
const detailId = ref<string | null>(null)
const form = reactive({
  entry_date: new Date().toISOString().slice(0, 10),
  description: '',
  reference: '',
  lines: [
    { account_id: undefined as string | undefined, description: '', debit: 0, credit: 0 },
    { account_id: undefined as string | undefined, description: '', debit: 0, credit: 0 }
  ]
})

function openCreate() {
  form.entry_date = new Date().toISOString().slice(0, 10)
  form.description = ''
  form.reference = ''
  form.lines = [
    { account_id: undefined as string | undefined, description: '', debit: 0, credit: 0 },
    { account_id: undefined as string | undefined, description: '', debit: 0, credit: 0 }
  ]
  modalOpen.value = true
}

function addLine() {
  form.lines.push({ account_id: undefined as string | undefined, description: '', debit: 0, credit: 0 })
}

function removeLine(index: number) {
  if (form.lines.length > 2) form.lines.splice(index, 1)
}

const formTotalDebit = computed(() =>
  form.lines.reduce((sum, line) => sum + (Number(line.debit) || 0), 0)
)
const formTotalCredit = computed(() =>
  form.lines.reduce((sum, line) => sum + (Number(line.credit) || 0), 0)
)
const isBalanced = computed(() =>
  formTotalDebit.value > 0 && formTotalDebit.value === formTotalCredit.value
)

async function onSubmit() {
  try {
    if (loading.value) return
    if (!isBalanced.value) {
      toast.add({
        title: 'Tidak Balance',
        description: 'Total debit harus sama dengan total credit dan lebih dari 0',
        icon: 'i-lucide-alert-triangle',
        color: 'warning'
      })
      return
    }

    loading.value = true

    const body: AccountingJournalPost = {
      entry_date: form.entry_date,
      description: form.description.trim(),
      reference: form.reference.trim() || null,
      lines: form.lines
        .filter(line => line.account_id)
        .map(line => ({
          account_id: line.account_id as string,
          description: line.description.trim() || null,
          debit: Number(line.debit) || 0,
          credit: Number(line.credit) || 0
        }))
    }

    await post<AccountingJournal, AccountingJournalPost>('/accounting/journal', body)

    toast.add({
      title: 'Berhasil',
      description: 'Jurnal berhasil dibuat',
      icon: 'i-lucide-check-circle',
      color: 'success'
    })

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
  <UDashboardPanel id="accounting-jurnal">
    <template #header>
      <UDashboardNavbar :ui="{ right: 'gap-2' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">Jurnal Umum</p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Catatan transaksi keuangan (debit & kredit)
            </p>
          </div>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-4 lg:p-6">
        <section class="flex flex-col lg:gap-4">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="flex items-center gap-2">
              <UInput
                v-model="search"
                icon="i-lucide-search"
                placeholder="Cari nomor atau deskripsi..."
                class="w-64"
              />
              <UDropdownMenu
                :items="[
                  { type: 'label', label: 'Export Data' },
                  { type: 'separator' },
                  { label: 'Export to Excel', icon: 'i-lucide-file-spreadsheet', onSelect: () => onExport('excel') },
                  { label: 'Export to PDF', icon: 'i-lucide-file-text', onSelect: () => onExport('pdf') },
                  { label: 'Export to CSV', icon: 'i-lucide-file-down', onSelect: () => onExport('csv') }
                ]"
              >
                <UButton icon="i-lucide-download" color="neutral" variant="soft">
                  Export
                </UButton>
              </UDropdownMenu>
              <UButton
                icon="i-lucide-plus"
                color="primary"
                @click="openCreate"
              >
                Buat Jurnal
              </UButton>
            </div>
          </div>

    <UCard>
      <UTable
        :data="journals"
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
          <UButton
            icon="i-lucide-eye"
            size="sm"
            color="neutral"
            variant="ghost"
            @click="detailId = row.original.id"
          >
            Detail
          </UButton>
        </template>
      </UTable>
    </UCard>

    <UModal v-model:open="modalOpen" :ui="{ content: 'max-w-3xl' }">
      <template #title>
        <h3 class="font-semibold">
          Buat Jurnal Umum
        </h3>
      </template>

      <template #body>
        <div class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <UFormField label="Tanggal Jurnal" required>
              <UInput v-model="form.entry_date" type="date" />
            </UFormField>
            <UFormField label="Referensi">
              <UInput v-model="form.reference" placeholder="Contoh: INV/2026/VII/001" />
            </UFormField>
          </div>
          <UFormField label="Deskripsi" required>
            <UInput v-model="form.description" placeholder="Deskripsi jurnal..." />
          </UFormField>

          <div>
            <div class="flex items-center justify-between mb-2">
              <p class="text-sm font-medium">
                Baris Jurnal
              </p>
              <UButton
                icon="i-lucide-plus"
                size="sm"
                color="neutral"
                variant="soft"
                @click="addLine"
              >
                Tambah Baris
              </UButton>
            </div>

            <div class="flex flex-col gap-2">
              <div
                v-for="(line, index) in form.lines"
                :key="index"
                class="flex flex-wrap items-center gap-2"
              >
                <USelect
                  v-model="line.account_id"
                  :items="accountItems"
                  value-key="value"
                  placeholder="Pilih akun"
                  class="w-56"
                />
                <UInput
                  v-model="line.description"
                  placeholder="Keterangan"
                  class="w-40"
                />
                <UInput
                  v-model.number="line.debit"
                  type="number"
                  placeholder="Debit"
                  class="w-28"
                />
                <UInput
                  v-model.number="line.credit"
                  type="number"
                  placeholder="Kredit"
                  class="w-28"
                />
                <UButton
                  icon="i-lucide-trash"
                  color="error"
                  variant="ghost"
                  size="sm"
                  :disabled="form.lines.length <= 2"
                  @click="removeLine(index)"
                />
              </div>
            </div>

            <div
              class="mt-3 flex flex-wrap items-center gap-3 rounded-lg bg-elevated/50 px-3 py-2 text-sm"
            >
              <span class="font-medium">Total Debit: {{ formatCurrency(formTotalDebit) }}</span>
              <span class="font-medium">Total Kredit: {{ formatCurrency(formTotalCredit) }}</span>
              <UBadge
                variant="soft"
                :color="isBalanced ? 'success' : 'warning'"
              >
                {{ isBalanced ? 'Balance' : 'Tidak Balance' }}
              </UBadge>
            </div>
          </div>
        </div>
      </template>

      <template #footer>
        <div class="flex justify-between items-center gap-2">
          <UButton
            color="neutral"
            variant="ghost"
            @click="modalOpen = false"
          >
            Batal
          </UButton>
          <UButton
            :loading="loading"
            icon="i-lucide-save"
            @click="onSubmit"
          >
            Simpan Jurnal
          </UButton>
        </div>
      </template>
    </UModal>

    <UModal
      :open="detailId !== null"
      @update:open="(value: boolean) => { if (!value) detailId = null }"
    >
      <template #title>
        <h3 class="font-semibold">
          Detail Jurnal
        </h3>
      </template>

      <template #body>
        <div v-if="detailId" class="space-y-4">
          <div class="space-y-1 text-sm">
            <p>
              <span class="font-medium">Nomor:</span>
              {{ journals.find((j) => j.id === detailId)?.entry_number }}
            </p>
            <p>
              <span class="font-medium">Tanggal:</span>
              {{ formatDate(journals.find((j) => j.id === detailId)?.entry_date ?? '') }}
            </p>
            <p>
              <span class="font-medium">Deskripsi:</span>
              {{ journals.find((j) => j.id === detailId)?.description }}
            </p>
          </div>

          <UTable
            :data="journals.find((j) => j.id === detailId)?.lines ?? []"
            :columns="[
              { accessorKey: 'account_code', header: 'Akun' },
              { accessorKey: 'description', header: 'Keterangan' },
              {
                accessorKey: 'debit',
                header: 'Debit',
                cell: ({ row }) => formatCurrency(row.getValue('debit') || 0)
              },
              {
                accessorKey: 'credit',
                header: 'Kredit',
                cell: ({ row }) => formatCurrency(row.getValue('credit') || 0)
              }
            ]"
          />
        </div>
      </template>

      <template #footer>
        <div class="flex justify-end">
          <UButton
            color="neutral"
            variant="ghost"
            @click="detailId = null"
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
