<script setup lang="ts">
import { h } from "vue";
import * as z from "zod";
import type { TableColumn, FormSubmitEvent } from "@nuxt/ui";

definePageMeta({ layout: "admin" });

const UBadge = resolveComponent("UBadge");
const UButton = resolveComponent("UButton");
const toast = useToast();
const { get, post, put } = useApi();

// ── Tipe lokal ────────────────────────────────────────────────
interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

// ── Data fetch ────────────────────────────────────────────────
const {
  data: users,
  pending,
  refresh,
} = await useAsyncData<User[]>("admin-users", () => get<User[]>("/profiles"), {
  default: () => [],
  lazy: true,
});

// ── Search (frontend) ─────────────────────────────────────────
const search = ref("");
const page = ref(1);
const PAGE_SIZE = 8;

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase();
  const list = users.value ?? [];
  if (!q) return list;
  return list.filter(
    (u) =>
      u.name.toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q) ||
      u.role.toLowerCase().includes(q),
  );
});

const paged = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE;
  return filtered.value.slice(start, start + PAGE_SIZE);
});

watch(search, () => {
  page.value = 1;
});

// ── Role badge ────────────────────────────────────────────────
const roleColor: Record<
  string,
  "neutral" | "info" | "warning" | "success" | "error" | "primary"
> = {
  admin: "error",
  marketing: "info",
  operations: "warning",
  finance: "success",
  accounting: "primary",
};

// ── Kolom tabel ───────────────────────────────────────────────
const columns: TableColumn<User>[] = [
  { accessorKey: "name", header: "Nama" },
  { accessorKey: "email", header: "Email" },
  {
    accessorKey: "role",
    header: "Role",
    cell: ({ row }) => {
      const r = row.getValue("role") as string;
      return h(
        UBadge,
        {
          variant: "subtle",
          color: roleColor[r] ?? "neutral",
          class: "capitalize",
        },
        () => r,
      );
    },
  },
  { id: "actions", header: "Aksi" },
];

// ── Modal states ──────────────────────────────────────────────
type ModalMode = "view" | "add" | "edit";
const modalOpen = ref(false);
const modalMode = ref<ModalMode>("add");
const selectedUser = ref<User | null>(null);

// ── Form schema ───────────────────────────────────────────────
const ROLES = [
  "admin",
  "marketing",
  "operations",
  "finance",
  "accounting",
] as const;

const addSchema = z.object({
  name: z.string().min(2, "Minimal 2 karakter"),
  email: z.email("Email tidak valid"),
  password: z.string().min(6, "Minimal 6 karakter"),
  role: z.enum(ROLES),
});
const editSchema = z.object({
  name: z.string().min(2, "Minimal 2 karakter"),
  email: z.email("Email tidak valid"),
  password: z.string().optional(),
  role: z.enum(ROLES),
});

type AddSchema = z.output<typeof addSchema>;
type EditSchema = z.output<typeof editSchema>;

const formState = reactive({
  name: "",
  email: "",
  password: "",
  role: "marketing" as (typeof ROLES)[number],
});

const saving = ref(false);

// ── Helpers ───────────────────────────────────────────────────
function openAdd() {
  modalMode.value = "add";
  selectedUser.value = null;
  formState.name = "";
  formState.email = "";
  formState.password = "";
  formState.role = "marketing";
  modalOpen.value = true;
}

function openView(user: User) {
  modalMode.value = "view";
  selectedUser.value = user;
  modalOpen.value = true;
}

function openEdit(user: User) {
  modalMode.value = "edit";
  selectedUser.value = user;
  formState.name = user.name;
  formState.email = user.email;
  formState.password = "";
  formState.role = user.role as (typeof ROLES)[number];
  modalOpen.value = true;
}

// ── Submit add ────────────────────────────────────────────────
async function onSubmitAdd(event: FormSubmitEvent<AddSchema>) {
  if (saving.value) return;
  saving.value = true;
  try {
    await post<User, AddSchema>("/profiles", event.data);
    toast.add({
      title: "Berhasil",
      description: "Pengguna baru berhasil ditambahkan.",
      color: "success",
    });
    modalOpen.value = false;
    refresh();
  } catch (err: any) {
    toast.add({
      title: "Error",
      description: err.message || "Gagal menambahkan pengguna.",
      color: "error",
    });
  } finally {
    saving.value = false;
  }
}

// ── Submit edit ───────────────────────────────────────────────
async function onSubmitEdit(event: FormSubmitEvent<EditSchema>) {
  if (saving.value || !selectedUser.value) return;
  saving.value = true;
  try {
    const body: Record<string, string> = {
      name: event.data.name,
      email: event.data.email,
      role: event.data.role,
    };
    if (event.data.password) body.password = event.data.password;
    await put<User, typeof body>(`/profiles/${selectedUser.value.id}`, body);
    toast.add({
      title: "Berhasil",
      description: "Data pengguna berhasil diperbarui.",
      color: "success",
    });
    modalOpen.value = false;
    refresh();
  } catch (err: any) {
    toast.add({
      title: "Error",
      description: err.message || "Gagal memperbarui pengguna.",
      color: "error",
    });
  } finally {
    saving.value = false;
  }
}

// ── Delete ────────────────────────────────────────────────────
const deleteTarget = ref<User | null>(null);
const deleteOpen = ref(false);
const deleting = ref(false);

function openDelete(user: User) {
  deleteTarget.value = user;
  deleteOpen.value = true;
}

async function confirmDelete() {
  if (deleting.value || !deleteTarget.value) return;
  deleting.value = true;
  try {
    const { get: _g, post: _p, put: _u, ...rest } = useApi();
    // Gunakan fetch langsung karena useApi tidak expose delete
    const res = await fetch(`/api/v1/profiles/${deleteTarget.value.id}`, {
      method: "DELETE",
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Error ${res.status}`);
    }
    toast.add({
      title: "Berhasil",
      description: `Pengguna ${deleteTarget.value.name} berhasil dihapus.`,
      color: "success",
    });
    deleteOpen.value = false;
    deleteTarget.value = null;
    refresh();
  } catch (err: any) {
    toast.add({
      title: "Error",
      description: err.message || "Gagal menghapus pengguna.",
      color: "error",
    });
  } finally {
    deleting.value = false;
  }
}

// ── Modal title ───────────────────────────────────────────────
const modalTitle = computed(() => {
  if (modalMode.value === "add") return "Tambah Pengguna Baru";
  if (modalMode.value === "edit")
    return `Edit Pengguna — ${selectedUser.value?.name ?? ""}`;
  return `Detail Pengguna — ${selectedUser.value?.name ?? ""}`;
});

const showPassword = ref(false);
</script>

<template>
  <UDashboardPanel id="admin-users">
    <template #header>
      <UDashboardNavbar title="Manajemen Pengguna" :ui="{ right: 'gap-2' }">
        <template #leading><UDashboardSidebarCollapse /></template>
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
            placeholder="Cari nama, email, atau role..."
            class="w-72"
          />
          <UButton icon="i-lucide-user-plus" color="primary" @click="openAdd">
            Tambah Pengguna
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
                  aria-label="Edit pengguna"
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
    <template #title>{{ modalTitle }}</template>

    <template #body>
      <!-- VIEW mode -->
      <div v-if="modalMode === 'view' && selectedUser" class="space-y-4">
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">Nama</p>
            <p class="font-medium">{{ selectedUser.name }}</p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">Email</p>
            <p class="font-medium">{{ selectedUser.email }}</p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">Role</p>
            <UBadge
              :color="roleColor[selectedUser.role] ?? 'neutral'"
              variant="subtle"
              class="capitalize"
            >
              {{ selectedUser.role }}
            </UBadge>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide mb-1">ID</p>
            <p class="font-mono text-xs text-muted truncate">
              {{ selectedUser.id }}
            </p>
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
        <UFormField name="password" label="Password" required>
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
        <UFormField name="role" label="Role" required>
          <USelect
            v-model="formState.role"
            :items="ROLES.map((r) => ({ label: r, value: r }))"
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
        <UFormField name="role" label="Role" required>
          <USelect
            v-model="formState.role"
            :items="ROLES.map((r) => ({ label: r, value: r }))"
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
        }}</span
        >? Tindakan ini tidak dapat dibatalkan.
      </p>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton color="error" :loading="deleting" @click="confirmDelete">
          Konfirmasi Hapus
        </UButton>

        <UButton color="neutral" variant="ghost" @click="deleteOpen = false"
          >Batal</UButton
        >
      </div>
    </template>
  </UModal>
</template>
