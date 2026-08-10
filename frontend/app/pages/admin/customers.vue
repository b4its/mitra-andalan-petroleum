<script setup lang="ts">
import { h } from 'vue'
import * as z from 'zod'
import type { TableColumn, FormSubmitEvent } from '@nuxt/ui'

definePageMeta({ layout: 'admin' })

const toast = useToast()
const { get, post, put, del } = useApi()

// ── Tipe lokal ────────────────────────────────────────────────
interface Customer {
  id: string
  name: string
  npwp: string | null
  address: string | null
  phone: string | null
  email: string | null
}

// ── Data fetch ────────────────────────────────────────────────
const {
  data: customers,
  pending,
  refresh
} = await useAsyncData<Customer[]>(
  'admin-customers',
  () => get<Customer[]>('/customers'),
  { default: () => [], lazy: true }
)

// ── Search (frontend) ─────────────────────────────────────────
const search = ref('')
const page = ref(1)
const PAGE_SIZE = 8

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  const list = customers.value ?? []
  if (!q) return list
  return list.filter(
    c =>
      c.name.toLowerCase().includes(q)
      || (c.npwp ?? '').toLowerCase().includes(q)
      || (c.email ?? '').toLowerCase().includes(q)
      || (c.phone ?? '').toLowerCase().includes(q)
      || (c.address ?? '').toLowerCase().includes(q)
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
const columns: TableColumn<Customer>[] = [
  { accessorKey: 'name', header: 'Nama' },
  {
    accessorKey: 'npwp',
    header: 'NPWP',
    cell: ({ row }) => row.getValue('npwp') || '-'
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
const selectedCustomer = ref<Customer | null>(null)

// ── Form schema ───────────────────────────────────────────────
const schema = z.object({
  name: z.string().min(2, 'Minimal 2 karakter'),
  npwp: z.string().optional(),
  address: z.string().optional(),
  phone: z.string().optional(),
  email: z.string().email('Email tidak valid').optional().or(z.literal(''))
})

type Schema = z.output<typeof schema>

const formState = reactive({
  name: '',
  npwp: '',
  address: '',
  phone: '',
  email: ''
})

const saving = ref(false)

// ── Helpers ───────────────────────────────────────────────────
function openAdd() {
  modalMode.value = 'add'
  selectedCustomer.value = null
  formState.name = ''
  formState.npwp = ''
  formState.address = ''
  formState.phone = ''
  formState.email = ''
  modalOpen.value = true
}

function openView(customer: Customer) {
  modalMode.value = 'view'
  selectedCustomer.value = customer
  modalOpen.value = true
}

function openEdit(customer: Customer) {
  modalMode.value = 'edit'
  selectedCustomer.value = customer
  formState.name = customer.name
  formState.npwp = customer.npwp ?? ''
  formState.address = customer.address ?? ''
  formState.phone = customer.phone ?? ''
  formState.email = customer.email ?? ''
  modalOpen.value = true
}

// ── Submit add ────────────────────────────────────────────────
async function onSubmitAdd(event: FormSubmitEvent<Schema>) {
  if (saving.value) return
  saving.value = true
  try {
    const npwp = event.data.npwp?.trim() || ''
    if (npwp && !/^\d{2}\.\d{3}\.\d{3}\.\d{1}-\d{3}\.\d{3}$/.test(npwp)) {
      toast.add({ title: 'Format NPWP salah', description: 'Gunakan format 00.000.000.0-000.000', color: 'warning' })
      saving.value = false
      return
    }
    const payload = {
      name: event.data.name,
      npwp: npwp || null,
      address: event.data.address || null,
      phone: event.data.phone || null,
      email: event.data.email || null
    }
    await post<Customer, typeof payload>('/customers', payload)
    toast.add({
      title: 'Berhasil',
      description: 'Customer baru berhasil ditambahkan.',
      color: 'success'
    })
    modalOpen.value = false
    refresh()
  } catch (err: any) {
    toast.add({
      title: 'Error',
      description: err.message || 'Gagal menambahkan customer.',
      color: 'error'
    })
  } finally {
    saving.value = false
  }
}

// ── Submit edit ───────────────────────────────────────────────
async function onSubmitEdit(event: FormSubmitEvent<Schema>) {
  if (saving.value || !selectedCustomer.value) return
  saving.value = true
  try {
    const npwp = event.data.npwp?.trim() || ''
    if (npwp && !/^\d{2}\.\d{3}\.\d{3}\.\d{1}-\d{3}\.\d{3}$/.test(npwp)) {
      toast.add({ title: 'Format NPWP salah', description: 'Gunakan format 00.000.000.0-000.000', color: 'warning' })
      saving.value = false
      return
    }
    const payload = {
      name: event.data.name,
      npwp: npwp || null,
      address: event.data.address || null,
      phone: event.data.phone || null,
      email: event.data.email || null
    }
    await put<Customer, typeof payload>(
      `/customers/${selectedCustomer.value.id}`,
      payload
    )
    toast.add({
      title: 'Berhasil',
      description: 'Data customer berhasil diperbarui.',
      color: 'success'
    })
    modalOpen.value = false
    refresh()
  } catch (err: any) {
    toast.add({
      title: 'Error',
      description: err.message || 'Gagal memperbarui customer.',
      color: 'error'
    })
  } finally {
    saving.value = false
  }
}

// ── Delete ────────────────────────────────────────────────────
const deleteTarget = ref<Customer | null>(null)
const deleteOpen = ref(false)
const deleting = ref(false)

function openDelete(customer: Customer) {
  deleteTarget.value = customer
  deleteOpen.value = true
}

async function confirmDelete() {
  if (deleting.value || !deleteTarget.value) return
  deleting.value = true
  try {
    await del(`/customers/${deleteTarget.value.id}`)
    toast.add({ title: 'Berhasil', description: `Customer ${deleteTarget.value.name} berhasil dihapus.`, color: 'success' })
    deleteOpen.value = false
    deleteTarget.value = null
    refresh()
  } catch (err: any) {
    toast.add({
      title: 'Error',
      description: err.message || 'Gagal menghapus customer.',
      color: 'error'
    })
  } finally {
    deleting.value = false
  }
}

// ── Modal title ───────────────────────────────────────────────
const modalTitle = computed(() => {
  if (modalMode.value === 'add') return 'Tambah Customer Baru'
  if (modalMode.value === 'edit')
    return `Edit Customer — ${selectedCustomer.value?.name ?? ''}`
  return `Detail Customer — ${selectedCustomer.value?.name ?? ''}`
})
</script>

<template>
  <UDashboardPanel id="admin-customers">
    <template #header>
      <UDashboardNavbar title="Manajemen Customer" :ui="{ right: 'gap-2' }">
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
          <UButton icon="i-lucide-user-plus" color="primary" @click="openAdd">
            Tambah Customer
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
                  aria-label="Edit customer"
                  @click="openEdit(row.original)"
                />
                <UButton
                  icon="i-lucide-trash-2"
                  size="xs"
                  color="error"
                  variant="ghost"
                  aria-label="Hapus customer"
                  @click="openDelete(row.original)"
                />
              </div>
            </template>
          </UTable>
          <UEmpty
            v-if="!paged.length && !pending"
            icon="i-lucide-users"
            title="Tidak ada customer"
            description="Belum ada customer yang cocok dengan pencarian."
          />
          <div
            class="flex items-center justify-between border-t border-default px-2 pt-3 mt-2"
          >
            <span class="text-xs text-muted">
              {{ filtered.length }} customer{{ search ? " ditemukan" : "" }}
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
  <UModal v-model:open="modalOpen" :ui="{ content: 'max-w-lg' }">
    <template #title>
      {{ modalTitle }}
    </template>

    <template #body>
      <!-- VIEW mode -->
      <div v-if="modalMode === 'view' && selectedCustomer" class="space-y-4">
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Nama
            </p>
            <p class="font-medium">
              {{ selectedCustomer.name }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              NPWP
            </p>
            <p class="font-medium">
              {{ selectedCustomer.npwp || "-" }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Email
            </p>
            <p class="font-medium">
              {{ selectedCustomer.email || "-" }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Telepon
            </p>
            <p class="font-medium">
              {{ selectedCustomer.phone || "-" }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              ID
            </p>
            <p class="font-mono text-xs text-muted truncate">
              {{ selectedCustomer.id }}
            </p>
          </div>
          <div class="col-span-2">
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Alamat
            </p>
            <p class="font-medium">
              {{ selectedCustomer.address || "-" }}
            </p>
          </div>
        </div>
      </div>

      <!-- ADD / EDIT mode -->
      <UForm
        v-else
        :id="modalMode === 'add' ? 'form-add-customer' : 'form-edit-customer'"
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
            placeholder="Nama customer"
            autocomplete="off"
          />
        </UFormField>
        <UFormField name="npwp" label="NPWP">
          <UInput
            v-model="formState.npwp"
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
            modalMode === 'add' ? 'form-add-customer' : 'form-edit-customer'
          "
          type="submit"
        >
          {{ modalMode === "add" ? "Tambah Customer" : "Simpan Perubahan" }}
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
        Hapus Customer
      </div>
    </template>
    <template #body>
      <p class="text-sm text-muted">
        Apakah Anda yakin ingin menghapus customer
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
