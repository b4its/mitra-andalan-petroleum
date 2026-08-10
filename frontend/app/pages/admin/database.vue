<script setup lang="ts">
definePageMeta({ layout: "admin" });

const toast = useToast();
const exporting = ref(false);
const importing = ref(false);
const clearing = ref(false);
const sqlFile = ref<File | null>(null);
const confirmation = ref("");
const clearConfirmation = ref("");
const confirmOpen = ref(false);
const pendingAction = ref<"export" | "import" | "clear" | null>(null);

const canImport = computed(
  () => Boolean(sqlFile.value) && confirmation.value === "IMPORT SQL",
);
const canClear = computed(
  () => clearConfirmation.value === "BERSIHKAN DATABASE",
);

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  sqlFile.value = input.files?.[0] ?? null;
}

const confirmContent = computed(() => {
  if (pendingAction.value === "export") {
    return {
      title: "Export data SQL?",
      description: "Seluruh data tabel database akan disimpan ke file .sql.",
      confirmLabel: "Ya, Export SQL",
      icon: "i-lucide-download",
      color: "primary" as const,
    };
  }
  if (pendingAction.value === "import") {
    return {
      title: "Import data SQL?",
      description:
        "File SQL yang dipilih akan dijalankan dan dapat mengubah data database.",
      confirmLabel: "Ya, Import SQL",
      icon: "i-lucide-upload",
      color: "error" as const,
    };
  }
  return {
    title: "Bersihkan database?",
    description:
      "Seluruh data tabel aplikasi akan dihapus. Aksi ini tidak bisa dibatalkan tanpa backup SQL.",
    confirmLabel: "Ya, Bersihkan",
    icon: "i-lucide-trash-2",
    color: "error" as const,
  };
});

const confirming = computed(
  () => exporting.value || importing.value || clearing.value,
);

function openConfirm(action: "export" | "import" | "clear") {
  pendingAction.value = action;
  confirmOpen.value = true;
}

async function runConfirmedAction() {
  if (pendingAction.value === "export") {
    await downloadExport();
  } else if (pendingAction.value === "import") {
    await importSql();
  } else if (pendingAction.value === "clear") {
    await clearDatabase();
  }
  confirmOpen.value = false;
  pendingAction.value = null;
}

async function downloadExport() {
  if (exporting.value) return;
  exporting.value = true;
  try {
    const res = await fetch("/api/v1/admin/database/export");
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Gagal export data SQL");
    }

    const blob = await res.blob();
    const disposition = res.headers.get("content-disposition") || "";
    const filename =
      disposition.match(/filename="?([^";]+)"?/)?.[1] || "mandalan-data.sql";
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
    toast.add({
      title: "Berhasil",
      description: "File SQL berhasil diunduh.",
      color: "success",
    });
  } catch (err: any) {
    toast.add({
      title: "Error",
      description: err.message || "Gagal export data SQL.",
      color: "error",
    });
  } finally {
    exporting.value = false;
  }
}

async function importSql() {
  if (importing.value || !sqlFile.value || !canImport.value) return;
  importing.value = true;
  try {
    const formData = new FormData();
    formData.append("file", sqlFile.value);

    const res = await fetch("/api/v1/admin/database/import", {
      method: "POST",
      body: formData,
    });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(body.detail || "Gagal import data SQL");
    }

    toast.add({
      title: "Import selesai",
      description: `${body.statements ?? 0} statement SQL berhasil dijalankan.`,
      color: "success",
    });
    sqlFile.value = null;
    confirmation.value = "";
  } catch (err: any) {
    toast.add({
      title: "Error",
      description: err.message || "Gagal import data SQL.",
      color: "error",
    });
  } finally {
    importing.value = false;
  }
}

async function clearDatabase() {
  if (clearing.value || !canClear.value) return;
  clearing.value = true;
  try {
    const res = await fetch("/api/v1/admin/database/clear", { method: "POST" });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(body.detail || "Gagal membersihkan database");
    }

    toast.add({
      title: "Database dibersihkan",
      description: `${body.tables ?? 0} tabel berhasil dikosongkan.`,
      color: "success",
    });
    clearConfirmation.value = "";
  } catch (err: any) {
    toast.add({
      title: "Error",
      description: err.message || "Gagal membersihkan database.",
      color: "error",
    });
  } finally {
    clearing.value = false;
  }
}
</script>

<template>
  <UDashboardPanel id="admin-database">
    <template #header>
      <UDashboardNavbar title="Konfigurasi Database">
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
          title="Aksi database bersifat permanen"
          description="Simpan export terbaru sebelum import atau membersihkan database. Bersihkan database akan menghapus seluruh data tabel, termasuk user."
        />

        <div class="grid gap-6 lg:grid-cols-2">
          <UCard>
            <template #header>
              <div class="flex items-center gap-3">
                <UIcon name="i-lucide-download" class="size-5 text-success" />
                <div>
                  <h2 class="font-semibold">Export Data SQL</h2>
                  <p class="text-sm text-muted">
                    Download seluruh data sebagai file `.sql`.
                  </p>
                </div>
              </div>
            </template>

            <div class="space-y-4">
              <p class="text-sm text-muted">
                File export berisi statement `DELETE` dan `INSERT` untuk restore
                data tabel aplikasi.
              </p>
              <UButton
                color="success"
                icon="i-lucide-database-backup"
                :loading="exporting"
                @click="openConfirm('export')"
              >
                Export SQL
              </UButton>
            </div>
          </UCard>

          <UCard>
            <template #header>
              <div class="flex items-center gap-3">
                <UIcon name="i-lucide-upload" class="size-5 text-warning" />
                <div>
                  <h2 class="font-semibold">Import Data SQL</h2>
                  <p class="text-sm text-muted">
                    Upload file `.sql` untuk restore data.
                  </p>
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
                />
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
                color="warning"
                :disabled="!canImport"
                :loading="importing"
                @click="openConfirm('import')"
              >
                Import SQL
              </UButton>
            </div>
          </UCard>
        </div>

        <UCard>
          <template #header>
            <div class="flex items-center gap-3">
              <UIcon name="i-lucide-trash-2" class="size-5 text-error" />
              <div>
                <h2 class="font-semibold">Bersihkan Database</h2>
                <p class="text-sm text-muted">
                  Kosongkan seluruh tabel database aplikasi.
                </p>
              </div>
            </div>
          </template>

          <div class="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-end">
            <div class="space-y-4">
              <UAlert
                icon="i-lucide-triangle-alert"
                color="error"
                variant="subtle"
                title="Aksi ini bersifat destruktif, gunakan dengan bijak!"
                description="Aksi ini akan menghapus seluruh data yang ada dalam sistem aplikasi. Lakukan
                backup dengan export SQL terlebih dahulu jika data masih dibutuhkan."
              />

              <UFormField label="Konfirmasi" required>
                <UInput
                  v-model="clearConfirmation"
                  placeholder="Ketik BERSIHKAN DATABASE"
                  class="w-full"
                />
              </UFormField>
            </div>

            <UButton
              icon="i-lucide-database-x"
              color="error"
              :disabled="!canClear"
              :loading="clearing"
              @click="openConfirm('clear')"
            >
              Bersihkan Database
            </UButton>
          </div>
        </UCard>
      </div>
    </template>
  </UDashboardPanel>

  <UModal v-model:open="confirmOpen" :ui="{ content: 'max-w-md' }">
    <template #title>
      <div class="flex items-center gap-2">
        <UIcon
          :name="confirmContent.icon"
          :class="
            confirmContent.color === 'error' ? 'text-error' : 'text-primary'
          "
        />
        <span>{{ confirmContent.title }}</span>
      </div>
    </template>

    <template #body>
      <p class="text-sm text-muted">
        {{ confirmContent.description }}
      </p>
    </template>

    <template #footer>
      <div class="flex w-full justify-end gap-2">
        <UButton
          :color="confirmContent.color"
          :icon="confirmContent.icon"
          :loading="confirming"
          @click="runConfirmedAction"
        >
          {{ confirmContent.confirmLabel }}
        </UButton>

        <UButton
          color="neutral"
          variant="ghost"
          :disabled="confirming"
          @click="confirmOpen = false"
        >
          Batal
        </UButton>
      </div>
    </template>
  </UModal>
</template>
