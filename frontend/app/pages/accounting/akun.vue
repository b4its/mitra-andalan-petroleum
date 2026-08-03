<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { ExportColumn } from '~/composables/useExport'
import type {
  AccountingAccount,
  AccountType
} from '~/types/accounting'

const { get, post, put } = useApi()
const toast = useToast()
const loading = ref(false)
const search = ref('')
const debouncedSearch = refDebounced(search, 300)
const { toCSV, toExcel, toPDF } = useExport()

const exportColumns: ExportColumn[] = [
  { header: 'Kode', accessor: (row: AccountingAccount) => row.code },
  { header: 'Nama Akun', accessor: (row: AccountingAccount) => row.name },
  { header: 'Jenis', accessor: (row: AccountingAccount) => typeLabel(row.type) },
  { header: 'Status', accessor: (row: AccountingAccount) => (row.is_active ? 'Aktif' : 'Nonaktif') },
  { header: 'Deskripsi', accessor: (row: AccountingAccount) => row.description ?? '' }
]

function onExport(format: 'excel' | 'pdf' | 'csv') {
  const filename = `chart-of-accounts-${new Date().toISOString().slice(0, 10)}`
  if (format === 'excel') toExcel(filename, 'Chart of Accounts', exportColumns, accounts.value)
  else if (format === 'pdf') toPDF(filename, 'Chart of Accounts', exportColumns, accounts.value, { subtitle: 'Daftar akun untuk jurnal umum' })
  else toCSV(filename, exportColumns, accounts.value)
}

const { data: accounts, refresh } = await useAsyncData(
  'accounting-accounts',
  async () => {
    const params: Record<string, string | number | boolean> = { include_inactive: true }
    if (debouncedSearch.value) params.search = debouncedSearch.value
    const res = await get<AccountingAccount[]>('/accounting/accounts', params)
    return res
  },
  { default: () => [], watch: [debouncedSearch], server: false }
)

const typeOptions: { label: string, value: AccountType, color: string }[] = [
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
            <p class="text-base font-semibold">Chart of Accounts</p>
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
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="flex items-center gap-2">
              <UInput
                v-model="search"
                icon="i-lucide-search"
                placeholder="Cari kode atau nama akun..."
                class="w-64"
              />
              <UButton
                icon="i-lucide-plus"
                color="primary"
                @click="openCreate"
              >
                Tambah Akun
              </UButton>
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
      </div>
    </div>

    <UCard>
      <UTable
        :data="accounts"
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
            icon="i-lucide-pencil"
            size="sm"
            color="neutral"
            variant="ghost"
            @click="openEdit(row.original)"
          >
            Edit
          </UButton>
        </template>
      </UTable>
    </UCard>

    <UModal
      v-model:open="modalOpen"
      :ui="{ content: 'max-w-lg' }"
    >
      <template #title>
        <h3 class="font-semibold">
          {{ editingId ? 'Edit Akun' : 'Tambah Akun' }}
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
            <USelect v-model="form.type" :items="typeOptions" value-key="value" />
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
            Simpan
          </UButton>
        </div>
      </template>
    </UModal>
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>
