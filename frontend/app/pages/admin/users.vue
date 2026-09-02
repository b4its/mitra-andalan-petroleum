<script setup lang="ts">
import { h } from 'vue'
import * as z from 'zod'
import type { TableColumn, FormSubmitEvent } from '@nuxt/ui'

definePageMeta({ layout: 'admin' })

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const toast = useToast()
const { get, post, put, postFile } = useApi()

interface Activity {
  id: string
  user_id: string | null
  actor_name: string
  actor_role: string
  action: string
  resource_type: string
  resource_id: string | null
  resource_name: string | null
  old_values: string | null
  new_values: string | null
  details: string | null
  ip_address: string | null
  user_agent: string | null
  created_at: string
}

// ── Tipe lokal ────────────────────────────────────────────────
interface User {
  id: string
  name: string
  email: string
  role: string
  signature?: string | null
  signature_caption?: string | null
}

// ── Data fetch ────────────────────────────────────────────────
const {
  data: users,
  pending,
  refresh
} = await useAsyncData<User[]>('admin-users', () => get<User[]>('/profiles'), {
  default: () => [],
  lazy: true
})

// ── Role filter & Search (frontend) ───────────────────────
const roleFilter = ref<string>('all')
const search = ref('')
const page = ref(1)
const PAGE_SIZE = 8

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  const list = users.value ?? []

  // First filter by role
  const result = list.filter(
    u => roleFilter.value === 'all' || u.role === roleFilter.value
  )

  if (!q) return result

  return result.filter(
    u =>
      u.name.toLowerCase().includes(q)
      || u.email.toLowerCase().includes(q)
      || u.role.toLowerCase().includes(q)
  )
})

const paged = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE
  return filtered.value.slice(start, start + PAGE_SIZE)
})

watch(search, () => {
  page.value = 1
})

// ── Peran badge ────────────────────────────────────────────────
const roleColor: Record<
  string,
  'neutral' | 'info' | 'warning' | 'success' | 'error' | 'primary'
> = {
  admin: 'error',
  marketing: 'info',
  operations: 'warning',
  finance: 'success',
  accounting: 'primary'
}

// ── Kolom tabel ───────────────────────────────────────────────
const columns: TableColumn<User>[] = [
  { accessorKey: 'name', header: 'Nama' },
  { accessorKey: 'email', header: 'Email' },
  {
    accessorKey: 'role',
    header: 'Peran',
    cell: ({ row }) => {
      const r = row.getValue('role') as string
      return h(
        UBadge,
        {
          variant: 'subtle',
          color: roleColor[r] ?? 'neutral',
          class: 'capitalize'
        },
        () => r
      )
    }
  },
  { id: 'actions', header: 'Aksi' }
]

// ── Modal states ──────────────────────────────────────────────
type ModalMode = 'view' | 'add' | 'edit'
const modalOpen = ref(false)
const modalMode = ref<ModalMode>('add')
const selectedUser = ref<User | null>(null)

// ── User Activity Monitoring ───────────────────────────────────
const activities = ref<Activity[]>([])
const loadingActivities = ref(false)
const activityPage = ref(1)
const activityPageSize = ref(10)

async function loadUserActivities(userId: string) {
  loadingActivities.value = true
  try {
    const res = await get<{ items: Activity[], total: number, page: number }>(
      `/activities?user_id=${userId}&page=${activityPage.value}&page_size=${activityPageSize.value}`
    )
    activities.value = res.items || []
  } catch (error) {
    console.error('Gagal memuat aktivitas:', error)
    toast.add({
      title: 'Gagal',
      description: 'Tidak dapat memuat data aktivitas pengguna',
      color: 'error'
    })
  } finally {
    loadingActivities.value = false
  }
}

// Watch for pagination changes
watch(activityPage, () => {
  if (selectedUser.value) {
    loadUserActivities(selectedUser.value.id)
  }
})

// ── Form schema ───────────────────────────────────────────────
const ROLES = [
  'admin',
  'marketing',
  'operations',
  'finance',
  'accounting'
] as const

const addSchema = z.object({
  name: z.string().min(2, 'Minimal 2 karakter'),
  email: z.email('Email tidak valid'),
  password: z.string().min(6, 'Minimal 6 karakter'),
  role: z.enum(ROLES),
  signature_caption: z.string().optional(),
  signature: z.instanceof(File).optional()
})
const editSchema = z.object({
  name: z.string().min(2, 'Minimal 2 karakter'),
  email: z.email('Email tidak valid'),
  password: z.string().optional(),
  role: z.enum(ROLES),
  signature_caption: z.string().optional(),
  signature: z.instanceof(File).optional()
})

type AddSchema = z.output<typeof addSchema>
type EditSchema = z.output<typeof editSchema>

const formState = reactive({
  name: '',
  email: '',
  password: '',
  role: 'marketing' as (typeof ROLES)[number],
  signature_caption: '',
  signature: undefined as File | undefined
})

const saving = ref(false)

// ── Helpers ───────────────────────────────────────────────────
function openAdd() {
  modalMode.value = 'add'
  selectedUser.value = null
  formState.name = ''
  formState.email = ''
  formState.password = ''
  formState.role = 'marketing'
  formState.signature_caption = ''
  formState.signature = undefined
  modalOpen.value = true
}

function openView(user: User) {
  modalMode.value = 'view'
  selectedUser.value = user
  activityPage.value = 1
  activities.value = []
  loadUserActivities(user.id).then(() => {
    modalOpen.value = true
  })
}

function openEdit(user: User) {
  modalMode.value = 'edit'
  selectedUser.value = user
  formState.name = user.name
  formState.email = user.email
  formState.password = ''
  formState.role = user.role as (typeof ROLES)[number]
  formState.signature_caption = user.signature_caption || ''
  formState.signature = undefined
  modalOpen.value = true
}

// ── Submit add ────────────────────────────────────────────────
async function onSubmitAdd(event: FormSubmitEvent<AddSchema>) {
  if (saving.value) return
  saving.value = true
  try {
    const body: Record<string, string> = {
      name: event.data.name,
      email: event.data.email,
      password: event.data.password,
      role: event.data.role
    }
    if (event.data.signature_caption) {
      body.signature_caption = event.data.signature_caption
    }
    const created = await post<{ id: string }, typeof body>('/profiles', body)

    // Upload tanda tangan jika ada
    if (event.data.signature && created.id) {
      await postFile('/upload', {
        files: [event.data.signature],
        folder: 'profiles',
        document_type: 'profile',
        document_id: created.id
      })
    }

    toast.add({
      title: 'Berhasil',
      description: 'Pengguna baru berhasil ditambahkan.',
      color: 'success'
    })
    modalOpen.value = false
    refresh()
  } catch (err) {
    toast.add({
      title: 'Gagal',
      description: err instanceof Error ? err.message : 'Gagal menambahkan pengguna.',
      color: 'error'
    })
  } finally {
    saving.value = false
  }
}

// ── Submit edit ───────────────────────────────────────────────
async function onSubmitEdit(event: FormSubmitEvent<EditSchema>) {
  if (saving.value || !selectedUser.value) return
  saving.value = true
  try {
    const body: Record<string, string> = {
      name: event.data.name,
      email: event.data.email,
      role: event.data.role
    }
    if (event.data.password) body.password = event.data.password
    if (event.data.signature_caption) {
      body.signature_caption = event.data.signature_caption
    }
    await put<Record<string, unknown>, typeof body>(`/profiles/${selectedUser.value.id}`, body)

    // Upload tanda tangan baru jika ada
    if (event.data.signature) {
      await postFile('/upload', {
        files: [event.data.signature],
        folder: 'profiles',
        document_type: 'profile',
        document_id: selectedUser.value.id
      })
    }

    toast.add({
      title: 'Berhasil',
      description: 'Data pengguna berhasil diperbarui.',
      color: 'success'
    })
    modalOpen.value = false
    refresh()
  } catch (err) {
    toast.add({
      title: 'Gagal',
      description: err instanceof Error ? err.message : 'Gagal memperbarui pengguna.',
      color: 'error'
    })
  } finally {
    saving.value = false
  }
}

// ── Activity helpers ──────────────────────────────────────────
const actionColor: Record<string, 'success' | 'info' | 'error'> = {
  create: 'success',
  update: 'info',
  delete: 'error'
}

const actionLabel: Record<string, string> = {
  create: 'Dibuat',
  update: 'Diubah',
  delete: 'Dihapus'
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString('id-ID', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// ── Delete ────────────────────────────────────────────────────
const deleteTarget = ref<User | null>(null)
const deleteOpen = ref(false)
const deleting = ref(false)

function openDelete(user: User) {
  deleteTarget.value = user
  deleteOpen.value = true
}

async function confirmDelete() {
  if (deleting.value || !deleteTarget.value) return
  deleting.value = true
  try {
    const { get: _g, post: _p, put: _u } = useApi()
    // Gunakan fetch langsung karena useApi tidak expose delete
    const res = await fetch(`/api/v1/profiles/${deleteTarget.value.id}`, {
      method: 'DELETE'
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || `Error ${res.status}`)
    }
    toast.add({
      title: 'Berhasil',
      description: `Pengguna ${deleteTarget.value.name} berhasil dihapus.`,
      color: 'success'
    })
    deleteOpen.value = false
    deleteTarget.value = null
    refresh()
  } catch (err) {
    toast.add({
      title: 'Gagal',
      description: err instanceof Error ? err.message : 'Gagal menghapus pengguna.',
      color: 'error'
    })
  } finally {
    deleting.value = false
  }
}

// ── Modal title ───────────────────────────────────────────────
const modalTitle = computed(() => {
  if (modalMode.value === 'add') return 'Tambah Pengguna Baru'
  if (modalMode.value === 'edit')
    return `Edit Pengguna — ${selectedUser.value?.name ?? ''}`
  return `Detail Pengguna — ${selectedUser.value?.name ?? ''}`
})

const showPassword = ref(false)
</script>

<template>
  <UDashboardPanel id="admin-users">
    <template #header>
      <UDashboardNavbar title="Manajemen Pengguna" :ui="{ right: 'gap-2' }">
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
            <USelect
              v-model="roleFilter"
              :items="[
                { label: 'Semua Role', value: 'all' },
                ...[
                  { label: 'Admin', value: 'admin' },
                  { label: 'Marketing', value: 'marketing' },
                  { label: 'Operations', value: 'operations' },
                  { label: 'Finance', value: 'finance' },
                  { label: 'Accounting', value: 'accounting' }
                ]
              ]"
              placeholder="Filter Role"
              class="w-full sm:w-48"
            />
            <UInput
              v-model="search"
              icon="i-lucide-search"
              placeholder="Cari nama, email, atau role..."
              class="w-full sm:w-72"
            />
          </div>
          <div class="flex flex-wrap justify-end gap-2">
            <UButton icon="i-lucide-user-plus" color="primary" @click="openAdd">
              Tambah Pengguna
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
                  aria-label="Ubah pengguna"
                  @click="openEdit(row.original)"
                />
                <UButton
                  icon="i-lucide-trash-2"
                  size="xs"
                  color="error"
                  variant="ghost"
                  aria-label="Hapus pengguna"
                  @click="openDelete(row.original)"
                />
              </div>
            </template>
          </UTable>
          <UEmpty
            v-if="!paged.length && !pending"
            icon="i-lucide-users"
            title="Tidak ada pengguna"
            description="Belum ada pengguna yang cocok dengan pencarian."
          />
          <div
            class="flex items-center justify-between border-t border-default px-2 pt-3 mt-2"
          >
            <span class="text-xs text-muted">
              {{ filtered.length }} pengguna{{ search ? " ditemukan" : "" }}
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
      <div v-if="modalMode === 'view' && selectedUser" class="space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Nama
            </p>
            <p class="font-medium">
              {{ selectedUser.name }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Email
            </p>
            <p class="font-medium">
              {{ selectedUser.email }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Peran
            </p>
            <UBadge
              :color="roleColor[selectedUser.role] ?? 'neutral'"
              variant="subtle"
              class="capitalize"
            >
              {{ selectedUser.role }}
            </UBadge>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              ID
            </p>
            <p class="font-mono text-xs text-muted truncate">
              {{ selectedUser.id }}
            </p>
          </div>
          <div v-if="selectedUser.signature" class="col-span-2">
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Tanda Tangan
            </p>
            <img
              :src="selectedUser.signature"
              alt="Tanda tangan"
              class="h-12 w-auto object-contain rounded border"
            >
            <p
              v-if="selectedUser.signature_caption"
              class="mt-1 text-xs text-muted"
            >
              {{ selectedUser.signature_caption }}
            </p>
          </div>

          <!-- Activity Monitoring Section -->
          <div class="col-span-2 mt-4 pt-4 border-t">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-semibold">
                Aktivitas Pengguna
              </h4>
              <UBadge
                :color="actionColor[activities.length > 0 ? 'create' : 'info']"
                variant="soft"
                size="xs"
              >
                {{ activities.length }} aktivitas
              </UBadge>
            </div>

            <div v-if="loadingActivities" class="space-y-2">
              <USkeleton v-for="i in 5" :key="i" class="h-12 rounded" />
            </div>

            <div v-else-if="activities.length === 0" class="text-sm text-muted py-4 text-center">
              <UIcon name="i-lucide-infinity" class="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>Belum ada aktivitas tercatat</p>
            </div>

            <div v-else class="overflow-x-auto rounded-lg border">
              <table class="w-full text-sm">
                <thead class="bg-muted">
                  <tr>
                    <th class="px-4 py-2 text-left font-medium">
                      Aksi
                    </th>
                    <th class="px-4 py-2 text-left font-medium">
                      Resource
                    </th>
                    <th class="px-4 py-2 text-left font-medium">
                      Waktu
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="activity in activities"
                    :key="activity.id"
                    class="border-t hover:bg-muted/50"
                  >
                    <td class="px-4 py-2">
                      <UBadge
                        :color="actionColor[activity.action || 'info']"
                        variant="soft"
                        size="xs"
                        class="capitalize"
                      >
                        {{ actionLabel[activity.action] || activity.action }}
                      </UBadge>
                    </td>
                    <td class="px-4 py-2 font-mono text-xs">
                      {{ activity.resource_type }}
                      <span v-if="activity.resource_name" class="text-muted ml-1">
                        ({{ activity.resource_name }})
                      </span>
                    </td>
                    <td class="px-4 py-2 text-xs text-muted">
                      {{ formatDate(activity.created_at) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Pagination -->
            <div v-if="activities.length > 0" class="mt-3 flex justify-end gap-2">
              <UButton
                size="xs"
                variant="ghost"
                :disabled="activityPage === 1"
                @click="activityPage--"
              >
                ← Sebelumnya
              </UButton>
              <span class="text-xs text-muted self-center">
                Halaman {{ activityPage }}
              </span>
              <UButton
                size="xs"
                variant="ghost"
                @click="activityPage++"
              >
                Berikutnya →
              </UButton>
            </div>
          </div>
        </div>
      </div>

      <!-- ADD mode -->
      <UForm
        v-else-if="modalMode === 'add'"
        id="form-add-user"
        :schema="addSchema"
        :state="formState"
        class="space-y-4"
        @submit="onSubmitAdd"
      >
        <UFormField name="name" label="Nama" required>
          <UInput
            v-model="formState.name"
            placeholder="Nama lengkap"
            autocomplete="off"
          />
        </UFormField>
        <UFormField name="email" label="Email" required>
          <UInput
            v-model="formState.email"
            type="email"
            placeholder="email@contoh.com"
            autocomplete="off"
          />
        </UFormField>
        <UFormField name="password" label="Kata Sandi" required>
          <UInput
            v-model="formState.password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Min. 6 karakter"
            :ui="{ trailing: 'pe-1' }"
          >
            <template #trailing>
              <UButton
                type="button"
                color="neutral"
                variant="link"
                size="sm"
                :icon="showPassword ? 'i-lucide-eye-off' : 'i-lucide-eye'"
                @click="showPassword = !showPassword"
              />
            </template>
          </UInput>
        </UFormField>
        <UFormField name="role" label="Peran" required>
          <USelect
            v-model="formState.role"
            :items="ROLES.map((r) => ({ label: r, value: r }))"
          />
        </UFormField>

        <USeparator />

        <UFormField name="signature" label="Tanda Tangan">
          <UFileUpload
            v-model="formState.signature"
            label="Upload File Tanda Tangan"
            description="Format gambar (.png, .jpg) — otomatis dijadikan barcode di dokumen marketing"
            accept="image/png,image/jpeg,image/jpg"
          />
        </UFormField>

        <UFormField
          name="signature_caption"
          label="Caption Tanda Tangan"
          description="Penanda siapa yang ada di tanda tangan ini"
        >
          <UInput
            v-model="formState.signature_caption"
            placeholder="Contoh: Nico - Marketing"
            autocomplete="off"
          />
        </UFormField>
      </UForm>

      <!-- EDIT mode -->
      <UForm
        v-else-if="modalMode === 'edit'"
        id="form-edit-user"
        :schema="editSchema"
        :state="formState"
        class="space-y-4"
        @submit="onSubmitEdit"
      >
        <UFormField name="name" label="Nama" required>
          <UInput
            v-model="formState.name"
            placeholder="Nama lengkap"
            autocomplete="off"
          />
        </UFormField>
        <UFormField name="email" label="Email" required>
          <UInput
            v-model="formState.email"
            type="email"
            placeholder="email@contoh.com"
            autocomplete="off"
          />
        </UFormField>
        <UFormField name="password" label="Password Baru">
          <UInput
            v-model="formState.password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Kosongkan jika tidak diubah"
            :ui="{ trailing: 'pe-1' }"
          >
            <template #trailing>
              <UButton
                type="button"
                color="neutral"
                variant="link"
                size="sm"
                :icon="showPassword ? 'i-lucide-eye-off' : 'i-lucide-eye'"
                @click="showPassword = !showPassword"
              />
            </template>
          </UInput>
        </UFormField>
        <UFormField name="role" label="Peran" required>
          <USelect
            v-model="formState.role"
            :items="ROLES.map((r) => ({ label: r, value: r }))"
          />
        </UFormField>

        <USeparator />

        <div v-if="selectedUser?.signature && !formState.signature" class="flex items-center gap-2 rounded-lg bg-elevated/50 p-2">
          <img
            :src="selectedUser.signature"
            alt="Tanda tangan saat ini"
            class="h-10 w-auto object-contain"
          >
          <span class="text-xs text-muted">
            Tanda tangan terpasang saat ini
          </span>
        </div>

        <UFormField name="signature" label="Tanda Tangan Baru">
          <UFileUpload
            v-model="formState.signature"
            label="Upload File Tanda Tangan"
            description="Format gambar (.png, .jpg) — upload baru untuk mengganti"
            accept="image/png,image/jpeg,image/jpg"
          />
        </UFormField>

        <UFormField
          name="signature_caption"
          label="Caption Tanda Tangan"
          description="Penanda siapa yang ada di tanda tangan ini"
        >
          <UInput
            v-model="formState.signature_caption"
            placeholder="Contoh: Nico - Marketing"
            autocomplete="off"
          />
        </UFormField>
      </UForm>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          v-if="modalMode === 'edit'"
          color="primary"
          :loading="saving"
          form="form-edit-user"
          type="submit"
        >
          Simpan Perubahan
        </UButton>

        <UButton
          v-else-if="modalMode === 'add'"
          color="primary"
          :loading="saving"
          form="form-add-user"
          type="submit"
        >
          Tambah Pengguna
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
        Hapus Pengguna
      </div>
    </template>
    <template #body>
      <p class="text-sm text-muted">
        Apakah Anda yakin ingin menghapus pengguna
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
