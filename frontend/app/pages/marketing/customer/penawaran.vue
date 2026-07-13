<script setup lang="ts">
import * as z from "zod";
import type { FormSubmitEvent, StepperItem } from "@nuxt/ui";

const items: StepperItem[] = [
  { title: "Kop Surat Penawaran", slot: "letterHeader" },
  { title: "Rincian Penawaran", slot: "letterOfferDetails" },
  { title: "Penutup Surat Penawaran", slot: "letterFooter" },
];

const letterHeaderSchema = z.object({
  location: z.string(),
  date: z.string(),
  offeringLetterNumber: z.string(),
  regarding: z.string(),
  receiver: z.string(),
});

const letterOfferDetailsSchema = z.object({
  supplyPoint: z.string(),
  qualityAssurance: z.string(),
  custodyTransfer: z.string(),
  unloadingProcedure: z.string(),
  volumeUnit: z.string(),
  volumeTolerance: z.number().min(0),
  paymentTerm: z.number().min(1),
  latePenalty: z.number().min(1),
  servicePattern: z.string(),
  personInCharge: z.object({
    name: z.string(),
    phoneNumber: z.string().length(11, "Phone Number"),
  }),
  paymentAddress: z.object({
    bankName: z.string(),
    accountNumber: z.string(),
    accountName: z.string(),
  }),
  fuelPrices: z.object({
    logisticInformation: z.string(),
    productName: z.string(),
    sellingPrice: z.object({
      ppkb: z.number(),
      oat: z.number().or(z.null()),
    }),
    ppn: z.number(),
  }),
});

const letterFooterSchema = z.object({
  purchaseOrderDeadline: z.number(),
  offeror: z.object({
    name: z.string(),
    signature: z.string(),
  }),
  companyInformation: z.object({
    address: z.string(),
    phoneNumber: z.string(),
    email: z.email(),
  }),
});

type LetterHeader = z.infer<typeof letterHeaderSchema>;
type LetterOfferDetails = z.infer<typeof letterOfferDetailsSchema>;
type LetterFooter = z.infer<typeof letterFooterSchema>;

const letterHeader = reactive<Partial<LetterHeader>>({
  location: "Samarinda",
  date: `${new Date().toISOString().split("T")[0]}`,
  offeringLetterNumber: "722",
  regarding: "Surat Penawaran Harga Bahan Bakar Minyak Bio diesel",
  receiver: "PT. Nuxtlabs",
});

const letterOfferDetails = reactive<Partial<LetterOfferDetails>>({
  supplyPoint: "PT. Nuxtlabs",
  qualityAssurance: "PT. Nuxtlabs",
  custodyTransfer: "PT. Nuxtlabs",
  unloadingProcedure: "PT. Nuxtlabs",
  volumeUnit: "Liter",
  volumeTolerance: 0.025,
  paymentTerm: 7,
  latePenalty: 0.02,
  servicePattern: "PT. Nuxtlabs",
  personInCharge: {
    name: "PT. Nuxtlabs",
    phoneNumber: "08123456789",
  },
  paymentAddress: {
    bankName: "BANK MANDIRI cab Segiri",
    accountNumber: "1480002719998",
    accountName: "PT. MITRA ANDALAN PETROLEUM",
  },
  fuelPrices: {
    logisticInformation: "PT. Nuxtlabs",
    productName: "PT. Nuxtlabs",
    sellingPrice: {
      ppkb: 17950,
      oat: 450,
    },
    ppn: 2024,
  },
});

const totalFuelPrices = computed(() => {
  return (
    letterOfferDetails.fuelPrices.sellingPrice.ppkb +
    letterOfferDetails.fuelPrices.sellingPrice.oat +
    letterOfferDetails.fuelPrices.ppn
  );
});

const letterFooter = reactive<Partial<LetterFooter>>({
  purchaseOrderDeadline: 30,
  offeror: {
    name: "PT. Nuxtlabs",
    signature: "PT. Nuxtlabs",
  },
  companyInformation: {
    address: "Jl. Belatuk No. 63 Samarinda, 75117 Indonesia",
    phoneNumber: "08123456789", // add masking
    email: "marketing.mapetroleum@gmail.com",
  },
});

// const toast = useToast();
// async function onSubmit(event: FormSubmitEvent<ProfileSchema>) {
//   toast.add({
//     title: "Success",
//     description: "Your settings have been updated.",
//     icon: "i-lucide-check",
//     color: "success",
//   });
//   console.log(event.data);
// }

const stepper = useTemplateRef("stepper");

definePageMeta({ layout: "marketing" });
</script>

<template>
  <UStepper ref="stepper" :items>
    <template #letterHeader>
      <UForm
        id="letter-header"
        :schema="letterHeaderSchema"
        :state="letterHeader"
        :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
      >
        <UPageCard variant="soft">
          <div class="flex w-full gap-4">
            <UFormField name="location" label="Lokasi" required>
              <UInput
                v-model="letterHeader.location"
                type="text"
                autocomplete="off"
              />
            </UFormField>

            <UFormField name="date" label="Tanggal Dibuat" required>
              <UInput
                v-model="letterHeader.date"
                type="date"
                autocomplete="off"
              />
            </UFormField>
          </div>

          <USeparator />

          <UFormField name="regarding" label="Perihal Surat" required>
            <UInput
              v-model="letterHeader.regarding"
              type="text"
              autocomplete="off"
            />
          </UFormField>

          <UFormField name="offeringLetterNumber" label="Nomor Surat" required>
            <UInput
              v-model="letterHeader.offeringLetterNumber"
              type="text"
              autocomplete="off"
            />
          </UFormField>

          <UFormField name="receiver" label="Yang Terhormat" required>
            <UInput
              v-model="letterHeader.receiver"
              type="text"
              autocomplete="off"
            />
          </UFormField>
        </UPageCard>
      </UForm>
    </template>

    <template #letterOfferDetails>
      <UForm
        id="letter-details"
        :schema="letterOfferDetailsSchema"
        :state="letterOfferDetails"
        :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
      >
        <UPageCard variant="soft">
          <div class="flex w-full gap-4">
            <UFormField name="supplyPoint" label="Supply Point" required>
              <UInput
                v-model="letterOfferDetails.supplyPoint"
                type="text"
                autocomplete="off"
              />
            </UFormField>

            <UFormField
              name="qualityAssurance"
              label="Jaminan Kualitas"
              required
            >
              <UInput
                v-model="letterOfferDetails.qualityAssurance"
                type="text"
                autocomplete="off"
              />
            </UFormField>
          </div>

          <USeparator />

          <div class="flex w-full gap-4">
            <UFormField
              name="custodyTransfer"
              label="Custody Transfer"
              required
            >
              <UInput
                v-model="letterOfferDetails.custodyTransfer"
                type="text"
                autocomplete="off"
              />
            </UFormField>

            <UFormField
              name="unloadingProcedure"
              label="Prosedur Bongkar"
              required
            >
              <UInput
                v-model="letterOfferDetails.unloadingProcedure"
                type="text"
                autocomplete="off"
              />
            </UFormField>
          </div>

          <USeparator />

          <div class="flex w-full gap-4">
            <UFormField name="volumeUnit" label="Satuan Volume" required>
              <UInput
                v-model="letterOfferDetails.volumeUnit"
                type="text"
                autocomplete="off"
              />
            </UFormField>

            <UFormField
              name="volumeTolerance"
              label="Toleransi Volume"
              required
            >
              <UInputNumber
                :ui="{
                  root: 'w-full',
                }"
                v-model="letterOfferDetails.volumeTolerance"
                orientation="vertical"
                :step="0.005"
                :format-options="{
                  style: 'percent',
                  minimumFractionDigits: 1,
                }"
              />
            </UFormField>
          </div>

          <USeparator />

          <UFormField name="paymentTerm" label="Term Pembayaran" required>
            <UInputNumber
              :ui="{
                root: 'w-full',
              }"
              v-model="letterOfferDetails.paymentTerm"
              orientation="vertical"
              :step="1"
              locale="id-ID"
              :format-options="{
                style: 'unit',
                unit: 'week',
                unitDisplay: 'long',
              }"
            />
          </UFormField>

          <div class="flex w-full gap-4">
            <UFormField
              name="latePenalty"
              label="Penalty Keterlambatan"
              required
            >
              <UInputNumber
                :ui="{
                  root: 'w-full',
                }"
                v-model="letterOfferDetails.latePenalty"
                orientation="vertical"
                :step="0.01"
                :format-options="{
                  style: 'percent',
                }"
              />
            </UFormField>

            <UFormField name="servicePattern" label="Pola Pelayanan" required>
              <UInput
                v-model="letterOfferDetails.servicePattern"
                type="text"
                autocomplete="off"
              />
            </UFormField>
          </div>

          <USeparator />

          <p>Person In Charge</p>

          <div class="flex w-full gap-4">
            <UFormField name="personName" label="Nama" required>
              <UInput
                v-model="letterOfferDetails.personInCharge.name"
                type="text"
                autocomplete="off"
              />
            </UFormField>

            <UFormField name="personNumber" label="Nomor Telepon" required>
              <UInput
                v-model="letterOfferDetails.personInCharge.phoneNumber"
                type="text"
                autocomplete="off"
              />
            </UFormField>
          </div>

          <USeparator />

          <p>Rekening Pembayaran</p>

          <div class="flex flex-col w-full gap-4">
            <UFormField name="bankName" label="Nama Bank" required>
              <UInput
                v-model="letterOfferDetails.paymentAddress.bankName"
                type="text"
                autocomplete="off"
              />
            </UFormField>

            <UFormField name="accountNumber" label="Nomor Rekening" required>
              <UInput
                v-model="letterOfferDetails.paymentAddress.accountNumber"
                type="text"
                autocomplete="off"
              />
            </UFormField>

            <UFormField name="accountName" label="Nama Rekening" required>
              <UInput
                v-model="letterOfferDetails.paymentAddress.accountName"
                type="text"
                autocomplete="off"
              />
            </UFormField>
          </div>

          <USeparator />

          <p>Harga Bahan Bakar Minyak</p>

          <div class="flex w-full gap-4">
            <UFormField
              name="logisticInformation"
              label="Informasi Logistik"
              required
            >
              <UInput
                v-model="letterOfferDetails.fuelPrices.logisticInformation"
                type="text"
                autocomplete="off"
              />
            </UFormField>

            <UFormField name="productName" label="Produk" required>
              <UInput
                v-model="letterOfferDetails.fuelPrices.productName"
                type="text"
                autocomplete="off"
              />
            </UFormField>
          </div>

          <div class="flex w-full gap-4">
            <UFormField name="ppkb" label="PPKB" required>
              <UInputNumber
                :ui="{
                  root: 'w-full',
                }"
                v-model="letterOfferDetails.fuelPrices.sellingPrice.ppkb"
                :increment="false"
                :decrement="false"
                :format-options="{
                  style: 'currency',
                  currency: 'IDR',
                  currencyDisplay: 'narrowSymbol',
                  currencySign: 'standard',
                }"
              />
            </UFormField>

            <UFormField name="oat" label="OAT" required>
              <UInputNumber
                :ui="{
                  root: 'w-full',
                }"
                v-model="letterOfferDetails.fuelPrices.sellingPrice.oat"
                :increment="false"
                :decrement="false"
                :format-options="{
                  style: 'currency',
                  currency: 'IDR',
                  currencyDisplay: 'narrowSymbol',
                  currencySign: 'standard',
                }"
              />
            </UFormField>
          </div>

          <UFormField
            name="ppn"
            label="PPN (11%)"
            description="Harga Jual & Ongkos Angkut"
            required
          >
            <UInputNumber
              :ui="{
                root: 'w-full',
              }"
              v-model="letterOfferDetails.fuelPrices.ppn"
              :increment="false"
              :decrement="false"
              :format-options="{
                style: 'currency',
                currency: 'IDR',
                currencyDisplay: 'narrowSymbol',
                currencySign: 'standard',
              }"
            />
          </UFormField>

          <UFormField name="total" label="Total">
            <UInputNumber
              :ui="{
                root: 'w-full',
              }"
              v-model="totalFuelPrices"
              :increment="false"
              :decrement="false"
              :format-options="{
                style: 'currency',
                currency: 'IDR',
                currencyDisplay: 'narrowSymbol',
                currencySign: 'standard',
              }"
              disabled
            />
          </UFormField>

          <USeparator />
        </UPageCard>
      </UForm>
    </template>

    <template #letterFooter>
      <UForm
        id="letter-footer"
        :schema="letterFooterSchema"
        :state="letterFooter"
        :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
      >
        <UPageCard variant="soft">
          <UFormField
            name="purchaseOrderDeadline"
            label="Tenggat Purchase Order (PO)"
            required
          >
            <UInputNumber
              :ui="{
                root: 'w-full',
              }"
              v-model="letterOfferDetails.paymentTerm"
              orientation="vertical"
              :step="1"
              locale="id-ID"
              :format-options="{
                style: 'unit',
                unit: 'day',
                unitDisplay: 'long',
              }"
            />
          </UFormField>

          <USeparator />

          <UFormField name="offerorName" label="Hormat Kami" required>
            <UInput
              v-model="letterFooter.offeror.name"
              type="text"
              autocomplete="off"
            />
          </UFormField>

          <UFormField name="offerorSignature" label="Tanda Tangan" required>
            <UFileUpload
              label="Upload File Tanda Tangan"
              description="Format file .png dengan max 2MB"
            />
          </UFormField>

          <USeparator />

          <p>Informasi Perusahaan</p>

          <UFormField name="address" label="Alamat" required>
            <UInput
              v-model="letterFooter.companyInformation.address"
              type="text"
              autocomplete="off"
            />
          </UFormField>

          <div class="flex w-full gap-4">
            <UFormField name="phoneNumber" label="Nomor Telepon" required>
              <UInput
                v-model="letterFooter.companyInformation.phoneNumber"
                type="text"
                autocomplete="off"
              />
            </UFormField>

            <UFormField name="email" label="Alamat Email" required>
              <UInput
                v-model="letterFooter.companyInformation.email"
                type="email"
                autocomplete="off"
              />
            </UFormField>
          </div>
        </UPageCard>
      </UForm>
    </template>
  </UStepper>

  <div class="flex gap-2 justify-between mt-4">
    <UButton
      leading-icon="i-lucide-arrow-left"
      :disabled="!stepper?.hasPrev"
      @click="stepper?.prev()"
    >
      Sebelumnya
    </UButton>

    <UButton
      trailing-icon="i-lucide-arrow-right"
      :disabled="!stepper?.hasNext"
      @click="stepper?.next()"
    >
      Selanjutnya
    </UButton>
  </div>
</template>
