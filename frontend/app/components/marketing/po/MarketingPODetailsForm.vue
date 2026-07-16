<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui";
import {
  marketingPODetailsSchema,
  type MarketingPODetailsState,
} from "~/types/schemas";

defineProps<{
  hasPrevious: boolean | undefined;
}>();

const emit = defineEmits<{
  submit: [];
  previous: [];
}>();

const state = defineModel<MarketingPODetailsState>({ required: true });
function emptyProduct() {
  return { name: "", qty: 1, unit: "", price: 0, totalPrice: 0 };
}

const products = computed(() => state.value.products);

function addItem() {
  if (!state.value.products) {
    state.value.products = [];
  }
  state.value.products.push(emptyProduct());
}

function removeItem(index: number) {
  state.value.products.splice(index, 1);
}

// Keep row totalPrice + grand total in sync
watch(
  () => state.value.products,
  (products) => {
    products?.forEach((p) => {
      p.totalPrice = (p.qty || 0) * (p.price || 0);
    });
    state.value.totalProductsPrice = (products || []).reduce(
      (sum, p) => sum + (p.totalPrice || 0),
      0,
    );
  },
  { deep: true, immediate: true },
);

function previous() {
  emit("previous");
}

function onSubmit(_event: FormSubmitEvent<MarketingPODetailsState>) {
  emit("submit");
}
</script>

<template>
  <UForm
    id="letter-associate"
    :schema="marketingPODetailsSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-4xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Deskripsi Purchase Order Produk</p>

      <div class="flex w-full gap-4">
        <UFormField
          name="po.date"
          label="Tanggal Dibuat"
          required
          class="flex-1"
        >
          <UInput
            v-model="state.po.date"
            type="date"
            autocomplete="off"
            class="w-full"
          />
        </UFormField>

        <UFormField name="po.number" label="Nomor PO" required class="flex-1">
          <UInput
            v-model="state.po.number"
            type="text"
            autocomplete="off"
            placeholder="Contoh 0543/PO/MAP/I/05/26"
            class="w-full"
          />
        </UFormField>
      </div>

      <USeparator />

      <p>Rekening Pembayaran</p>

      <div class="flex w-full gap-4">
        <UFormField name="bankName" label="Nama Bank" required>
          <UInput
            v-model="state.paymentAddress.bankName"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="accountNumber" label="Nomor Rekening" required>
          <UInput
            v-model="state.paymentAddress.accountNumber"
            type="text"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <div class="flex w-full gap-4">
        <UFormField name="accountName" label="Nama Rekening" required>
          <UInput
            v-model="state.paymentAddress.accountName"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField label="VAT" name="vat" class="w-full" required>
          <UInputNumber
            :ui="{
              root: 'w-full',
            }"
            v-model="state.vat"
            orientation="vertical"
            :step="0.01"
            :format-options="{
              style: 'percent',
            }"
          />
        </UFormField>
      </div>

      <USeparator />

      <div class="space-y-3">
        <p class="font-medium">Daftar Produk</p>

        <div
          v-for="(product, index) in products"
          :key="`product-${index}`"
          class="flex items-end gap-2"
        >
          <UFormField
            :name="`products.${index}.name`"
            label="Produk"
            class="w-full"
            required
          >
            <UInput v-model="product.name" placeholder="Nama produk" />
          </UFormField>

          <UFormField
            :name="`products.${index}.qty`"
            label="Qty"
            class="w-full"
            required
          >
            <UInputNumber v-model="product.qty" :min="1" />
          </UFormField>

          <UFormField
            :name="`products.${index}.unit`"
            label="Unit"
            class="w-full"
            required
          >
            <UInput v-model="product.unit" placeholder="pcs" />
          </UFormField>

          <UFormField
            :name="`products.${index}.price`"
            label="Harga Unit"
            class="w-full"
            required
          >
            <UInputNumber
              locale="id-ID"
              :format-options="{
                style: 'currency',
                currency: 'IDR',
                currencyDisplay: 'narrowSymbol',
              }"
              :step="1000"
              v-model="product.price"
              :min="0"
            />
          </UFormField>

          <UFormField
            :name="`products.${index}.totalPrice`"
            label="Total"
            class="w-full"
            required
          >
            <UInputNumber
              locale="id-ID"
              :format-options="{
                style: 'currency',
                currency: 'IDR',
                currencyDisplay: 'narrowSymbol',
              }"
              :decrement="false"
              :increment="false"
              v-model="product.totalPrice"
              disabled
            />
          </UFormField>

          <UButton
            icon="i-lucide-trash-2"
            color="error"
            variant="ghost"
            :disabled="state.products.length === 1"
            @click="removeItem(index)"
          />
        </div>

        <UButton
          icon="i-lucide-plus"
          color="neutral"
          variant="subtle"
          size="sm"
          label="Tambah produk"
          @click="addItem"
        />

        <div class="flex justify-end pt-2 font-semibold">
          SubTotal: {{ formatCurrency(state.totalProductsPrice) }}
        </div>
      </div>

      <div class="flex justify-between pt-4">
        <UButton
          variant="ghost"
          color="neutral"
          leading-icon="i-lucide-arrow-left"
          :disabled="!hasPrevious"
          @click="previous"
        >
          Sebelumnya
        </UButton>

        <UButton type="submit" trailing-icon="i-lucide-arrow-right">
          Selanjutnya
        </UButton>
      </div>
    </UPageCard>
  </UForm>
</template>
