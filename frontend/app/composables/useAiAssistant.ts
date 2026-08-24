/**
 * useAiAssistant — composable global untuk AI Assistant.
 *
 * Memakai useState agar state persist antar navigasi halaman (SSR-friendly).
 * Menyediakan:
 *  - isOpen          : boolean untuk membuka/menutup panel chat
 *  - messages        : riwayat percakapan
 *  - streaming       : status sedang streaming respons
 *  - error           : pesan error terakhir
 *  - context         : konteks data halaman (analisa/prediksi) yang diinjeksi
 *  - setContext()    : atur konteks analisa halaman saat ini
 *  - open()/close()/toggle()
 *  - send()          : kirim pesan + stream respons dari /api/ai/chat
 *  - analyze()       : minta AI menganalisa konteks halaman saat ini
 *  - clear()         : bersihkan riwayat
 */

export interface AiMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  /** apakah pesan ini sedang di-streaming (belum selesai) */
  streaming?: boolean
  /** timestamp iso */
  at: string
}

interface AiState {
  messages: AiMessage[]
  isOpen: boolean
  streaming: boolean
  error: string | null
  context: string | null
  contextTitle: string | null
}

function createState(): AiState {
  return {
    messages: [],
    isOpen: false,
    streaming: false,
    error: null,
    context: null,
    contextTitle: null
  }
}

function uid(): string {
  return (
    Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
  )
}

export function useAiAssistant() {
  const state = useState<AiState>('ai-assistant', createState)

  // ── Kontrol panel ─────────────────────────────────────────────
  function open() {
    state.value.isOpen = true
  }
  function close() {
    state.value.isOpen = false
  }
  function toggle() {
    state.value.isOpen = !state.value.isOpen
  }

  // ── Konteks halaman ───────────────────────────────────────────
  /**
   * Atur konteks analisa halaman. Dipanggil oleh halaman dashboard
   * yang punya data prediksi/analisa supaya AI bisa menganalisa data tsb.
   *
   * @param context  ringkasan data analisa (bisa JSON atau teks)
   * @param title    judul konteks (mis. "Dashboard Admin")
   */
  function setContext(context: string | null, title?: string | null) {
    state.value.context = context
    state.value.contextTitle = title ?? null
  }

  function clearContext() {
    state.value.context = null
    state.value.contextTitle = null
  }

  // ── Bersihkan riwayat ────────────────────────────────────────
  function clear() {
    state.value.messages = []
    state.value.error = null
  }

  // ── Parser SSE ───────────────────────────────────────────────
  function parseSSEChunk(chunk: string): string[] {
    const deltas: string[] = []
    const lines = chunk.split('\n')
    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed || !trimmed.startsWith('data:')) continue
      const data = trimmed.slice(5).trim()
      if (data === '[DONE]') continue
      try {
        const json = JSON.parse(data)
        const delta =
          json?.choices?.[0]?.delta?.content ??
          json?.choices?.[0]?.message?.content ??
          ''
        if (delta) deltas.push(delta)
      } catch {
        // bukan JSON valid, abaikan
      }
    }
    return deltas
  }

  // ── Kirim pesan + stream respons ─────────────────────────────
  async function send(text: string) {
    const content = text.trim()
    if (!content || state.value.streaming) return

    state.value.error = null

    const userMsg: AiMessage = {
      id: uid(),
      role: 'user',
      content,
      at: new Date().toISOString()
    }
    state.value.messages = [...state.value.messages, userMsg]

    // Tambahkan placeholder assistant yang akan diisi sambil streaming
    const assistantId = uid()
    const assistantMsg: AiMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      streaming: true,
      at: new Date().toISOString()
    }
    state.value.messages = [...state.value.messages, assistantMsg]
    state.value.streaming = true

    // Riwayat yang dikirim ke AI (tanpa placeholder streaming)
    const history = state.value.messages
      .filter((m) => !m.streaming && m.role !== 'system')
      .filter((m) => m.id !== assistantId)
      .map((m) => ({ role: m.role, content: m.content }))

    try {
      const res = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream'
        },
        body: JSON.stringify({
          messages: history,
          context: state.value.context,
          stream: true
        })
      })

      if (!res.ok) {
        const txt = await res.text().catch(() => res.statusText)
        throw new Error(
          `Gagal menghubungi AI (${res.status}): ${txt.slice(0, 300)}`
        )
      }

      if (!res.body) {
        // Fallback: non-streaming JSON
        const data = await res.json().catch(() => null)
        const reply = data?.content ?? '(tidak ada respons)'
        patchMessage(assistantId, reply, false)
        return
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        // Proses per-event (dipisah double newline)
        let idx: number
        while ((idx = buffer.indexOf('\n\n')) !== -1) {
          const chunk = buffer.slice(0, idx)
          buffer = buffer.slice(idx + 2)
          const deltas = parseSSEChunk(chunk)
          if (deltas.length) {
            appendToMessage(assistantId, deltas.join(''))
          }
        }
        // Juga tangani baris data tunggal tanpa double-newline
        if (buffer.startsWith('data:') && buffer.endsWith('\n')) {
          const deltas = parseSSEChunk(buffer)
          if (deltas.length) {
            appendToMessage(assistantId, deltas.join(''))
          }
          buffer = ''
        }
      }

      // Sisa buffer
      if (buffer.trim()) {
        const deltas = parseSSEChunk(buffer)
        if (deltas.length) {
          appendToMessage(assistantId, deltas.join(''))
        }
      }

      patchMessage(assistantId, '', false)
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : 'Terjadi kesalahan saat menghubungi AI.'
      state.value.error = msg
      patchMessage(
        assistantId,
        `⚠️ ${msg}`,
        false
      )
    } finally {
      state.value.streaming = false
    }
  }

  // ── Minta AI menganalisa konteks halaman ─────────────────────
  async function analyze(extraHint?: string) {
    const ctx = state.value.context
    if (!ctx) {
      await send(
        extraHint ||
          'Tolong berikan analisa dan prediksi umum untuk halaman ini.'
      )
      return
    }
    const prompt =
      `Analisa data ${state.value.contextTitle ?? 'halaman'} berikut. ` +
      `Tampilkan: ringkasan kondisi saat ini, tren yang terlihat, ` +
      `potensi anomali/risiko, dan rekomendasi tindakan. ` +
      (extraHint ? `\n\n${extraHint}` : '')
    await send(prompt)
  }

  // ── Helper mutasi pesan ──────────────────────────────────────
  function patchMessage(id: string, content: string, streaming: boolean) {
    const msgs = [...state.value.messages]
    const i = msgs.findIndex((m) => m.id === id)
    if (i === -1) return
    const cur = msgs[i]
    if (!cur) return
    msgs[i] = {
      ...cur,
      content: content ? cur.content + content : cur.content,
      streaming
    }
    state.value.messages = msgs
  }

  function appendToMessage(id: string, delta: string) {
    patchMessage(id, delta, true)
  }

  return {
    state: readonly(state),
    isOpen: computed(() => state.value.isOpen),
    messages: computed(() => state.value.messages),
    streaming: computed(() => state.value.streaming),
    error: computed(() => state.value.error),
    context: computed(() => state.value.context),
    contextTitle: computed(() => state.value.contextTitle),
    open,
    close,
    toggle,
    setContext,
    clearContext,
    send,
    analyze,
    clear
  }
}
