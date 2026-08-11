<script setup lang="ts">
interface Region {
  code: string
  name: string
}

interface RegionResponse {
  data: Region[]
}

const province = defineModel<string>('province', { default: '' })
const city = defineModel<string>('city', { default: '' })

const provinces = ref<Region[]>([])
const regencies = ref<Region[]>([])
const provincesLoading = ref(true)
const regenciesLoading = ref(false)
const provincesError = ref(false)
const regenciesError = ref(false)
const regencyCache = new Map<string, Region[]>()

onMounted(async () => {
  try {
    const res = await $fetch<RegionResponse>(
      'https://wilayah.id/api/provinces.json'
    )
    provinces.value = res.data || []
  } catch {
    provincesError.value = true
  } finally {
    provincesLoading.value = false
  }
})

const selectedProvince = computed(() =>
  provinces.value.find(p => p.name === province.value)
)

watch(
  () => selectedProvince.value?.code,
  async (code) => {
    if (!code) {
      regencies.value = []
      city.value = ''
      return
    }
    const cached = regencyCache.get(code)
    if (cached) {
      regencies.value = cached
      return
    }
    regenciesLoading.value = true
    regenciesError.value = false
    try {
      const res = await $fetch<RegionResponse>(
        `https://wilayah.id/api/regencies/${code}.json`
      )
      regencies.value = res.data || []
      regencyCache.set(code, regencies.value)
    } catch {
      regenciesError.value = true
    } finally {
      regenciesLoading.value = false
    }
  },
  { immediate: true }
)
</script>

<template>
  <div class="flex w-full gap-4">
    <UFormField label="Provinsi" class="w-full">
      <USelectMenu
        v-model="province"
        :items="provinces.map(p => p.name)"
        :loading="provincesLoading"
        :disabled="provincesLoading || provincesError"
        searchable
        placeholder="Pilih Provinsi"
      />
      <p v-if="provincesError" class="text-xs text-red-500 mt-1">
        Gagal memuat data provinsi.
      </p>
    </UFormField>

    <UFormField label="Kota/Kabupaten" class="w-full">
      <USelectMenu
        v-model="city"
        :items="regencies.map(r => r.name)"
        :loading="regenciesLoading"
        :disabled="!selectedProvince || regenciesLoading || regenciesError"
        searchable
        placeholder="Pilih Kota/Kabupaten"
      />
      <p v-if="regenciesError" class="text-xs text-red-500 mt-1">
        Gagal memuat data kota/kabupaten.
      </p>
    </UFormField>
  </div>
</template>
