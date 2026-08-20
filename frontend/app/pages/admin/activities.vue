<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'

definePageMeta({ layout: 'admin' })

const toast = useToast()
const { get } = useApi()

// ── Tipe lokal ────────────────────────────────────────────────
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

interface PaginatedActivities {
  items: Activity[]
  total: number
  page: number
  page_size: number
  pages: number
}

// ── Kolom tabel (hanya data ringkas) ──────────────────────────
const columns: TableColumn<Activity>[] = [
  { accessorKey: 'action', header: 'Aksi' },
  { accessorKey: 'resource_type', header: 'Resource' },
  { accessorKey: 'resource_name', header: 'Nama Resource' },
  { accessorKey: 'actor_name', header: 'Actor' },
  { accessorKey: 'created_at', header: 'Waktu' },
  { id: 'actions', header: '' }
]

// ── Data fetch ────────────────────────────────────────────────
const {
  data: activitiesData,
  pending,
  refresh
} = await useAsyncData<PaginatedActivities>(
  'admin-activities',
  () => get<PaginatedActivities>('/activities?page=1&page_size=20'),
  { default: () => ({ items: [], total: 0, page: 1, page_size: 20, pages: 0 }), lazy: true }
)

// ── Filter state ──────────────────────────────────────────────
const actionFilter = ref<string>('all')
const resourceTypeFilter = ref<string>('all')
const actorFilter = ref<string>('')
const search = ref('')
const dateFrom = ref<string>('')
const dateTo = ref<string>('')
const currentPage = ref(1)
const pageSize = ref(20)

// ── Apply filters ─────────────────────────────────────────────
async function applyFilters() {
  try {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      page_size: pageSize.value.toString()
    })

    if (actionFilter.value !== 'all') {
      params.append('action', actionFilter.value)
    }

    if (resourceTypeFilter.value !== 'all') {
      params.append('resource_type', resourceTypeFilter.value)
    }

    if (actorFilter.value) {
      params.append('actor_name', actorFilter.value)
    }

    if (search.value) {
      params.append('search', search.value)
    }

    if (dateFrom.value) {
      params.append('from_date', dateFrom.value)
    }

    if (dateTo.value) {
      params.append('to_date', dateTo.value)
    }

    const res = await get<PaginatedActivities>(`/activities?${params.toString()}`)
    activitiesData.value = res
  } catch (error: any) {
    console.error(error)
    toast.add({
      title: 'Gagal',
      description: error?.response?.data?.detail || 'Terjadi kesalahan saat memuat data',
      color: 'danger'
    })
  }
}

// Reset pagination on filter change
watch([actionFilter, resourceTypeFilter, actorFilter], () => {
  currentPage.value = 1
})

// Fetch ulang saat halaman / ukuran halaman berubah
watch([currentPage, pageSize], ([newPage, newPageSize], [oldPage, oldPageSize]) => {
  if (newPageSize !== oldPageSize) {
    if (newPage !== 1) {
      currentPage.value = 1
      return
    }
    applyFilters()
    return
  }
  if (newPage !== oldPage) {
    applyFilters()
  }
})

// ── Action colors ─────────────────────────────────────────────
const actionColors: Record<string, 'success' | 'info' | 'error'> = {
  create: 'success',
  update: 'info',
  delete: 'error'
}

const actionLabels: Record<string, string> = {
  create: 'Dibuat',
  update: 'Diubah',
  delete: 'Dihapus'
}

// ── Resource types (statis sesuai seluruh entitas sistem) ─────
const resourceTypes = [
  'account',
  'company',
  'customer',
  'delivery_order',
  'invoice',
  'journal_entry',
  'notification',
  'offering_letter',
  'po_transportir',
  'price',
  'purchase_order',
  'sale',
  'supplier',
  'upload',
  'user'
]

// ── Actors (dari data yang sudah dimuat) ──────────────────────
const actorOptions = Array.from(new Set(
  activitiesData.value?.items?.map(a => a.actor_name) || []
)).sort()

// Actors dari filter sekarang disediakan via input teks (Pencarian Actor),
// tidak perlu dropdown statis.
const actors = actorOptions

// ── View activity details modal ──────────────────────────────
const viewModalOpen = ref(false)
const selectedActivity = ref<Activity | null>(null)

function openViewDetail(activity: Activity) {
  selectedActivity.value = activity
  viewModalOpen.value = true
}

// Parse JSON safely & pretty-print
function prettyJSON(jsonString: string | null): string {
  if (!jsonString) return ''
  try {
    return JSON.stringify(JSON.parse(jsonString), null, 2)
  } catch {
    return jsonString
  }
}

function copyJSON(jsonString: string | null) {
  if (!jsonString) return
  navigator.clipboard.writeText(prettyJSON(jsonString))
  toast.add({ title: 'Disalin', description: 'JSON berhasil disalin', color: 'success' })
}

// Format date
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString('id-ID', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Get actions
const actions = ['all', 'create', 'update', 'delete'] as const
</script>

<template>
  <UDashboardPanel id="admin-activities">
    <template #header>
      <UDashboardNavbar
        title="Log Aktivitas Sistem"
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
        <!-- Toolbar: filters -->
        <div class="flex flex-col gap-3">
          <!-- First row: main filters -->
          <div class="flex flex-wrap items-end gap-3">
            <div class="flex flex-col gap-1">
              <label class="text-xs text-muted uppercase tracking-wide">Tipe Aksi</label>
              <USelect
                v-model="actionFilter"
                :items="actions.map(a => ({ label: actionLabels[a] || a, value: a }))"
                placeholder="Semua Aksi"
                class="w-40"
              />
            </div>

            <div class="flex flex-col gap-1">
              <label class="text-xs text-muted uppercase tracking-wide">Resource Type</label>
              <USelect
                v-model="resourceTypeFilter"
                :items="[
                  { label: 'Semua', value: 'all' },
                  ...resourceTypes.map(rt => ({ label: rt, value: rt }))
                ]"
                placeholder="Semua Resource"
                class="w-48"
              />
            </div>

            <div class="flex flex-col gap-1 flex-1 min-w-[200px]">
              <label class="text-xs text-muted uppercase tracking-wide">Pencarian Actor</label>
              <UInput
                v-model="actorFilter"
                placeholder="Cari nama actor..."
                icon="i-lucide-search"
                class="w-full"
              />
            </div>
          </div>

          <!-- Second row: date range & search -->
          <div class="flex flex-wrap items-end gap-3">
            <div class="flex flex-col gap-1">
              <label class="text-xs text-muted uppercase tracking-wide">Dari Tanggal</label>
              <UInput
                v-model="dateFrom"
                type="date"
                class="w-48"
              />
            </div>

            <div class="flex flex-col gap-1">
              <label class="text-xs text-muted uppercase tracking-wide">Sampai Tanggal</label>
              <UInput
                v-model="dateTo"
                type="date"
                class="w-48"
              />
            </div>

            <div class="flex gap-2 ml-auto">
              <UButton
                color="primary"
                @click="applyFilters"
              >
                Terapkan Filter
              </UButton>
              <UButton
                color="neutral"
                variant="ghost"
                @click="() => {
                  actionFilter = 'all'
                  resourceTypeFilter = 'all'
                  actorFilter = ''
                  dateFrom = ''
                  dateTo = ''
                  applyFilters()
                }"
              >
                Reset
              </UButton>
            </div>
          </div>
        </div>

        <!-- Skeleton -->
        <div v-if="pending" class="space-y-3">
          <USkeleton v-for="i in 5" :key="i" class="h-16 rounded-lg" />
        </div>

        <!-- Table -->
        <UCard v-else>
          <UTable :data="activitiesData?.items ?? []" :columns="columns">
            <template #action-cell="{ row }">
              <UBadge
                :color="actionColors[row.original.action] ?? 'neutral'"
                variant="soft"
                class="capitalize"
              >
                {{ actionLabels[row.original.action] || row.original.action }}
              </UBadge>
            </template>

            <template #resource-type-cell="{ row }">
              <span class="font-mono text-sm">{{ row.original.resource_type }}</span>
            </template>

            <template #resource-name-cell="{ row }">
              <span class="text-sm">{{ row.original.resource_name || '-' }}</span>
            </template>

            <template #actor-name-cell="{ row }">
              <div class="flex items-center gap-2">
                <UBadge color="info" variant="soft" class="capitalize">
                  {{ row.original.actor_role }}
                </UBadge>
                <span class="text-sm">{{ row.original.actor_name }}</span>
              </div>
            </template>

            <template #created-at-cell="{ row }">
              <span class="text-sm text-muted whitespace-nowrap">
                {{ formatDate(row.original.created_at) }}
              </span>
            </template>

            <template #actions-cell="{ row }">
              <UButton
                icon="i-lucide-eye"
                size="sm"
                color="primary"
                variant="ghost"
                aria-label="Lihat detail"
                :title="'Lihat detail ' + (row.original.resource_name || row.original.resource_type)"
                @click="openViewDetail(row.original)"
              />
            </template>
          </UTable>

          <UEmpty
            v-if="!activitiesData?.items?.length && !pending"
            icon="i-lucide-history"
            title="Tidak ada aktivitas"
            description="Belum ada aktivitas yang tercatat."
          />

          <!-- Pagination -->
          <div
            v-if="activitiesData?.pages"
            class="flex flex-wrap items-center justify-between gap-3 border-t border-default px-2 pt-3 mt-2"
          >
            <div class="flex items-center gap-3">
              <span class="text-xs text-muted">
                Menampilkan
                <span class="font-medium text-foreground">
                  {{ activitiesData.items.length
                    ? ((activitiesData.page - 1) * (activitiesData.page_size ?? pageSize) + 1)
                    : 0 }}–{{ (activitiesData.page - 1) * (activitiesData.page_size ?? pageSize) + activitiesData.items.length }}
                </span>
                dari
                <span class="font-medium text-foreground">{{ activitiesData.total }}</span>
                aktivitas
              </span>

              <USelect
                v-model="pageSize"
                :items="[10, 20, 50, 100].map(n => ({ label: `${n} / hal`, value: n }))"
                class="w-28"
                aria-label="Jumlah per halaman"
              />
            </div>

            <UPagination
              v-model:page="currentPage"
              :total="activitiesData.total"
              :items-per-page="pageSize"
              :max-delta="2"
              :active-button="{ color: 'primary' }"
            />
          </div>
        </UCard>
      </div>
    </template>
  </UDashboardPanel>

  <!-- Modal View Detail -->
  <UModal v-model:open="viewModalOpen" :ui="{ content: 'max-w-4xl' }">
    <template #title>
      <div class="flex items-center gap-2">
        <UIcon
          v-if="selectedActivity"
          :name="actionColors[selectedActivity.action] === 'success' ? 'i-lucide-circle-check' :
                 actionColors[selectedActivity.action] === 'info' ? 'i-lucide-pencil' : 'i-lucide-trash'"
          :class="`w-6 h-6 ${actionColors[selectedActivity.action] === 'success' ? 'text-success' :
                   actionColors[selectedActivity.action] === 'info' ? 'text-info' : 'text-error'}`"
        />
        <span>Detail Aktivitas</span>
      </div>
    </template>

    <template #body>
      <div v-if="selectedActivity" class="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
        <!-- Basic Info -->
        <div class="grid grid-cols-2 gap-4 p-4 bg-elevated rounded-lg">
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">Aksi</p>
            <p class="font-medium capitalize">{{ actionLabels[selectedActivity.action] || selectedActivity.action }}</p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">Resource</p>
            <p class="font-medium">{{ selectedActivity.resource_type }}</p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">Nama Resource</p>
            <p class="font-medium">{{ selectedActivity.resource_name || '-' }}</p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">Waktu</p>
            <p class="font-medium">{{ formatDate(selectedActivity.created_at) }}</p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">Actor</p>
            <p class="font-medium">{{ selectedActivity.actor_name }}</p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">Role</p>
            <p class="font-medium capitalize">{{ selectedActivity.actor_role }}</p>
          </div>
        </div>

        <!-- Details -->
        <div v-if="selectedActivity.details" class="p-4 bg-elevated rounded-lg">
          <p class="text-xs text-muted uppercase tracking-wide mb-2">Detail</p>
          <p class="text-sm">{{ selectedActivity.details }}</p>
        </div>

        <!-- JSON Data Lama & Baru -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div class="p-4 bg-elevated rounded-lg border border-error/20">
            <div class="flex items-center justify-between mb-2">
              <p class="text-xs text-muted uppercase tracking-wide">JSON Data Lama (Old)</p>
              <UButton
                size="xs"
                variant="ghost"
                icon="i-lucide-copy"
                :disabled="!selectedActivity.old_values"
                @click="copyJSON(selectedActivity.old_values)"
              >
                Copy
              </UButton>
            </div>
            <pre
              v-if="selectedActivity.old_values"
              class="text-xs bg-neutral-900 dark:bg-neutral-950 p-3 rounded overflow-x-auto text-white max-h-72 overflow-y-auto"
            >{{ prettyJSON(selectedActivity.old_values) }}</pre>
            <p v-else class="text-xs text-muted italic">Tidak ada data lama (aksi {{ actionLabels[selectedActivity.action] || selectedActivity.action }})</p>
          </div>

          <div class="p-4 bg-elevated rounded-lg border border-success/20">
            <div class="flex items-center justify-between mb-2">
              <p class="text-xs text-muted uppercase tracking-wide">JSON Data Baru (New)</p>
              <UButton
                size="xs"
                variant="ghost"
                icon="i-lucide-copy"
                :disabled="!selectedActivity.new_values"
                @click="copyJSON(selectedActivity.new_values)"
              >
                Copy
              </UButton>
            </div>
            <pre
              v-if="selectedActivity.new_values"
              class="text-xs bg-neutral-900 dark:bg-neutral-950 p-3 rounded overflow-x-auto text-white max-h-72 overflow-y-auto"
            >{{ prettyJSON(selectedActivity.new_values) }}</pre>
            <p v-else class="text-xs text-muted italic">Tidak ada data baru</p>
          </div>
        </div>

        <!-- Network Info -->
        <div v-if="selectedActivity.ip_address" class="p-4 bg-elevated rounded-lg">
          <p class="text-xs text-muted uppercase tracking-wide mb-2">Informasi Jaringan</p>
          <div class="space-y-1 text-sm">
            <div class="flex justify-between">
              <span class="text-muted">IP Address:</span>
              <span class="font-mono">{{ selectedActivity.ip_address }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted">User Agent:</span>
              <span class="text-sm truncate">{{ selectedActivity.user_agent || '-' }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end">
        <UButton color="neutral" variant="ghost" @click="viewModalOpen = false">
          Tutup
        </UButton>
      </div>
    </template>
  </UModal>
</template>

<style scoped>
pre {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}
</style>