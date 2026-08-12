<script setup lang="ts">
import type {
  AccountingAccount,
  AccountingJournal,
  AccountingJournalPost
} from '~/types/accounting'

const props = defineProps<{
  open: boolean
  mode: 'income' | 'expense'
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  saved: []
}>()

const { get, post } = useApi()
const toast = useToast()
const loading = ref(false)

const modalOpen = computed({
  get: () => props.open,
  set: value => emit('update:open', value)
})

const { data: accounts, pending: pendingAccounts } = await useAsyncData(
  'accounting-entry-accounts',
  () => get<AccountingAccount[]>('/accounting/accounts'),
  { default: () => [], server: false }
)

const isIncome = computed(() => props.mode === 'income')

const categoryAccounts = computed(() =>
  accounts.value.filter(
    account =>
      account.is_active
      && (isIncome.value ? account.type === 'revenue' : account.type === 'expense')
  )
)
const cashAccounts = computed(() =>
  accounts.value.filter(account => account.is_active && account.type === 'asset')
)

const categoryItems = computed(() =>
  categoryAccounts.value.map(account => ({
    label: `${account.code} · ${account.name}`,
    value: account.id
  }))
)
const cashItems = computed(() =>
  cashAccounts.value.map(account => ({
    label: `${account.code} · ${account.name}`,
    value: account.id
  }))
)

const form = reactive({
  entry_date: new Date().toISOString().slice(0, 10),
  description: '',
  reference: '',
  category_account_id: undefined as string | undefined,
  cash_account_id: undefined as string | undefined,
  amount: 0
})

function resetForm() {
  form.entry_date = new Date().toISOString().slice(0, 10)
  form.description = ''
  form.reference = ''
  form.category_account_id = undefined
  form.cash_account_id = undefined
  form.amount = 0
}

watch(
  () => props.open,
  value => {
    if (value) resetForm()
  }
)

async function onSubmit() {
  try {
    if (loading.value) return
    const amount = Number(form.amount)
    if (
      !form.description.trim()
      || !form.category_account_id
      || !form.cash_account_id
      || !(amount > 0)
    ) {
      toast.add({
        title: 'Lengkapi Data',
        description: 'Isi deskripsi, akun, dan nominal yang valid',
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
      lines: isIncome.value
        ? [
            {
              account_id: form.cash_account_id,
              description: 'Penerimaan kas',
              debit: amount,
              credit: 0
            },
            {
              account_id: form.category_account_id,
              description: form.description.trim(),
              debit: 0,
              credit: amount
            }
          ]
        : [
            {
              account_id: form.category_account_id,
              description: form.description.trim(),
              debit: amount,
              credit: 0
            },
            {
              account_id: form.cash_account_id,
              description: 'Pengeluaran kas',
              debit: 0,
              credit: amount
            }
          ]
    }

    await post<AccountingJournal, AccountingJournalPost>(
      '/accounting/journal',
      body
    )

    toast.add({
      title: 'Berhasil',
      description: isIncome.value
        ? 'Pemasukan berhasil dicatat'
        : 'Pengeluaran berhasil dicatat',
      icon: 'i-lucide-check-circle',
      color: 'success'
    })

    modalOpen.value = false
    emit('saved')
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
</script>

<template>
  <UModal v-model:open="modalOpen">
    <template #title>
      <h3 class="font-semibold">
        {{ isIncome ? 'Tambah Pemasukan' : 'Tambah Pengeluaran' }}
      </h3>
    </template>

    <template #body>
      <div class="space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <UFormField label="Tanggal" required>
            <UInput v-model="form.entry_date" type="date" />
          </UFormField>
          <UFormField label="Referensi">
            <UInput
              v-model="form.reference"
              placeholder="Contoh: INV/2026/VII/001"
            />
          </UFormField>
        </div>

        <UFormField label="Deskripsi" required>
          <UInput
            v-model="form.description"
            :placeholder="isIncome ? 'Deskripsi pemasukan...' : 'Deskripsi pengeluaran...'"
          />
        </UFormField>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <UFormField :label="isIncome ? 'Akun Pendapatan' : 'Akun Beban'" required>
            <USelect
              v-if="!pendingAccounts"
              v-model="form.category_account_id"
              :items="categoryItems"
              value-key="value"
              :placeholder="isIncome ? 'Pilih akun pendapatan' : 'Pilih akun beban'"
            />
            <USkeleton v-else class="h-10 rounded-lg" />
          </UFormField>
          <UFormField :label="isIncome ? 'Diterima ke Akun' : 'Dibayar dari Akun'" required>
            <USelect
              v-if="!pendingAccounts"
              v-model="form.cash_account_id"
              :items="cashItems"
              value-key="value"
              placeholder="Pilih akun kas/bank"
            />
            <USkeleton v-else class="h-10 rounded-lg" />
          </UFormField>
        </div>

        <UFormField label="Nominal" required>
          <UInput v-model.number="form.amount" type="number" min="0" placeholder="0" />
        </UFormField>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-between items-center gap-2">
        <UButton :loading="loading" icon="i-lucide-save" @click="onSubmit">
          Simpan
        </UButton>
        <UButton color="neutral" variant="ghost" @click="modalOpen = false">
          Batal
        </UButton>
      </div>
    </template>
  </UModal>
</template>
