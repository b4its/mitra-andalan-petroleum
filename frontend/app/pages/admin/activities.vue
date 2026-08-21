<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import type { RangeDate } from '~/types'

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

// ── Kolom tabel (ringkas: No, Nama, Peran, Resource Type) ─────
const columns: TableColumn<Activity>[] = [
  { id: 'no', header: 'No.' },
  { accessorKey: 'actor_name', header: 'Nama' },
  { accessorKey: 'actor_role', header: 'Peran' },
  { accessorKey: 'resource_type', header: 'Resource Type' },
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
  {
    default: () => ({ items: [], total: 0, page: 1, page_size: 20, pages: 0 }),
    lazy: true
  }
)

// ── Filter state ──────────────────────────────────────────────
const actionFilter = ref<'all' | 'create' | 'update' | 'delete'>('all')
const resourceTypeFilter = ref<string>('all')
const actorFilter = ref<string>('')
const search = ref('')
const range = ref<RangeDate>({
  start: new Date(Date.now() - 30 * 86400000),
  end: new Date()
})
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

    if (range.value.start) {
      params.append(
        'from_date',
        range.value.start.toISOString().split('T')[0] || ''
      )
    }

    if (range.value.end) {
      params.append(
        'to_date',
        range.value.end.toISOString().split('T')[0] || ''
      )
    }

    const res = await get<PaginatedActivities>(
      `/activities?${params.toString()}`
    )
    activitiesData.value = res
  } catch (error: unknown) {
    console.error(error)
    const detail = (error as { response?: { data?: { detail?: string } } })
      ?.response?.data?.detail
    toast.add({
      title: 'Gagal',
      description: detail || 'Terjadi kesalahan saat memuat data',
      color: 'error'
    })
  }
}

// Reset pagination on filter change
watch([actionFilter, resourceTypeFilter, actorFilter], () => {
  currentPage.value = 1
})

// ── Action colors ─────────────────────────────────────────────
const actionColors: Record<string, 'info' | 'success' | 'warning' | 'error'> = {
  create: 'success',
  update: 'info',
  delete: 'error'
}

const actionLabels: Record<string, string> = {
  all: 'Semua',
  create: 'Dibuat',
  update: 'Diubah',
  delete: 'Dihapus'
}

// ── Resource types ────────────────────────────────────────────
const resourceTypes = ref<string[]>([])

async function loadResourceTypes() {
  try {
    const types = await get<string[]>('/activities/resource-types')
    if (Array.isArray(types)) {
      resourceTypes.value = [...types].sort()
    }
  } catch (error: unknown) {
    console.error('Gagal memuat resource types', error)
  }
}

await loadResourceTypes()

// ── View activity details modal ──────────────────────────────
const viewModalOpen = ref(false)
const selectedActivity = ref<Activity | null>(null)

function openViewDetail(activity: Activity) {
  selectedActivity.value = activity
  viewModalOpen.value = true
}

// Parse JSON safely
// function parseJSON(jsonString: string | null): any {
//   if (!jsonString) return null;
//   try {
//     return JSON.parse(jsonString);
//   } catch {
//     return jsonString;
//   }
// }

// function copyJSON(jsonString: string | null) {
//   if (!jsonString) return
//   navigator.clipboard.writeText(prettyJSON(jsonString))
//   toast.add({ title: 'Disalin', description: 'JSON berhasil disalin', color: 'success' })
// }

// Format date
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString('id-ID', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Copy teks to clipboard
async function copyText(text: string | null | undefined) {
  if (!text) return
  try {
    await navigator.clipboard.writeText(text)
    toast.add({
      title: 'Disalin',
      description: 'Teks berhasil disalin',
      color: 'success'
    })
  } catch {
    toast.add({
      title: 'Gagal',
      description: 'Gagal menyalin teks',
      color: 'error'
    })
  }
}

// Get actions
const actions = ['all', 'create', 'update', 'delete'] as const
</script>

<template>
  <UDashboardPanel id="admin-activities">
    <template #header>
      <UDashboardNavbar title="Log Aktivitas Sistem" :ui="{ right: 'gap-2' }">
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
                :items="
                  actions.map((a) => ({
                    label: actionLabels[a] || a,
                    value: a
                  }))
                "
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
                  ...resourceTypes.map((rt) => ({ label: rt, value: rt }))
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
              <HomeDateRangePicker v-model="range" />
            </div>

            <div class="flex gap-2 ml-auto">
              <UButton color="primary" @click="applyFilters">
                Terapkan Filter
              </UButton>

              <UButton
                color="neutral"
                variant="ghost"
                @click="
                  () => {
                    actionFilter = 'all';
                    resourceTypeFilter = 'all';
                    actorFilter = '';
                    range = {
                      start: new Date(Date.now() - 30 * 86400000),
                      end: new Date()
                    };
                    applyFilters();
                  }
                "
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
            <template #no-cell="{ row }">
              <span class="text-muted">
                {{
                  (activitiesData?.page - 1)
                    * (activitiesData?.page_size ?? pageSize)
                    + row.index
                    + 1
                }}
              </span>
            </template>

            <template #actor-name-cell="{ row }">
              <span class="font-medium">{{ row.original.actor_name }}</span>
            </template>

            <template #actor-role-cell="{ row }">
              <UBadge
                :color="row.original.actor_role === 'admin' ? 'error' : 'info'"
                variant="soft"
                class="capitalize"
              >
                {{ row.original.actor_role }}
              </UBadge>
            </template>

            <template #resource-type-cell="{ row }">
              <span class="font-mono text-sm">{{
                row.original.resource_type
              }}</span>
            </template>

            <template #actions-cell="{ row }">
              <UButton
                icon="i-lucide-eye"
                size="xs"
                color="primary"
                variant="ghost"
                aria-label="Lihat detail"
                @click="openViewDetail(row.original)"
              >
                Detail
              </UButton>
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
          :name="
            actionColors[selectedActivity.action] === 'success'
              ? 'i-lucide-circle-check'
              : actionColors[selectedActivity.action] === 'info'
                ? 'i-lucide-pencil'
                : 'i-lucide-trash'
          "
          :class="`w-6 h-6 ${
            actionColors[selectedActivity.action] === 'success'
              ? 'text-success'
              : actionColors[selectedActivity.action] === 'info'
                ? 'text-info'
                : 'text-error'
          }`"
        />
        <span>Detail Aktivitas</span>
      </div>
    </template>

    <template #body>
      <div
        v-if="selectedActivity"
        class="space-y-4 max-h-[70vh] overflow-y-auto pr-2"
      >
        <!-- Basic Info -->
        <div class="grid grid-cols-2 gap-4 p-4 bg-elevated rounded-lg">
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Aksi
            </p>
            <p class="font-medium capitalize">
              {{
                actionLabels[selectedActivity.action] || selectedActivity.action
              }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Resource
            </p>
            <p class="font-medium">
              {{ selectedActivity.resource_type }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Nama Resource
            </p>
            <p class="font-medium">
              {{ selectedActivity.resource_name || "-" }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Waktu
            </p>
            <p class="font-medium">
              {{ formatDate(selectedActivity.created_at) }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Actor
            </p>
            <p class="font-medium">
              {{ selectedActivity.actor_name }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Role
            </p>
            <p class="font-medium capitalize">
              {{ selectedActivity.actor_role }}
            </p>
          </div>
        </div>

        <!-- Details -->
        <div v-if="selectedActivity.details" class="p-4 bg-elevated rounded-lg">
          <p class="text-xs text-muted uppercase tracking-wide mb-2">
            Detail
          </p>
          <p class="text-sm">
            {{ selectedActivity.details }}
          </p>
        </div>

        <!-- Old Values -->
        <div
          v-if="selectedActivity.old_values"
          class="p-4 bg-elevated rounded-lg"
        >
          <div class="flex items-center justify-between mb-2">
            <p class="text-xs text-muted uppercase tracking-wide">
              Nilai Sebelum (Old)
            </p>
            <UButton
              size="xs"
              variant="ghost"
              icon="i-lucide-copy"
              @click="copyText(selectedActivity.old_values)"
            >
              Copy
            </UButton>
          </div>
          <pre
            class="text-xs bg-neutral-900 dark:bg-neutral-950 p-3 rounded overflow-x-auto text-white"
          >{{ selectedActivity.old_values }}</pre>
        </div>

        <!-- New Values -->
        <div
          v-if="selectedActivity.new_values"
          class="p-4 bg-elevated rounded-lg"
        >
          <div class="flex items-center justify-between mb-2">
            <p class="text-xs text-muted uppercase tracking-wide">
              Nilai Setelah (New)
            </p>
            <UButton
              size="xs"
              variant="ghost"
              icon="i-lucide-copy"
              @click="copyText(selectedActivity.new_values)"
            >
              Copy
            </UButton>
          </div>
          <pre
            class="text-xs bg-neutral-900 dark:bg-neutral-950 p-3 rounded overflow-x-auto text-white"
          >{{ selectedActivity.new_values }}</pre>
        </div>

        <!-- Network Info -->
        <div
          v-if="selectedActivity.ip_address"
          class="p-4 bg-elevated rounded-lg"
        >
          <p class="text-xs text-muted uppercase tracking-wide mb-2">
            Informasi Jaringan
          </p>
          <div class="space-y-1 text-sm">
            <div class="flex justify-between">
              <span class="text-muted">IP Address:</span>
              <span class="font-mono">{{ selectedActivity.ip_address }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted">User Agent:</span>
              <span class="text-sm truncate">{{
                selectedActivity.user_agent || "-"
              }}</span>
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
