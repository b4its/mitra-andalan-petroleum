<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ 'update:open': [value: boolean] }>()

const { get, put } = useApi()

// ── Fetch ─────────────────────────────────────────────────────
const { data, pending, error, refresh } = await useAsyncData(
  'admin-notifications-list',
  () => get<any[]>('/notifications'),
  { default: () => [] }
)

const notifications = computed<any[]>(() =>
  Array.isArray(data.value) ? data.value : []
)

watch(() => props.open, (isOpen) => {
  if (isOpen) refresh()
})

// ── Search (frontend) ─────────────────────────────────────────
const search = ref('')

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return notifications.value

  return notifications.value.filter((n) => {
    // Gunakan kurung kurawal {} dan let/const di sini
    const is_reading = n.is_read ? 'Dibaca' : 'Belum'

    // Wajib pakai 'return' untuk mengembalikan hasil filternya
    return (
      n.title?.toLowerCase().includes(q)
      || n.message?.toLowerCase().includes(q)
      || n.user_name?.toLowerCase().includes(q)
      || is_reading.toLowerCase().includes(q)
      || n.type?.toLowerCase().includes(q)
    )
  })
})

// ── Pagination ────────────────────────────────────────────────
const page = ref(1)
const PAGE_SIZE = 10
watch(search, () => {
  page.value = 1
})

const paged = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE
  return filtered.value.slice(start, start + PAGE_SIZE)
})

// ── Mark as read ──────────────────────────────────────────────
async function markAsRead(id: string) {
  try {
    await put(`/notifications/${id}`, { is_read: true })
    refresh()
  } catch {
    // silently ignore
  }
}

// ── Detail modal ──────────────────────────────────────────────
const detailOpen = ref(false)
const selectedNotif = ref<any>(null)

function openDetail(notif: any) {
  selectedNotif.value = notif
  // Tutup modal list, buka detail
  emit('update:open', false)
  detailOpen.value = true
  // Tandai dibaca otomatis saat dibuka
  if (!notif.is_read) markAsRead(notif.id)
}

function closeDetail() {
  detailOpen.value = false
  // Buka kembali modal list
  emit('update:open', true)
}

// ── Type badge ────────────────────────────────────────────────
const typeColor: Record<string, 'info' | 'success' | 'warning' | 'error'> = {
  info: 'info',
  success: 'success',
  warning: 'warning',
  error: 'error'
}

function formatDateTime(raw: any): string {
  if (!raw) return '-'
  const d = new Date(raw)
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const yyyy = d.getFullYear()
  const hh = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${dd}-${mm}-${yyyy}, ${hh}:${min}`
}

// ── Kolom tabel ───────────────────────────────────────────────
const columns: TableColumn<any>[] = [
  {
    accessorKey: 'created_at',
    header: 'Waktu',
    cell: ({ row }) => formatDateTime(row.getValue('created_at'))
  },
  {
    accessorKey: 'user_name',
    header: 'Pengguna',
    cell: ({ row }) => row.getValue('user_name') || '-'
  },
  {
    accessorKey: 'is_read',
    header: 'Status',
    cell: ({ row }) => {
      const read = row.getValue('is_read') as boolean
      return h(resolveComponent('UBadge'), {
        variant: 'subtle',
        color: read ? 'success' : 'warning'
      }, () => read ? 'Dibaca' : 'Belum')
    }
  },

  { accessorKey: 'title', header: 'Judul' },
  { accessorKey: 'message', header: 'Pesan' },

  {
    id: 'actions',
    header: '',
    cell: ({ row }) => {
      const notif = row.original
      return h('div', { class: 'flex items-center gap-1' }, [
        h(resolveComponent('UButton'), {
          size: 'xs',
          variant: 'ghost',
          color: 'primary',
          icon: 'i-lucide-eye',
          label: 'Lihat',
          onClick: () => openDetail(notif)
        }),
        !notif.is_read
          ? h(resolveComponent('UButton'), {
              size: 'xs',
              variant: 'soft',
              color: 'neutral',
              label: 'Tandai dibaca',
              onClick: () => markAsRead(notif.id)
            })
          : null
      ])
    }
  }
]
</script>

<template>
  <!-- ── Modal List Notifikasi ── -->
  <UModal
    :open="open"
    title="Notifikasi Sistem"
    :ui="{ content: 'max-w-5xl' }"
    @update:open="emit('update:open', $event)"
  >
    <template #body>
      <UAlert
        v-if="error"
        color="error"
        title="Gagal memuat notifikasi"
        :description="error.message"
      />

      <div v-else-if="pending" class="space-y-3">
        <USkeleton v-for="i in 5" :key="i" class="h-12 w-full" />
      </div>

      <template v-else>
        <!-- Toolbar: search + refresh + counter -->
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <UInput
            v-model="search"
            icon="i-lucide-search"
            placeholder="Cari judul, pesan, pengguna, atau tipe..."
            class="w-72"
          />
          <div class="flex items-center gap-2">
            <span class="text-xs text-muted">
              {{ filtered.length }} notifikasi
            </span>
            <UButton
              size="xs"
              variant="soft"
              icon="i-lucide-refresh-cw"
              @click="() => refresh()"
            />
          </div>
        </div>

        <UTable :data="paged" :columns="columns" />

        <UEmpty
          v-if="!paged.length"
          icon="i-lucide-bell-off"
          title="Tidak ada notifikasi"
          description="Tidak ada notifikasi yang cocok dengan pencarian."
        />

        <div
          v-if="filtered.length > PAGE_SIZE"
          class="flex items-center justify-end border-t border-default pt-3 mt-3"
        >
          <UPagination
            v-model:page="page"
            :total="filtered.length"
            :items-per-page="PAGE_SIZE"
          />
        </div>
      </template>
    </template>
  </UModal>

  <!-- ── Modal Detail Notifikasi ── -->
  <UModal
    :open="detailOpen"
    :ui="{ content: 'max-w-lg' }"
    @update:open="(val) => { if (!val) closeDetail() }"
  >
    <template #title>
      <div class="flex items-center gap-2">
        <UIcon name="i-lucide-bell" class="size-4 text-primary" />
        Detail Notifikasi
      </div>
    </template>

    <template #body>
      <div v-if="selectedNotif" class="space-y-4">
        <!-- Badge tipe + status -->
        <div class="flex items-center gap-2">
          <UBadge
            :color="typeColor[selectedNotif.type] ?? 'neutral'"
            variant="subtle"
            class="capitalize"
          >
            {{ selectedNotif.type }}
          </UBadge>
          <UBadge
            :color="selectedNotif.is_read ? 'success' : 'warning'"
            variant="subtle"
          >
            {{ selectedNotif.is_read ? 'Sudah Dibaca' : 'Belum Dibaca' }}
          </UBadge>
        </div>

        <!-- Detail fields -->
        <div class="space-y-3 text-sm">
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Judul
            </p>
            <p class="font-semibold text-highlighted">
              {{ selectedNotif.title }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">
              Pesan
            </p>
            <p class="text-muted leading-relaxed">
              {{ selectedNotif.message }}
            </p>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-1">
                Pengguna
              </p>
              <p class="font-medium">
                {{ selectedNotif.user_name || '-' }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-1">
                Waktu
              </p>
              <p class="font-medium">
                {{ formatDateTime(selectedNotif.created_at) }}
              </p>
            </div>
            <div v-if="selectedNotif.to">
              <p class="text-xs text-muted uppercase tracking-wide mb-1">
                Tautan
              </p>
              <p class="font-mono text-xs text-primary truncate">
                {{ selectedNotif.to }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-1">
                ID
              </p>
              <p class="font-mono text-xs text-muted truncate">
                {{ selectedNotif.id }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton color="neutral" variant="ghost" @click="closeDetail">
          Kembali ke Notifikasi
        </UButton>
        <UButton
          v-if="selectedNotif?.to"
          color="primary"
          icon="i-lucide-external-link"
          @click="() => { closeDetail(); navigateTo(selectedNotif.to) }"
        >
          Buka Halaman
        </UButton>
      </div>
    </template>
  </UModal>
</template>
