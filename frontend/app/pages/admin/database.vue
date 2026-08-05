<script setup lang="ts">
definePageMeta({ layout: 'admin' })

const toast = useToast()
const exporting = ref(false)
const importing = ref(false)
const sqlFile = ref<File | null>(null)
const confirmation = ref('')

const canImport = computed(() => Boolean(sqlFile.value) && confirmation.value === 'IMPORT SQL')

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  sqlFile.value = input.files?.[0] ?? null
}

async function downloadExport() {
  if (exporting.value) return
  exporting.value = true
  try {
    const res = await fetch('/api/v1/admin/database/export')
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || 'Gagal export data SQL')
    }

    const blob = await res.blob()
    const disposition = res.headers.get('content-disposition') || ''
    const filename = disposition.match(/filename="?([^";]+)"?/)?.[1] || 'mandalan-data.sql'
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    URL.revokeObjectURL(url)
    toast.add({ title: 'Berhasil', description: 'File SQL berhasil diunduh.', color: 'success' })
  } catch (err: any) {
    toast.add({ title: 'Error', description: err.message || 'Gagal export data SQL.', color: 'error' })
  } finally {
    exporting.value = false
  }
}

async function importSql() {
  if (importing.value || !sqlFile.value || !canImport.value) return
  importing.value = true
  try {
    const formData = new FormData()
    formData.append('file', sqlFile.value)

    const res = await fetch('/api/v1/admin/database/import', {
      method: 'POST',
      body: formData
    })
    const body = await res.json().catch(() => ({}))
    if (!res.ok) {
      throw new Error(body.detail || 'Gagal import data SQL')
    }

    toast.add({ title: 'Import selesai', description: `${body.statements ?? 0} statement SQL berhasil dijalankan.`, color: 'success' })
    sqlFile.value = null
    confirmation.value = ''
  } catch (err: any) {
    toast.add({ title: 'Error', description: err.message || 'Gagal import data SQL.', color: 'error' })
  } finally {
    importing.value = false
  }
}
</script>

<template>
  <UDashboardPanel id="admin-database">
    <template #header>
      <UDashboardNavbar title="Export / Import SQL">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="space-y-6 p-4 lg:p-6">
        <UAlert
          icon="i-lucide-triangle-alert"
          color="warning"
          variant="subtle"
          title="Import SQL akan mengubah data database"
          description="Gunakan fitur ini hanya untuk backup/restore data internal. Simpan export terbaru sebelum melakukan import."
        />

        <div class="grid gap-6 lg:grid-cols-2">
          <UCard>
            <template #header>
              <div class="flex items-center gap-3">
                <UIcon name="i-lucide-download" class="size-5 text-primary" />
                <div>
                  <h2 class="font-semibold">Export Data SQL</h2>
                  <p class="text-sm text-muted">Download seluruh data sebagai file `.sql`.</p>
                </div>
              </div>
            </template>

            <div class="space-y-4">
              <p class="text-sm text-muted">
                File export berisi statement `DELETE` dan `INSERT` untuk restore data tabel aplikasi.
              </p>
              <UButton
                icon="i-lucide-database-backup"
                :loading="exporting"
                @click="downloadExport"
              >
                Export SQL
              </UButton>
            </div>
          </UCard>

          <UCard>
            <template #header>
              <div class="flex items-center gap-3">
                <UIcon name="i-lucide-upload" class="size-5 text-error" />
                <div>
                  <h2 class="font-semibold">Import Data SQL</h2>
                  <p class="text-sm text-muted">Upload file `.sql` untuk restore data.</p>
                </div>
              </div>
            </template>

            <div class="space-y-4">
              <UFormField label="File SQL" required>
                <input
                  type="file"
                  accept=".sql,application/sql,text/sql,text/plain"
                  class="block w-full rounded-md border border-default bg-default px-3 py-2 text-sm"
                  @change="onFileChange"
                >
              </UFormField>

              <UFormField label="Konfirmasi" required>
                <UInput
                  v-model="confirmation"
                  placeholder="Ketik IMPORT SQL"
                  class="w-full"
                />
              </UFormField>

              <UButton
                icon="i-lucide-database-zap"
                color="error"
                :disabled="!canImport"
                :loading="importing"
                @click="importSql"
              >
                Import SQL
              </UButton>
            </div>
          </UCard>
        </div>
      </div>
    </template>
  </UDashboardPanel>
</template>
