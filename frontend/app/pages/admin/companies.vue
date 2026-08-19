<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn, FormSubmitEvent } from '@nuxt/ui'
import type { Company, CompanyData } from '~/types/company'

definePageMeta({ layout: 'admin' })

const toast = useToast()
const { get, post, put, del } = useApi()

// ── Data fetch ────────────────────────────────────────────────
const {
  data: companies,
  pending,
  refresh
} = await useAsyncData<Company[]>(
  'admin-companies',
  () => get<Company[]>('/companies'),
  { default: () => [], lazy: true }
)

// ── Search (frontend) ─────────────────────────────────────────
const search = ref('')
const page = ref(1)
const PAGE_SIZE = 8

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  const list = companies.value ?? []
  if (!q) return list
  return list.filter(
    c =>
      c.name.toLowerCase().includes(q)
      || c.abbreviation.toLowerCase().includes(q)
  )
})

const paged = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE
  return filtered.value.slice(start, start + PAGE_SIZE)
})

watch(search, () => {
  page.value = 1
})

// ── Modal state ───────────────────────────────────────────────
const modalOpen = ref(false)
const editingId = ref<string | null>(null)

function openCreateModal() {
  editingId.value = null
  formName.value = ''
  formAbbreviation.value = ''
  formCompanyImage.value = null
  modalOpen.value = true
}

function openUpdateModal(company: Company) {
  editingId.value = company.id
  formName.value = company.name
  formAbbreviation.value = company.abbreviation
  formCompanyImage.value = company.company_image
  modalOpen.value = true
}

async function onSubmitForm(event: FormSubmitEvent<FormData>) {
  event.preventDefault()
  try {
    if (editingId.value) {
      // Update
      const payload: CompanyData = {
        id: editingId.value,
        name: formName.value,
        abbreviation: formAbbreviation.value,
        company_image: formCompanyImage.value
      }
      await put(`/companies/${editingId.value}`, payload)
      toast.add({
        title: 'Sukses',
        description: 'Perusahaan berhasil diperbarui'
      })
    } else {
      // Create
      const payload: Omit<CompanyData, 'id'> = {
        name: formName.value,
        abbreviation: formAbbreviation.value,
        company_image: formCompanyImage.value
      }
      await post('/companies', payload)
      toast.add({
        title: 'Sukses',
        description: 'Perusahaan baru berhasil ditambahkan'
      })
    }
    modalOpen.value = false
    refresh()
  } catch (error: any) {
    console.error(error)
    toast.add({
      title: 'Gagal',
      description: error?.response?.data?.detail || 'Terjadi kesalahan saat menyimpan data',
      color: 'danger'
    })
  }
}

async function onDelete(id: string, name: string) {
  const confirm = await useDialog().confirm({
    title: 'Konfirmasi Hapus',
    message: `Apakah Anda yakin ingin menghapus perusahaan "${name}"?`,
    actions: ['cancel', 'ok'],
    variant: 'outline',
    class: 'rounded-xl'
  })
  
  if (!confirm.ok) return
  
  try {
    await del(`/companies/${id}`)
    toast.add({
      title: 'Sukses',
      description: 'Perusahaan berhasil dihapus'
    })
    refresh()
  } catch (error: any) {
    console.error(error)
    toast.add({
      title: 'Gagal',
      description: error?.response?.data?.detail || 'Terjadi kesalahan saat menghapus data',
      color: 'danger'
    })
  }
}

// ── Form fields ───────────────────────────────────────────────
const formName = ref('')
const formAbbreviation = ref('')
const formCompanyImage = ref<string | null>(null)

// ── Columns ───────────────────────────────────────────────────
const columns: TableColumn<Company>[] = [
  { accessorKey: 'name', header: 'Nama Perusahaan' },
  { accessorKey: 'abbreviation', header: 'Singkatan' },
  {
    accessorKey: 'company_image',
    header: 'Logo',
    cell: ({ row }) => {
      const img = row.getValue('company_image') as string | null
      if (!img) return '-'
      return h('div', { class: 'flex items-center gap-2' }, [
        h('img', {
          src: img,
          alt: 'Company logo',
          class: 'w-8 h-8 rounded object-cover border'
        }),
        h('span', '- logo available')
      ])
    }
  },
  {
    key: 'actions',
    header: 'Aksi',
    cell: ({ row }) => {
      const company = row.original
      return h('div', { class: 'flex gap-2' }, [
        h(Button, {
          size: 'sm',
          variant: 'outline',
          onClick: () => openUpdateModal(company)
        }, () => 'Edit'),
        h(Button, {
          size: 'sm',
          variant: 'destructive-outline',
          onClick: () => onDelete(company.id, company.name)
        }, () => 'Hapus')
      ])
    }
  }
]
</script>

<template>
  <div class="grid gap-6 py-6 px-4 md:px-8">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <NuxtCardTitle class="text-2xl font-bold tracking-tight">Manajemen Perusahaan</NuxtCardTitle>
      <Button @click="openCreateModal" size="sm">
        Tambah Perusahaan
      </Button>
    </div>

    <!-- Content Card -->
    <NuxtCard class="bg-white dark:bg-neutral-800 rounded-lg shadow-sm">
      <NuxtCardContent class="p-0">
        <!-- Search -->
        <div class="p-4 border-b dark:border-neutral-700">
          <InputField
            v-model="search"
            placeholder="Cari nama perusahaan atau singkatan..."
            icon="i-lucide-search"
          />
        </div>

        <!-- Table -->
        <div v-if="pending" class="p-12 flex items-center justify-center">
          <span class="animate-spin mr-2 text-primary">Loading...</span>
        </div>
        
        <div v-else-if="filtered.length === 0" class="p-12 text-center text-muted-foreground">
          {{ search ? 'Tidak ada hasil untuk pencarian Anda' : 'Belum ada data perusahaan' }}
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-neutral-700">
            <thead class="bg-gray-50 dark:bg-neutral-900">
              <tr>
                <th
                  v-for="col in columns"
                  :key="col.accessorKey || col.key"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {{ col.header }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-neutral-800 divide-y divide-gray-200 dark:divide-neutral-700">
              <tr
                v-for="company in paged"
                :key="company.id"
                class="hover:bg-gray-50 dark:hover:bg-neutral-700 transition-colors"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">{{ company.name }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">{{ company.abbreviation }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div v-if="company.company_image" class="flex items-center gap-2">
                    <img :src="company.company_image" class="w-8 h-8 rounded object-cover border" alt="Logo">
                    <span class="text-xs text-muted-foreground">available</span>
                  </div>
                  <div v-else class="text-sm text-muted-foreground">-</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex gap-2">
                    <button
                      @click="openUpdateModal(company)"
                      class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                    >
                      Edit
                    </button>
                    <button
                      @click="onDelete(company.id, company.name)"
                      class="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    >
                      Hapus
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination footer -->
        <div v-if="paged.length > 0" class="p-4 border-t dark:border-neutral-700 flex justify-end">
          <div class="flex items-center gap-2">
            <button
              :disabled="page === 1"
              @click="page--"
              class="px-3 py-1 border rounded disabled:opacity-50 dark:border-neutral-700"
            >
              Previous
            </button>
            <span class="text-sm">{{ page }} / {{ Math.ceil(filtered.length / PAGE_SIZE) }}</span>
            <button
              :disabled="page >= Math.ceil(filtered.length / PAGE_SIZE)"
              @click="page++"
              class="px-3 py-1 border rounded disabled:opacity-50 dark:border-neutral-700"
            >
              Next
            </button>
          </div>
        </div>
      </NuxtCardContent>
    </NuxtCard>

    <!-- Modal Create/Update -->
    <dialog v-if="modalOpen" class="m-0 rounded-xl overflow-hidden w-[90%] max-w-lg backdrop:bg-black/50" role="dialog" aria-modal="true">
      <form
        @submit="onSubmitForm"
        class="flex flex-col bg-white dark:bg-neutral-800 shadow-xl"
      >
        <div class="flex items-center justify-between px-6 py-4 border-b dark:border-neutral-700">
          <h3 class="text-lg font-semibold">
            {{ editingId ? 'Edit Perusahaan' : 'Tambah Perusahaan Baru' }}
          </h3>
          <button
            type="button"
            @click="modalOpen = false"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            ✕
          </button>
        </div>

        <div class="p-6 space-y-4">
          <div>
            <label for="name" class="block text-sm font-medium mb-1">Nama Perusahaan *</label>
            <input
              id="name"
              v-model="formName"
              type="text"
              required
              class="w-full px-3 py-2 border rounded-lg dark:bg-neutral-700 dark:border-neutral-600 focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Contoh: PT. Mitra Andalan Petroleum"
            />
          </div>
          
          <div>
            <label for="abbreviation" class="block text-sm font-medium mb-1">Singkatan *</label>
            <input
              id="abbreviation"
              v-model="formAbbreviation"
              type="text"
              required
              maxlength="20"
              class="w-full px-3 py-2 border rounded-lg dark:bg-neutral-700 dark:border-neutral-600 focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Contoh: MAP"
            />
          </div>
          
          <div>
            <label for="companyImage" class="block text-sm font-medium mb-1">Logo Perusahaan</label>
            <input
              id="companyImage"
              v-model="formCompanyImage"
              type="url"
              class="w-full px-3 py-2 border rounded-lg dark:bg-neutral-700 dark:border-neutral-600 focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="URL gambar logo (base64 atau URL eksternal)"
            />
            <p class="mt-1 text-xs text-muted-foreground">Format: base64 atau URL HTTPS</p>
          </div>
        </div>

        <div class="flex justify-end gap-3 px-6 py-4 border-t dark:border-neutral-700">
          <Button type="button" variant="outline" @click="modalOpen = false">Batal</Button>
          <Button type="submit">{{ editingId ? 'Simpan Perubahan' : 'Tambahkan' }}</Button>
        </div>
      </form>
    </dialog>
  </div>
</template>
