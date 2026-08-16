<script setup lang="ts">
import { h } from 'vue'
import * as z from 'zod'
import type { TableColumn, FormSubmitEvent } from '@nuxt/ui'
import { formatNPWP } from '~/utils'

definePageMeta({ layout: 'admin' })

const toast = useToast()
const { get, post, put, del } = useApi()

// ── Tipe lokal ────────────────────────────────────────────────
interface Supplier {
  id: string
  name: string
  npwp: string | null
  address: string | null
  province: string | null
  city: string | null
  phone: string | null
  phone2: string | null
  email: string | null
  bank_name: string | null
  bank_account: string | null
}

// ── Data fetch ────────────────────────────────────────────────
const {
  data: suppliers,
  pending,
  refresh
} = await useAsyncData<Supplier[]>(
  'admin-suppliers',
  () => get<Supplier[]>('/suppliers'),
  { default: () => [], lazy: true }
)

// ── Search (frontend) ─────────────────────────────────────────
const search = ref('')
const page = ref(1)
const PAGE_SIZE = 8

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  const list = suppliers.value ?? []
  if (!q) return list
  return list.filter(
    s =>
      s.name.toLowerCase().includes(q)
      || (s.npwp ?? '').toLowerCase().includes(q)
      || (s.email ?? '').toLowerCase().includes(q)
      || (s.phone ?? '').toLowerCase().includes(q)
      || (s.phone2 ?? '').toLowerCase().includes(q)
      || (s.address ?? '').toLowerCase().includes(q)
      || (s.province ?? '').toLowerCase().includes(q)
      || (s.city ?? '').toLowerCase().includes(q)
      || (s.bank_name ?? '').toLowerCase().includes(q)
      || (s.bank_account ?? '').toLowerCase().includes(q)
  )
})

const paged = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE
  return filtered.value.slice(start, start + PAGE_SIZE)
})

watch(search, () => {
  page.value = 1
})

// ── Kolom tabel ───────────────────────────────────────────────
const columns: TableColumn<Supplier>[] = [
  { accessorKey: 'name', header: 'Nama' },
  {
    accessorKey: 'npwp',
    header: 'NPWP',
    cell: ({ row }) => formatNPWP(row.getValue('npwp')) || '-'
  },
  {
    accessorKey: 'email',
    header: 'Email',
    cell: ({ row }) => row.getValue('email') || '-'
  },
  {
    accessorKey: 'phone',
    header: 'Telepon',
    cell: ({ row }) => row.getValue('phone') || '-'
  },
  {
    accessorKey: 'bank_name',
    header: 'Bank',
    cell: ({ row }) => {
      const bank = row.getValue('bank_name') as string
      const acc = (row.original as Supplier).bank_account as string
      return bank || acc ? `${bank || '-'}${bank && acc ? ' · ' : ''}${acc || ''}` : '-'
    }
  },
  {
    accessorKey: 'province',
    header: 'Provinsi',
    cell: ({ row }) => row.getValue('province') || '-'
  },
  {
    accessorKey: 'city',
    header: 'Kota',
    cell: ({ row }) => row.getValue('city') || '-'
  },
  {
    accessorKey: 'address',
    header: 'Alamat',
    cell: ({ row }) => {
      const a = row.getValue('address') as string
      return a ? h('span', { class: 'block max-w-xs truncate' }, a) : '-'
    }
  },
  { id: 'actions', header: 'Aksi' }
]

// ── Modal states ──────────────────────────────────────────────
type ModalMode = 'view' | 'add' | 'edit'
const modalOpen = ref(false)
const modalMode = ref<ModalMode>('add')
const selectedSupplier = ref<Supplier | null>(null)

// ── Form schema ───────────────────────────────────────────────
const schema = z.object({
  name: z.string().min(2, 'Minimal 2 karakter'),
  npwp: z.string().optional(),
  address: z.string().optional(),
  province: z.string().optional(),
  city: z.string().optional(),
  phone: z.string().optional(),
  phone2: z.string().optional(),
  email: z.string().email('Email tidak valid').optional().or(z.literal('')),
  bank_name: z.string().optional(),
  bank_account: z.string().optional()
})

type Schema = z.output<typeof schema>

const formState = reactive({
  name: '',
  npwp: '',
  address: '',
  province: '',
  city: '',
  phone: '',
  phone2: '',
  email: '',
  bank_name: '',
  bank_account: ''
})

const baseStreet = ref('')

watch(
  () => formState.address,
  (value) => {
    const suffix = [formState.city, formState.province]
      .filter(Boolean)
      .join(', ')
    if (suffix && value && value.endsWith(suffix)) {
      baseStreet.value = value
        .slice(0, value.length - suffix.length)
        .replace(/[, ]+$/, '')
    } else {
      baseStreet.value = value
    }
  }
)

watch([() => formState.province, () => formState.city], () => {
  if (formState.city) {
    formState.address = [
      baseStreet.value,
      formState.city,
      formState.province
    ]
      .filter(Boolean)
      .join(', ')
  }
})

const saving = ref(false)

// ── Helpers ───────────────────────────────────────────────────
function openAdd() {
  modalMode.value = 'add'
  selectedSupplier.value = null
  formState.name = ''
  formState.npwp = ''
  formState.address = ''
  formState.province = ''
  formState.city = ''
  formState.phone = ''
  formState.phone2 = ''
  formState.email = ''
  formState.bank_name = ''
  formState.bank_account = ''
  modalOpen.value = true
}

function openView(supplier: Supplier) {
  modalMode.value = 'view'
  selectedSupplier.value = supplier
  modalOpen.value = true
}

function openEdit(supplier: Supplier) {
  modalMode.value = 'edit'
  selectedSupplier.value = supplier
  formState.name = supplier.name
  formState.npwp = formatNPWP(supplier.npwp ?? '')
  formState.address = supplier.address ?? ''
  formState.province = supplier.province ?? ''
  formState.city = supplier.city ?? ''
  formState.phone = supplier.phone ?? ''
  formState.phone2 = supplier.phone2 ?? ''
  formState.email = supplier.email ?? ''
  formState.bank_name = supplier.bank_name ?? ''
  formState.bank_account = supplier.bank_account ?? ''
  modalOpen.value = true
}

// ── Submit add ────────────────────────────────────────────────
async function onSubmitAdd(event: FormSubmitEvent<Schema>) {
  if (saving.value) return
  saving.value = true
  try {
    const npwp = (event.data.npwp ?? '').replace(/\D/g, '')
    if (npwp && npwp.length !== 15) {
      toast.add({ title: 'NPWP harus 15 digit', description: 'Contoh: 00.000.000.0-000.000', color: 'warning' })
      saving.value = false
      return
    }
    const payload = {
      name: event.data.name,
      npwp: npwp || null,
      address: event.data.address || null,
      province: event.data.province || null,
      city: event.data.city || null,
      phone: event.data.phone || null,
      phone2: event.data.phone2 || null,
      email: event.data.email || null,
      bank_name: event.data.bank_name || null,
      bank_account: event.data.bank_account || null
    }
    await post<Supplier, typeof payload>('/suppliers', payload)
    toast.add({
      title: 'Berhasil',
      description: 'Supplier baru berhasil ditambahkan.',
      color: 'success'
    })
    modalOpen.value = false
    refresh()
  } catch (err: unknown) {
    toast.add({
      title: 'Gagal',
      description: (err as Error).message || 'Gagal menambahkan supplier.',
      color: 'error'
    })
  } finally {
    saving.value = false
  }
}

// ── Submit edit ───────────────────────────────────────────────
async function onSubmitEdit(event: FormSubmitEvent<Schema>) {
  if (saving.value || !selectedSupplier.value) return
  saving.value = true
  try {
    const npwp = (event.data.npwp ?? '').replace(/\D/g, '')
    if (npwp && npwp.length !== 15) {
      toast.add({ title: 'NPWP harus 15 digit', description: 'Contoh: 00.000.000.0-000.000', color: 'warning' })
      saving.value = false
      return
    }
    const payload = {
      name: event.data.name,
      npwp: npwp || null,
      address: event.data.address || null,
      province: event.data.province || null,
      city: event.data.city || null,
      phone: event.data.phone || null,
      phone2: event.data.phone2 || null,
      email: event.data.email || null,
      bank_name: event.data.bank_name || null,
      bank_account: event.data.bank_account || null
    }
    await put<Supplier, typeof payload>(
      `/suppliers/${selectedSupplier.value.id}`,
      payload
    )
    toast.add({
      title: 'Berhasil',
      description: 'Data supplier berhasil diperbarui.',
      color: 'success'
    })
    modalOpen.value = false
    refresh()
  } catch (err: unknown) {
    toast.add({
      title: 'Gagal',
      description: (err as Error).message || 'Gagal memperbarui supplier.',
      color: 'error'
    })
  } finally {
    saving.value = false
  }
}

// ── Delete ────────────────────────────────────────────────────
const deleteTarget = ref<Supplier | null>(null)
const deleteOpen = ref(false)
const deleting = ref(false)

function openDelete(supplier: Supplier) {
  deleteTarget.value = supplier
  deleteOpen.value = true
}

async function confirmDelete() {
  if (deleting.value || !deleteTarget.value) return
  deleting.value = true
  try {
    await del(`/suppliers/${deleteTarget.value.id}`)
    toast.add({ title: 'Berhasil', description: `Supplier ${deleteTarget.value.name} berhasil dihapus.`, color: 'success' })
    deleteOpen.value = false
    deleteTarget.value = null
    refresh()
  } catch (err: unknown) {
    toast.add({
      title: 'Gagal',
      description: (err as Error).message || 'Gagal menghapus supplier.',
      color: 'error'
    })
  } finally {
    deleting.value = false
  }
}

// ── Modal title ───────────────────────────────────────────────
const modalTitle = computed(() => {
  if (modalMode.value === 'add') return 'Tambah Supplier Baru'
  if (modalMode.value === 'edit')
    return `Edit Supplier — ${selectedSupplier.value?.name ?? ''}`
  return `Detail Supplier — ${selectedSupplier.value?.name ?? ''}`
})
</script>

<template>
  <UDashboardPanel id="admin-suppliers">
    <template #header>
      <UDashboardNavbar title="Manajemen Supplier" :ui="{ right: 'gap-2' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #right>
          <UButton
            icon="i-lucide-refresh-cw"
            color="neutral"
            variant="ghost"
            @click="refresh()"
          />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="space-y-5 p-4 lg:p-6">
        <!-- Toolbar: search + add -->
        <div class="flex flex-wrap items-center justify-between gap-3">
          <UInput
            v-model="search"
            icon="i-lucide-search"
            placeholder="Cari nama, email, telepon, alamat..."
            class="w-72"
          />
          <UButton icon="i-lucide-circle-plus" color="primary" @click="openAdd">
            Tambah Supplier
          </UButton>
        </div>

        <!-- Skeleton -->
        <div v-if="pending" class="space-y-3">
          <USkeleton v-for="i in 5" :key="i" class="h-12 rounded-lg" />
        </div>

        <!-- Tabel -->
        <UCard v-else>
          <UTable :data="paged" :columns="columns">
            <template #actions-cell="{ row }">
              <div class="flex items-center gap-2">
                <UButton
                  icon="i-lucide-eye"
                  size="xs"
                  color="neutral"
                  variant="ghost"
                  aria-label="Lihat detail"
                  @click="openView(row.original)"
                />
                <UButton
                  icon="i-lucide-pencil"
                  size="xs"
                  color="primary"
                  variant="ghost"
                  aria-label="Ubah supplier"
                  @click="openEdit(row.original)"
                />
                <UButton
                  icon="i-lucide-trash-2"
                  size="xs"
                  color="error"
                  variant="ghost"
                  aria-label="Hapus supplier"
                  @click="openDelete(row.original)"
                />
              </div>
            </template>
          </UTable>
          <UEmpty
            v-if="!paged.length && !pending"
            icon="i-lucide-building-2"
            title="Tidak ada supplier"
            description="Belum ada supplier yang cocok dengan pencarian."
          />
          <div
            class="flex items-center justify-between border-t border-default px-2 pt-3 mt-2"
          >
            <span class="text-xs text-muted">
              {{ filtered.length }} supplier{{ search ? " ditemukan" : "" }}
            </span>
            <UPagination
              v-if="filtered.length > PAGE_SIZE"
              v-model:page="page"
              :total="filtered.length"
              :items-per-page="PAGE_SIZE"
            />
          </div>
        </UCard>
      </div>
    </template>
  </UDashboardPanel>

  <!-- ── Modal Add / Edit / View ── -->
  <UModal v-model:open="modalOpen" :ui="{ content: 'max-w-xl' }">
    <template #title>
      {{ modalTitle }}
    </template>

    <template #body>
      <!-- VIEW mode -->
      <div v-if="modalMode === 'view' && selectedSupplier" class="space-y-4">
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Nama
            </p>
            <p class="font-medium">
              {{ selectedSupplier.name }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              NPWP
            </p>
            <p class="font-medium">
              {{ formatNPWP(selectedSupplier.npwp) || "-" }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Email
            </p>
            <p class="font-medium">
              {{ selectedSupplier.email || "-" }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Telepon
            </p>
            <p class="font-medium">
              {{ selectedSupplier.phone || "-" }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Telepon 2 (PIC)
            </p>
            <p class="font-medium">
              {{ selectedSupplier.phone2 || "-" }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Bank
            </p>
            <p class="font-medium">
              {{ selectedSupplier.bank_name || "-" }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              No. Rekening
            </p>
            <p class="font-medium">
              {{ selectedSupplier.bank_account || "-" }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Provinsi
            </p>
            <p class="font-medium">
              {{ selectedSupplier.province || "-" }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Kota
            </p>
            <p class="font-medium">
              {{ selectedSupplier.city || "-" }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              ID
            </p>
            <p class="font-mono text-xs text-muted truncate">
              {{ selectedSupplier.id }}
            </p>
          </div>
          <div class="col-span-2">
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Alamat
            </p>
            <p class="font-medium">
              {{ selectedSupplier.address || "-" }}
            </p>
          </div>
        </div>
      </div>

      <!-- ADD / EDIT mode -->
      <UForm
        v-else
        :id="modalMode === 'add' ? 'form-add-supplier' : 'form-edit-supplier'"
        :schema="schema"
        :state="formState"
        class="space-y-4"
        @submit="
          modalMode === 'add' ? onSubmitAdd($event) : onSubmitEdit($event)
        "
      >
        <UFormField name="name" label="Nama" required>
          <UInput
            v-model="formState.name"
            placeholder="Nama supplier"
            autocomplete="off"
          />
        </UFormField>
        <UFormField name="npwp" label="NPWP">
          <UInput
            v-model="formState.npwp"
            v-maska="'##.###.###.#-###.###'"
            inputmode="numeric"
            placeholder="00.000.000.0-000.000"
            autocomplete="off"
          />
        </UFormField>
        <UFormField name="email" label="Email">
          <UInput
            v-model="formState.email"
            type="email"
            placeholder="email@contoh.com"
            autocomplete="off"
          />
        </UFormField>
        <UFormField name="phone" label="Telepon">
          <UInput
            v-model="formState.phone"
            placeholder="08xxxxxxxxxx"
            autocomplete="off"
          />
        </UFormField>
        <UFormField name="phone2" label="Telepon 2 (PIC / Penanggung Jawab)">
          <UInput
            v-model="formState.phone2"
            placeholder="08xxxxxxxxxx"
            autocomplete="off"
          />
        </UFormField>

        <div class="rounded-lg border border-default p-3 space-y-4">
          <p class="text-sm font-semibold">
            Informasi Pembayaran
          </p>
          <UFormField name="bank_name" label="Nama Bank">
            <UInput
              v-model="formState.bank_name"
              placeholder="Contoh: BANK BCA"
              autocomplete="off"
            />
          </UFormField>
          <UFormField name="bank_account" label="No. Rekening">
            <UInput
              v-model="formState.bank_account"
              placeholder="Contoh: 8801234567"
              autocomplete="off"
            />
          </UFormField>
        </div>

        <div class="rounded-lg border border-default p-3 space-y-4">
          <p class="text-sm font-semibold">
            Wilayah
          </p>
          <WilayahLocationPicker
            v-model:province="formState.province"
            v-model:city="formState.city"
          />
        </div>

        <UFormField name="address" label="Alamat">
          <UTextarea
            v-model="formState.address"
            class="w-full"
            placeholder="Alamat lengkap"
          />
        </UFormField>
      </UForm>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          v-if="modalMode !== 'view'"
          color="primary"
          :loading="saving"
          :form="
            modalMode === 'add' ? 'form-add-supplier' : 'form-edit-supplier'
          "
          type="submit"
        >
          {{ modalMode === "add" ? "Tambah Supplier" : "Simpan Perubahan" }}
        </UButton>

        <UButton color="neutral" variant="ghost" @click="modalOpen = false">
          {{ modalMode === "view" ? "Tutup" : "Batal" }}
        </UButton>
      </div>
    </template>
  </UModal>

  <!-- ── Modal Konfirmasi Delete ── -->
  <UModal v-model:open="deleteOpen" :ui="{ content: 'max-w-md' }">
    <template #title>
      <div class="flex items-center gap-2 text-error">
        <UIcon name="i-lucide-triangle-alert" class="size-5" />
        Hapus Supplier
      </div>
    </template>
    <template #body>
      <p class="text-sm text-muted">
        Apakah Anda yakin ingin menghapus supplier
        <span class="font-semibold text-highlighted">{{
          deleteTarget?.name
        }}</span>? Tindakan ini tidak dapat dibatalkan.
      </p>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          color="neutral"
          variant="ghost"
          @click="deleteOpen = false"
        >
          Batal
        </UButton>
        <UButton color="error" :loading="deleting" @click="confirmDelete">
          Ya, Hapus
        </UButton>
      </div>
    </template>
  </UModal>
</template>
