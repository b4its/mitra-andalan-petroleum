<script setup lang="ts">
import { h } from 'vue'
import * as z from 'zod'
import type { TableColumn, FormSubmitEvent } from '@nuxt/ui'
import type { ResUploads } from '~/types'
import type { CompanyData } from '~/types/company'

definePageMeta({ layout: 'admin' })

const toast = useToast()
const { get, post, put, del, postFile } = useApi()

// ── Tipe lokal ────────────────────────────────────────────────
interface CompanyLocal {
  id: string
  name: string
  abbreviation: string
  company_image: string | null
}

// ── Data fetch ────────────────────────────────────────────────
const {
  data: companies,
  pending,
  refresh
} = await useAsyncData<CompanyLocal[]>(
  'admin-companies',
  () => get<CompanyLocal[]>('/companies'),
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

// ── Modal states ──────────────────────────────────────────────
type ModalMode = 'view' | 'add' | 'edit'
const modalOpen = ref(false)
const modalMode = ref<ModalMode>('add')
const selectedCompany = ref<CompanyLocal | null>(null)

function openAdd() {
  modalMode.value = 'add'
  selectedCompany.value = null
  formState.name = ''
  formState.abbreviation = ''
  formState.company_image = ''
  imagePreview.value = null
  filesForUpload.value = null
  modalOpen.value = true
}

function openEdit(company: CompanyLocal) {
  modalMode.value = 'edit'
  selectedCompany.value = company
  formState.name = company.name
  formState.abbreviation = company.abbreviation
  formState.company_image = company.company_image ?? ''
  imagePreview.value = null
  filesForUpload.value = null
  modalOpen.value = true
}

function openView(company: CompanyLocal) {
  modalMode.value = 'view'
  selectedCompany.value = company
  modalOpen.value = true
}

// ── Form schema ────────────────────────────────────────────────
const addSchema = z.object({
  name: z.string().min(2, 'Minimal 2 karakter'),
  abbreviation: z.string().min(1).max(20),
  company_image: z.string().optional()
})

const editSchema = z.object({
  name: z.string().min(2, 'Minimal 2 karakter'),
  abbreviation: z.string().min(1).max(20),
  company_image: z.string().optional()
})

type AddSchema = z.output<typeof addSchema>
type EditSchema = z.output<typeof editSchema>

const formState = reactive<AddSchema & EditSchema>({
  name: '',
  abbreviation: '',
  company_image: null as unknown as string
})

async function onSubmitAdd(event: FormSubmitEvent<AddSchema>) {
  event.preventDefault()
  try {
    await post<{ id: string }, Omit<CompanyData, 'id'>>(
      '/companies',
      {
        name: formState.name,
        abbreviation: formState.abbreviation,
        company_image: formState.company_image || null
      }
    )
    toast.add({
      title: 'Sukses',
      description: 'Perusahaan baru berhasil ditambahkan.',
      color: 'success'
    })
    modalOpen.value = false
    refresh()
  } catch (err) {
    toast.add({
      title: 'Gagal',
      description: err instanceof Error ? err.message : 'Gagal menambahkan perusahaan.',
      color: 'error'
    })
  }
}

async function onSubmitEdit(event: FormSubmitEvent<EditSchema>) {
  event.preventDefault()
  if (!selectedCompany.value) return
  try {
    await put(`/companies/${selectedCompany.value.id}`, {
      name: formState.name,
      abbreviation: formState.abbreviation,
      company_image: formState.company_image || null
    })
    toast.add({
      title: 'Sukses',
      description: 'Data perusahaan berhasil diperbarui.',
      color: 'success'
    })
    modalOpen.value = false
    refresh()
  } catch (err) {
    toast.add({
      title: 'Gagal',
      description: err instanceof Error ? err.message : 'Gagal memperbarui perusahaan.',
      color: 'error'
    })
  }
}

// ── Delete ────────────────────────────────────────────────────
const deleteTarget = ref<CompanyLocal | null>(null)
const deleteOpen = ref(false)
const deleting = ref(false)

function openDelete(user: CompanyLocal) {
  deleteTarget.value = user
  deleteOpen.value = true
}

async function confirmDelete() {
  if (deleting.value || !deleteTarget.value) return
  deleting.value = true
  try {
    await del(`/companies/${deleteTarget.value.id}`)
    toast.add({
      title: 'Berhasil',
      description: `Perusahaan ${deleteTarget.value.name} berhasil dihapus.`,
      color: 'success'
    })
    deleteOpen.value = false
    deleteTarget.value = null
    refresh()
  } catch (err) {
    toast.add({
      title: 'Gagal',
      description: err instanceof Error ? err.message : 'Gagal menghapus perusahaan.',
      color: 'error'
    })
  } finally {
    deleting.value = false
  }
}

// ── Modal title ───────────────────────────────────────────────
const modalTitle = computed(() => {
  if (modalMode.value === 'add') return 'Tambah Perusahaan Baru'
  if (modalMode.value === 'edit')
    return `Edit Perusahaan — ${selectedCompany.value?.name ?? ''}`
  return `Detail Perusahaan — ${selectedCompany.value?.name ?? ''}`
})

// ── Columns ───────────────────────────────────────────────────
const columns: TableColumn<CompanyLocal>[] = [
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
  { id: 'actions', header: 'Aksi' }
]

const saving = ref(false)

// ── Image upload state ────────────────────────────────────────
const imagePreview = ref<string | null>(null)
const filesForUpload = ref<File | null>(null)
const uploadingImage = ref(false)

watch(filesForUpload, (file) => {
  if (file && !uploadingImage.value) {
    onFileSelected(file)
  }
})

async function onFileSelected(file: File) {
  // Validate file size (max 10MB)
  const maxSize = 10 * 1024 * 1024 // 10MB in bytes
  if (file.size > maxSize) {
    toast.add({
      title: 'Gagal',
      description: 'Ukuran file maksimal adalah 10MB',
      color: 'error'
    })
    return
  }

  // Validate file type
  const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
  if (!validTypes.includes(file.type)) {
    toast.add({
      title: 'Gagal',
      description: 'Format file harus JPG, PNG, atau WEBP',
      color: 'error'
    })
    return
  }

  uploadingImage.value = true

  try {
    // Convert to base64 for preview
    const reader = new FileReader()
    reader.onload = () => {
      imagePreview.value = reader.result as string
    }
    reader.readAsDataURL(file)

    // Upload to server
    const res = await postFile<ResUploads[]>('/upload', {
      files: [file],
      folder: 'companies'
    })

    formState.company_image = res[0]?.url ?? ''
    filesForUpload.value = null

    toast.add({
      title: 'Sukses',
      description: 'Gambar berhasil diupload',
      color: 'success'
    })
  } catch (err) {
    console.error(err)
    toast.add({
      title: 'Gagal',
      description: err instanceof Error ? err.message : 'Gagal mengupload gambar',
      color: 'error'
    })
    imagePreview.value = null
  } finally {
    uploadingImage.value = false
  }
}

function clearImage() {
  imagePreview.value = null
  formState.company_image = ''
}
</script>

<template>
  <UDashboardPanel id="admin-companies">
    <template #header>
      <UDashboardNavbar
        title="Manajemen Perusahaan"
        :ui="{ right: 'gap-2' }"
      >
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
        <!-- Toolbar: filter + aksi -->
        <div class="flex flex-col gap-3">
          <div class="flex flex-wrap items-end gap-3">
            <UInput
              v-model="search"
              icon="i-lucide-search"
              placeholder="Cari nama perusahaan atau singkatan..."
              class="w-72"
            />
          </div>
          <div class="flex flex-wrap justify-end gap-2">
            <UButton icon="i-lucide-plus" color="primary" @click="openAdd">
              Tambah Perusahaan
            </UButton>
          </div>
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
                  aria-label="Ubah perusahaan"
                  @click="openEdit(row.original)"
                />
                <UButton
                  icon="i-lucide-trash-2"
                  size="xs"
                  color="error"
                  variant="ghost"
                  aria-label="Hapus perusahaan"
                  @click="openDelete(row.original)"
                />
              </div>
            </template>
          </UTable>
          <UEmpty
            v-if="!paged.length && !pending"
            icon="i-lucide-building-2"
            title="Tidak ada perusahaan"
            description="Belum ada perusahaan yang cocok dengan pencarian."
          />
          <div
            class="flex items-center justify-between border-t border-default px-2 pt-3 mt-2"
          >
            <span class="text-xs text-muted">
              {{ filtered.length }} perusahaan{{
                search ? " ditemukan" : ""
              }}
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
      <div
        v-if="modalMode === 'view' && selectedCompany"
        class="space-y-4"
      >
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Nama
            </p>
            <p class="font-medium">
              {{ selectedCompany.name }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Singkatan
            </p>
            <p class="font-medium">
              {{ selectedCompany.abbreviation }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Logo
            </p>
            <p class="font-medium">
              {{
                selectedCompany.company_image
                  ? "Tersedia"
                  : "Tidak tersedia"
              }}
            </p>
          </div>
        </div>
      </div>

      <!-- ADD mode -->
      <UForm
        v-else-if="modalMode === 'add'"
        id="form-add-company"
        :schema="addSchema"
        :state="formState"
        class="space-y-4"
        @submit="onSubmitAdd"
      >
        <UFormField name="name" label="Nama Perusahaan" required>
          <UInput
            v-model="formState.name"
            placeholder="Contoh: PT. Mitra Andalan Petroleum"
            autocomplete="off"
          />
        </UFormField>
        <UFormField name="abbreviation" label="Singkatan" required>
          <UInput
            v-model="formState.abbreviation"
            maxlength="20"
            placeholder="Contoh: MAP"
            autocomplete="off"
          />
        </UFormField>

        <!-- Logo Upload Section -->
        <UFormField name="company_image" label="Logo Perusahaan">
          <div class="space-y-3">
            <div
              v-if="imagePreview"
              class="relative aspect-square max-w-[200px] mx-auto rounded-lg overflow-hidden border dark:border-neutral-700"
            >
              <img
                :src="imagePreview"
                alt="Preview logo"
                class="w-full h-full object-cover"
              >
              <div class="absolute inset-0 bg-black/50 flex items-center justify-center gap-2 opacity-0 hover:opacity-100 transition-opacity">
                <UButton
                  size="xs"
                  color="error"
                  variant="solid"
                  @click="clearImage"
                >
                  Hapus
                </UButton>
                <UFileUpload
                  v-if="!uploadingImage"
                  v-model="filesForUpload"
                  label="Upload File Baru"
                  description="Maksimal 10MB (JPG, PNG, WEBP)"
                  accept="image/jpeg,image/png,image/jpg,image/webp"
                />
                <span v-else class="text-xs text-white">
                  Mengupload...
                </span>
              </div>
            </div>

            <UFileUpload
              v-else
              v-model="filesForUpload"
              label="Upload Logo Perusahaan"
              description="Maksimal 10MB (JPG, PNG, WEBP)"
              accept="image/jpeg,image/png,image/jpg,image/webp"
            />
          </div>

          <p v-if="formState.company_image" class="mt-2 text-xs text-muted">
            URL gambar telah diupload dari server
          </p>
        </UFormField>
      </UForm>

      <!-- EDIT mode -->
      <UForm
        v-else-if="modalMode === 'edit'"
        id="form-edit-company"
        :schema="editSchema"
        :state="formState"
        class="space-y-4"
        @submit="onSubmitEdit"
      >
        <UFormField name="name" label="Nama Perusahaan" required>
          <UInput
            v-model="formState.name"
            placeholder="Contoh: PT. Mitra Andalan Petroleum"
            autocomplete="off"
          />
        </UFormField>
        <UFormField name="abbreviation" label="Singkatan" required>
          <UInput
            v-model="formState.abbreviation"
            maxlength="20"
            placeholder="Contoh: MAP"
            autocomplete="off"
          />
        </UFormField>

        <!-- Logo Upload Section -->
        <UFormField name="company_image" label="Logo Perusahaan">
          <div class="space-y-3">
            <div
              v-if="imagePreview || selectedCompany?.company_image"
              class="relative aspect-square max-w-[200px] mx-auto rounded-lg overflow-hidden border dark:border-neutral-700"
            >
              <img
                :src="imagePreview || selectedCompany?.company_image || ''"
                alt="Preview logo"
                class="w-full h-full object-cover"
              >
              <div class="absolute inset-0 bg-black/50 flex items-center justify-center gap-2 opacity-0 hover:opacity-100 transition-opacity">
                <UButton
                  size="xs"
                  color="error"
                  variant="solid"
                  @click="clearImage"
                >
                  Hapus
                </UButton>
                <UFileUpload
                  v-if="!uploadingImage && !imagePreview"
                  v-model="filesForUpload"
                  label="Upload File Baru"
                  description="Maksimal 10MB (JPG, PNG, WEBP)"
                  accept="image/jpeg,image/png,image/jpg,image/webp"
                />
                <span v-else-if="uploadingImage" class="text-xs text-white">
                  Mengupload...
                </span>
              </div>
            </div>

            <UFileUpload
              v-else
              v-model="filesForUpload"
              label="Upload Logo Perusahaan"
              description="Maksimal 10MB (JPG, PNG, WEBP)"
              accept="image/jpeg,image/png,image/jpg,image/webp"
            />
          </div>

          <p v-if="formState.company_image" class="mt-2 text-xs text-muted">
            URL gambar telah diupload dari server
          </p>
        </UFormField>
      </UForm>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          v-if="modalMode === 'edit'"
          color="primary"
          :loading="saving"
          form="form-edit-company"
          type="submit"
        >
          Simpan Perubahan
        </UButton>

        <UButton
          v-else-if="modalMode === 'add'"
          color="primary"
          :loading="saving"
          form="form-add-company"
          type="submit"
        >
          Tambahkan
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
        Hapus Perusahaan
      </div>
    </template>
    <template #body>
      <p class="text-sm text-muted">
        Apakah Anda yakin ingin menghapus perusahaan
        <span class="font-semibold text-highlighted">{{
          deleteTarget?.name
        }}</span>? Tindakan ini tidak dapat dibatalkan.
      </p>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton color="error" :loading="deleting" @click="confirmDelete">
          Konfirmasi Hapus
        </UButton>

        <UButton
          color="neutral"
          variant="ghost"
          @click="deleteOpen = false"
        >
          Batal
        </UButton>
      </div>
    </template>
  </UModal>
</template>
