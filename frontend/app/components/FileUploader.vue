<script setup lang="ts">
import type { ResUploads } from "~/types";
import { useFileUpload } from "~/composables/useFileUpload";

const props = defineProps<{
  folder: string;
  documentType?: string;
  documentId?: string;
  label?: string;
  description?: string;
  accept?: string;
  multiple?: boolean;
}>();

const emit = defineEmits<{
  uploaded: [files: ResUploads[]];
}>();

const {
  pendingFiles,
  uploadedFiles,
  isUploading,
  addFiles,
  removeFile,
  cancelAll,
  uploadAll,
} = useFileUpload();

const dropZoneRef = ref<HTMLDivElement>();

function onDrop(files: FileList | File[]) {
  addFiles(files);
}

function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files?.length) {
    addFiles(target.files);
    target.value = "";
  }
}

function onRemove(index: number) {
  removeFile(index);
}

function onCancelAll() {
  cancelAll();
}

async function onUploadAll() {
  const results = await uploadAll(
    props.folder,
    props.documentType,
    props.documentId,
  );
  if (results.length) {
    emit("uploaded", results);
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

function isImage(mime: string): boolean {
  return mime.startsWith("image/");
}
</script>

<template>
  <div class="space-y-4">
    <!-- Drop zone -->
    <div
      ref="dropZoneRef"
      class="relative flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-neutral-300 p-6 transition hover:border-primary-400 dark:border-neutral-600"
      @dragover.prevent
      @drop.prevent="event => event.dataTransfer?.files && onDrop(event.dataTransfer.files)"
    >
      <UIcon name="i-lucide-upload" class="mb-2 size-8 text-neutral-400" />
      <p class="text-sm font-medium">
        {{ label || "Upload File" }}
      </p>
      <p v-if="description" class="mt-1 text-xs text-neutral-400">
        {{ description }}
      </p>
      <UButton tag="label" size="sm" variant="soft" class="mt-3 cursor-pointer">
        Pilih File
        <input
          type="file"
          :accept="accept"
          :multiple="multiple ?? true"
          class="hidden"
          @change="onFileChange"
        />
      </UButton>
    </div>

    <!-- Preview grid -->
    <div v-if="pendingFiles.length" class="space-y-3">
      <div class="flex items-center justify-between">
        <p class="text-sm font-medium">
          {{ pendingFiles.length }} file dipilih
        </p>
        <div class="flex gap-2">
          <UButton
            size="xs"
            color="primary"
            :loading="isUploading"
            :disabled="isUploading"
            @click="onUploadAll"
          >
            Upload Semua
          </UButton>

          <UButton size="xs" color="error" variant="ghost" @click="onCancelAll">
            Batal Semua
          </UButton>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
        <div
          v-for="(item, index) in pendingFiles"
          :key="item.previewUrl"
          class="group relative overflow-hidden rounded-lg border border-neutral-200 bg-neutral-50 dark:border-neutral-700 dark:bg-neutral-800"
        >
          <!-- Image preview -->
          <div
            v-if="isImage(item.file.type)"
            class="flex aspect-square items-center justify-center bg-neutral-100 dark:bg-neutral-700"
          >
            <img
              :src="item.previewUrl"
              :alt="item.file.name"
              class="size-full object-cover"
            />
          </div>

          <!-- Non-image icon -->
          <div
            v-else
            class="flex aspect-square items-center justify-center bg-neutral-100 dark:bg-neutral-700"
          >
            <UIcon name="i-lucide-file" class="size-10 text-neutral-400" />
          </div>

          <!-- File info -->
          <div class="p-2">
            <p class="truncate text-xs font-medium">
              {{ item.file.name }}
            </p>
            <p class="text-xs text-neutral-400">
              {{ formatSize(item.file.size) }}
            </p>
          </div>

          <!-- Remove button -->
          <button
            class="absolute right-1 top-1 flex size-6 items-center justify-center rounded-full bg-black/50 text-white opacity-0 transition group-hover:opacity-100"
            @click="onRemove(index)"
          >
            <UIcon name="i-lucide-x" class="size-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Uploaded files -->
    <div v-if="uploadedFiles.length" class="space-y-2">
      <p class="text-sm font-medium text-green-600">Telah diupload:</p>
      <div
        v-for="upload in uploadedFiles"
        :key="upload.id"
        class="flex items-center gap-3 rounded-lg border border-green-200 bg-green-50 p-3 dark:border-green-800 dark:bg-green-900/20"
      >
        <UIcon
          name="i-lucide-check-circle"
          class="size-5 shrink-0 text-green-500"
        />
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-medium">
            {{ upload.original_filename }}
          </p>
          <a
            :href="upload.url"
            target="_blank"
            class="text-xs text-primary-500 underline"
          >
            {{ upload.url }}
          </a>
        </div>
        <span class="shrink-0 text-xs text-neutral-400">{{ upload.size }}</span>
      </div>
    </div>
  </div>
</template>
