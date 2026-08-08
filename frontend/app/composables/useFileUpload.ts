export interface TempFile {
  file: File
  previewUrl: string
  uploaded: boolean
  result?: ResUploads
}

export function useFileUpload() {
  const pendingFiles = ref<TempFile[]>([])
  const uploadedFiles = ref<ResUploads[]>([])
  const isUploading = ref(false)

  function addFiles(files: FileList | File[]) {
    const list = files instanceof FileList ? Array.from(files) : files
    for (const file of list) {
      const previewUrl = URL.createObjectURL(file)
      pendingFiles.value.push({ file, previewUrl, uploaded: false })
    }
  }

  function removeFile(index: number) {
    const item = pendingFiles.value[index]
    if (item) {
      URL.revokeObjectURL(item.previewUrl)
      pendingFiles.value.splice(index, 1)
    }
  }

  function cancelAll() {
    for (const item of pendingFiles.value) {
      URL.revokeObjectURL(item.previewUrl)
    }
    pendingFiles.value = []
  }

  async function uploadAll(
    folder: string,
    documentType?: string,
    documentId?: string
  ): Promise<ResUploads[]> {
    if (pendingFiles.value.length === 0) return []
    isUploading.value = true

    try {
      const payload: Uploads = {
        files: pendingFiles.value.map(f => f.file),
        folder,
        document_type: documentType || 'general',
        document_id: documentId || ''
      }

      const results = await postFile<ResUploads[]>('/upload', payload)

      for (const item of pendingFiles.value) {
        URL.revokeObjectURL(item.previewUrl)
        item.uploaded = true
      }

      uploadedFiles.value.push(...results)
      pendingFiles.value = []
      return results
    } finally {
      isUploading.value = false
    }
  }

  onUnmounted(() => {
    cancelAll()
  })

  return {
    pendingFiles,
    uploadedFiles,
    isUploading,
    addFiles,
    removeFile,
    cancelAll,
    uploadAll
  }
}
