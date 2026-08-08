<script setup lang="ts">
import { getPaginationRowModel } from "@tanstack/vue-table";
import { h } from "vue";
import type { TableColumn } from "@nuxt/ui";

definePageMeta({ layout: "admin" });

const UBadge = resolveComponent("UBadge");
const UButton = resolveComponent("UButton");
const table = useTemplateRef("table");
const columnPinning = ref({ right: ["actions"] });
const toast = useToast();
const { get, put, post, del } = useApi();

const search = ref("");
const debouncedSearch = refDebounced(search, 300);

interface DeliveryOrderRow {
  id: string;
  do_number: string;
  customer_id: string;
  customer_name: string;
  po_number: string | null;
  transport_name: string | null;
  fuel_total: number;
  status: string;
  status_rilis_dana: boolean;
  rilis_dana_at: string | null;
  status_ready_order: boolean;
  ready_order_at: string | null;
  status_selesai_dikirim: boolean;
  selesai_dikirim_at: string | null;
  status_lunas_ongkir: boolean;
  lunas_ongkir_at: string | null;
}

interface CustomerOption {
  id: string;
  name: string;
}

const { data: dos, refresh } = await useAsyncData(
  "admin-delivery-orders",
  async () => {
    const params: Record<string, string | number> = { page: 1, page_size: 100 };
    if (debouncedSearch.value) params.search = debouncedSearch.value;
    const res = await get<{ items: DeliveryOrderRow[] }>(
      "/delivery-orders",
      params,
    );
    return res.items || [];
  },
  { default: () => [], watch: [debouncedSearch], server: false },
);

const { data: customers } = await useAsyncData(
  "admin-customers-options",
  () => get<CustomerOption[]>("/customers"),
  { default: () => [], server: false },
);
const customerItems = computed(() =>
  customers.value.map((c: CustomerOption) => ({ label: c.name, value: c.id })),
);

const statusLabel: Record<string, string> = {
  created: "Dibuat",
  document_returned: "Dokumen Kembali",
};
const statusColor: Record<string, string> = {
  created: "info",
  document_returned: "success",
};

function statusBadge(
  done: boolean,
  label: string,
  at: string | null | undefined,
) {
  return h("div", { class: "flex flex-col gap-0.5" }, [
    h(
      UBadge,
      {
        variant: "subtle",
        color: done ? "success" : "neutral",
        class: "text-xs",
      },
      () => (done ? label : "-"),
    ),
    done && at
      ? h("span", { class: "text-[10px] text-muted" }, formatDate(at))
      : null,
  ]);
}

// ── Modal detail ─────────────────────────────────────────────
const detailOpen = ref(false);
const detailId = ref<string | null>(null);
function openDetail(id: string) {
  detailId.value = id;
  detailOpen.value = true;
}

// ── Modal edit ───────────────────────────────────────────────
const editOpen = ref(false);
const editTarget = ref<DeliveryOrderRow | null>(null);
const editLoading = ref(false);
const form = reactive({
  do_number: "",
  customer_id: "",
  po_number: "",
  transport_name: "",
  fuel_total: 0,
  status: "created",
});

function openEdit(row: DeliveryOrderRow) {
  editTarget.value = row;
  form.do_number = row.do_number;
  form.customer_id = row.customer_id;
  form.po_number = row.po_number ?? "";
  form.transport_name = row.transport_name ?? "";
  form.fuel_total = row.fuel_total ?? 0;
  form.status = row.status ?? "created";
  editOpen.value = true;
}

async function submitEdit() {
  if (editLoading.value || !editTarget.value) return;
  editLoading.value = true;
  try {
    await put(`/delivery-orders/${editTarget.value.id}`, {
      do_number: form.do_number.trim(),
      customer_id: form.customer_id,
      po_number: form.po_number.trim() || null,
      transport_name: form.transport_name.trim() || null,
      fuel_total: Number(form.fuel_total) || 0,
      status: form.status,
    });
    toast.add({
      title: "Berhasil",
      description: "Delivery order berhasil diperbarui",
      icon: "i-lucide-check-circle",
      color: "success",
    });
    editOpen.value = false;
    refresh();
  } catch (err) {
    toast.add({
      title: "Gagal",
      description:
        err instanceof Error ? err.message : "Gagal memperbarui delivery order",
      icon: "i-lucide-alert-triangle",
      color: "error",
    });
  } finally {
    editLoading.value = false;
  }
}

// ── Modal Rilis Dana ──────────────────────────────────────────
const rilisDanaOpen = ref(false);
const rilisDanaTarget = ref<DeliveryOrderRow | null>(null);
const rilisDanaLoading = ref(false);

function openRilisDana(row: DeliveryOrderRow) {
  rilisDanaTarget.value = row;
  rilisDanaOpen.value = true;
}

async function confirmRilisDana() {
  if (rilisDanaLoading.value || !rilisDanaTarget.value) return;
  rilisDanaLoading.value = true;
  try {
    await post(`/delivery-orders/${rilisDanaTarget.value.id}/rilis-dana`, {});
    toast.add({
      title: "Berhasil",
      description: "Dana telah dirilis. DO tersedia di Operations.",
      color: "success",
    });
    rilisDanaOpen.value = false;
    rilisDanaTarget.value = null;
    refresh();
  } catch (err) {
    toast.add({
      title: "Gagal",
      description: err instanceof Error ? err.message : "Gagal merilis dana.",
      color: "error",
    });
  } finally {
    rilisDanaLoading.value = false;
  }
}

// ── Modal Lunas Ongkir ────────────────────────────────────────
const lunasOngkirOpen = ref(false);
const lunasOngkirTarget = ref<DeliveryOrderRow | null>(null);
const lunasOngkirLoading = ref(false);

function openLunasOngkir(row: DeliveryOrderRow) {
  lunasOngkirTarget.value = row;
  lunasOngkirOpen.value = true;
}

async function confirmLunasOngkir() {
  if (lunasOngkirLoading.value || !lunasOngkirTarget.value) return;
  lunasOngkirLoading.value = true;
  try {
    await post(
      `/delivery-orders/${lunasOngkirTarget.value.id}/lunas-ongkir`,
      {},
    );
    toast.add({
      title: "Berhasil",
      description: "Ongkir telah dilunasi.",
      color: "success",
    });
    lunasOngkirOpen.value = false;
    lunasOngkirTarget.value = null;
    refresh();
  } catch (err) {
    toast.add({
      title: "Gagal",
      description:
        err instanceof Error ? err.message : "Gagal melunasi ongkir.",
      color: "error",
    });
  } finally {
    lunasOngkirLoading.value = false;
  }
}

// ── Modal hapus ──────────────────────────────────────────────
const deleteOpen = ref(false);
const deleteTarget = ref<DeliveryOrderRow | null>(null);
const deleteLoading = ref(false);

function openDelete(row: DeliveryOrderRow) {
  deleteTarget.value = row;
  deleteOpen.value = true;
}

async function confirmDelete() {
  if (deleteLoading.value || !deleteTarget.value) return;
  deleteLoading.value = true;
  try {
    await del(`/delivery-orders/${deleteTarget.value.id}`);
    toast.add({
      title: "Berhasil",
      description: "Delivery order berhasil dihapus",
      icon: "i-lucide-check-circle",
      color: "success",
    });
    deleteOpen.value = false;
    deleteTarget.value = null;
    refresh();
  } catch (err) {
    toast.add({
      title: "Gagal",
      description:
        err instanceof Error ? err.message : "Gagal menghapus delivery order",
      icon: "i-lucide-alert-triangle",
      color: "error",
    });
  } finally {
    deleteLoading.value = false;
  }
}

const pagination = ref({ pageIndex: 0, pageSize: 7 });

const columns: TableColumn<DeliveryOrderRow>[] = [
  { accessorKey: "do_number", header: "Nomor DO" },
  { accessorKey: "customer_name", header: "Customer" },
  { accessorKey: "po_number", header: "Nomor PO" },
  { accessorKey: "transport_name", header: "Transportir" },
  {
    accessorKey: "fuel_total",
    header: "Volume (L)",
    cell: ({ row }) => formatNumber(row.original.fuel_total ?? 0),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) =>
      h(
        UBadge,
        {
          variant: "subtle",
          color: statusColor[row.original.status] ?? "neutral",
          class: "text-xs",
        },
        () => statusLabel[row.original.status] ?? row.original.status,
      ),
  },
  {
    accessorKey: "status_rilis_dana",
    header: "Rilis Dana",
    cell: ({ row }) =>
      statusBadge(
        row.original.status_rilis_dana,
        "Dirilis",
        row.original.rilis_dana_at,
      ),
  },
  {
    accessorKey: "status_ready_order",
    header: "Siap Kirim",
    cell: ({ row }) =>
      statusBadge(
        row.original.status_ready_order,
        "Siap",
        row.original.ready_order_at,
      ),
  },
  {
    accessorKey: "status_selesai_dikirim",
    header: "Selesai Kirim",
    cell: ({ row }) =>
      statusBadge(
        row.original.status_selesai_dikirim,
        "Selesai",
        row.original.selesai_dikirim_at,
      ),
  },
  {
    accessorKey: "status_lunas_ongkir",
    header: "Lunas Ongkir",
    cell: ({ row }) =>
      statusBadge(
        row.original.status_lunas_ongkir,
        "Lunas",
        row.original.lunas_ongkir_at,
      ),
  },
  { id: "actions", header: "Aksi", size: 300 },
];
</script>

<template>
  <UDashboardPanel id="admin-data-do">
    <template #header>
      <UDashboardNavbar title="Data Delivery Order" :ui="{ right: 'gap-3' }">
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
      <section class="flex flex-col gap-4 p-4 lg:p-6">
        <div class="flex items-center gap-2">
          <UInput
            v-model="search"
            icon="i-lucide-search"
            placeholder="Cari nomor DO, customer, PO, atau transportir..."
            class="w-72"
          />
        </div>

        <UCard>
          <UTable
            ref="table"
            v-model:pagination="pagination"
            :data="dos"
            :columns="columns"
            :column-pinning="columnPinning"
            :ui="{
              base: 'table-fixed border-separate border-spacing-0',
              thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
              tbody: '[&>tr]:last:[&>td]:border-b-0',
              th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
              td: 'border-b border-default',
            }"
            :pagination-options="{
              getPaginationRowModel: getPaginationRowModel(),
            }"
          >
            <template #actions-cell="{ row }">
              <div class="flex flex-col items-center gap-3">
                <div class="space-x-2">
                  <!-- Rilis Dana: belum dirilis -->
                  <UButton
                    v-if="!row.original.status_rilis_dana"
                    size="sm"
                    color="success"
                    variant="solid"
                    icon="i-lucide-circle-dollar-sign"
                    @click="openRilisDana(row.original)"
                  >
                    Rilis Dana
                  </UButton>

                  <!-- Lunasi Ongkir: muncul setelah siap dikirim (ready_order=true) dan belum lunas -->
                  <UButton
                    v-if="
                      row.original.status_ready_order &&
                      !row.original.status_lunas_ongkir
                    "
                    size="xs"
                    color="warning"
                    variant="solid"
                    icon="i-lucide-truck"
                    @click="openLunasOngkir(row.original)"
                  >
                    Lunasi Ongkir
                  </UButton>
                </div>

                <USeparator />

                <div class="flex gap-2 w-full">
                  <UButton
                    class="flex w-full"
                    icon="i-lucide-eye"
                    size="sm"
                    color="neutral"
                    variant="soft"
                    @click="openDetail(row.original.id)"
                  >
                    Lihat
                  </UButton>

                  <UButton
                    class="flex w-full"
                    icon="i-lucide-pencil"
                    size="sm"
                    color="info"
                    variant="soft"
                    @click="openEdit(row.original)"
                  >
                    Edit
                  </UButton>

                  <UButton
                    icon="i-lucide-trash-2"
                    size="sm"
                    color="error"
                    variant="soft"
                    @click="openDelete(row.original)"
                  >
                  </UButton>
                </div>
              </div>
            </template>
          </UTable>

          <UEmpty
            v-if="!dos.length"
            icon="i-lucide-file-search"
            title="Tidak ada data"
            description="Belum ada delivery order"
          />

          <div class="flex justify-end border-t border-default pt-4 px-4">
            <UPagination
              :page="
                (table?.tableApi?.getState().pagination.pageIndex || 0) + 1
              "
              :items-per-page="table?.tableApi?.getState().pagination.pageSize"
              :total="table?.tableApi?.getFilteredRowModel().rows.length"
              @update:page="(p) => table?.tableApi?.setPageIndex(p - 1)"
            />
          </div>
        </UCard>
      </section>
    </template>
  </UDashboardPanel>

  <!-- ── Modal Edit ── -->
  <UModal v-model:open="editOpen" :ui="{ content: 'max-w-lg' }">
    <template #title>
      <div class="flex items-center gap-2 text-info">
        <UIcon name="i-lucide-pencil" class="size-5" />
        Edit Delivery Order
      </div>
    </template>
    <template #body>
      <div class="space-y-4">
        <UFormField label="Nomor DO" required>
          <UInput v-model="form.do_number" placeholder="Contoh: DO-001" />
        </UFormField>
        <UFormField label="Customer" required>
          <USelect
            v-model="form.customer_id"
            :items="customerItems"
            value-key="value"
          />
        </UFormField>
        <div class="grid grid-cols-2 gap-3">
          <UFormField label="Nomor PO">
            <UInput v-model="form.po_number" placeholder="Contoh: PO-001" />
          </UFormField>
          <UFormField label="Transportir">
            <UInput
              v-model="form.transport_name"
              placeholder="Nama transportir"
            />
          </UFormField>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <UFormField label="Volume BBM (L)">
            <UInput v-model.number="form.fuel_total" type="number" />
          </UFormField>
          <UFormField label="Status">
            <USelect
              v-model="form.status"
              :items="[
                { label: 'Dibuat', value: 'created' },
                { label: 'Dokumen Kembali', value: 'document_returned' },
              ]"
              value-key="value"
            />
          </UFormField>
        </div>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton color="info" :loading="editLoading" @click="submitEdit">
          Simpan Perubahan
        </UButton>

        <UButton color="neutral" variant="ghost" @click="editOpen = false">
          Batal
        </UButton>
      </div>
    </template>
  </UModal>

  <!-- ── Modal Konfirmasi Hapus ── -->
  <UModal v-model:open="deleteOpen" :ui="{ content: 'max-w-md' }">
    <template #title>
      <div class="flex items-center gap-2 text-error">
        <UIcon name="i-lucide-triangle-alert" class="size-5" />
        Konfirmasi Hapus
      </div>
    </template>
    <template #body>
      <p class="text-sm text-muted">
        Apakah Anda yakin ingin menghapus Delivery Order
        <span class="font-semibold text-highlighted">{{
          deleteTarget?.do_number
        }}</span
        >?
      </p>
      <p class="mt-2 text-xs text-dimmed">
        Tindakan ini juga menghapus dokumen terkait dan tidak dapat dibatalkan.
      </p>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton color="error" :loading="deleteLoading" @click="confirmDelete">
          Konfirmasi
        </UButton>

        <UButton color="neutral" variant="ghost" @click="deleteOpen = false">
          Batal
        </UButton>
      </div>
    </template>
  </UModal>

  <RecordDetailModal :id="detailId" v-model:open="detailOpen" type="do" />

  <!-- ── Modal Konfirmasi Rilis Dana ── -->
  <UModal v-model:open="rilisDanaOpen" :ui="{ content: 'max-w-md' }">
    <template #title>
      <div class="flex items-center gap-2 text-success">
        <UIcon name="i-lucide-circle-dollar-sign" class="size-5" />
        Konfirmasi Rilis Dana
      </div>
    </template>
    <template #body>
      <p class="text-sm text-muted">
        Apakah Anda yakin ingin
        <span class="font-semibold text-highlighted">merilis dana</span>
        untuk Delivery Order
        <span class="font-semibold text-highlighted">{{
          rilisDanaTarget?.do_number
        }}</span
        >?
      </p>
      <p class="mt-2 text-xs text-dimmed">
        Setelah dirilis, DO akan muncul di halaman Operations dan tim dapat
        menyiapkan pengantaran.
      </p>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          color="success"
          :loading="rilisDanaLoading"
          icon="i-lucide-check"
          @click="confirmRilisDana"
        >
          Konfirmasi Rilis Dana
        </UButton>

        <UButton color="neutral" variant="ghost" @click="rilisDanaOpen = false">
          Batal
        </UButton>
      </div>
    </template>
  </UModal>

  <!-- ── Modal Konfirmasi Lunas Ongkir ── -->
  <UModal v-model:open="lunasOngkirOpen" :ui="{ content: 'max-w-md' }">
    <template #title>
      <div class="flex items-center gap-2 text-warning">
        <UIcon name="i-lucide-truck" class="size-5" />
        Konfirmasi Pelunasan Ongkir
      </div>
    </template>
    <template #body>
      <p class="text-sm text-muted">
        Apakah Anda ingin
        <span class="font-semibold text-highlighted">melunasi ongkir</span>
        untuk Delivery Order
        <span class="font-semibold text-highlighted">{{
          lunasOngkirTarget?.do_number
        }}</span
        >?
      </p>
      <p class="mt-2 text-xs text-dimmed">
        Tindakan ini akan menandai pelunasan ongkir dengan waktu saat ini (WITA)
        dan tidak dapat dibatalkan.
      </p>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          color="warning"
          :loading="lunasOngkirLoading"
          icon="i-lucide-check"
          @click="confirmLunasOngkir"
        >
          Konfirmasi Lunasi Ongkir
        </UButton>

        <UButton
          color="neutral"
          variant="ghost"
          @click="lunasOngkirOpen = false"
        >
          Batal
        </UButton>
      </div>
    </template>
  </UModal>
</template>
