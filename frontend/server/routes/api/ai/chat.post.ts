import { createError, defineEventHandler, readBody, setResponseHeader, sendStream } from 'h3'
import type { H3Event } from 'h3'

/**
 * Server-side proxy untuk AI Assistant.
 *
 * Meneruskan permintaan chat ke endpoint OpenAI-compatible:
 *   {baseURL}/chat/completions
 *
 * API key & model diatur di server (runtimeConfig.ai), sehingga tidak
 * bocor ke klien. Mendukung mode streaming (SSE) maupun respons penuh.
 *
 * Body yang diterima dari klien:
 *   {
 *     messages: Array<{ role, content }>,   // riwayat percakapan
 *     context?: string,                    // konteks analisa halaman (opsional)
 *     system?: string,                      // system prompt tambahan (opsional)
 *     stream?: boolean,                     // default true
 *     temperature?: number
 *   }
 */

interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

interface ClientRequestBody {
  messages?: ChatMessage[]
  context?: string
  system?: string
  stream?: boolean
  temperature?: number
}

const DEFAULT_SYSTEM =
  'Kamu adalah AI Assistant internal untuk sistem manajemen "Mitra Andalan Petroleum" ' +
  '(perusahaan distributor BBM). Jawab dalam Bahasa Indonesia yang sopan, ringkas, dan jelas. ' +
  'Jika diberi konteks data analisa/prediksi halaman, gunakan data tersebut untuk memberikan ' +
  'insight, tren, anomali, dan rekomendasi yang relevan. Jika data tidak cukup, sebutkan dengan jelas.'

export default defineEventHandler(async (event: H3Event) => {
  const config = useRuntimeConfig()
  const baseURL = config.ai?.baseURL || 'http://localhost:20128/v1'
  const apiKey = config.ai?.apiKey || 'sk-dede08aea594e222-upk4p8-5bfa2c54'
  const model = config.ai?.model || 'qd/dmodel'

  const body = await readBody<ClientRequestBody>(event)

  if (!body || !Array.isArray(body.messages) || body.messages.length === 0) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Bad Request',
      message: 'Field "messages" wajib diisi dan tidak boleh kosong.'
    })
  }

  // Susun system prompt: default + system tambahan + konteks halaman
  const systemParts: string[] = [DEFAULT_SYSTEM]
  if (body.system) systemParts.push(body.system)
  if (body.context && body.context.trim()) {
    systemParts.push(
      `\n=== KONTEKS DATA HALAMAN INI ===\n${body.context.trim()}\n=== AKHIR KONTEKS ===\n` +
      'Gunakan konteks di atas sebagai sumber data primer untuk menjawab pertanyaan terkait halaman ini.'
    )
  }

  const upstreamMessages: ChatMessage[] = [
    { role: 'system', content: systemParts.join('\n\n') },
    ...body.messages
  ]

  const stream = body.stream !== false
  const temperature =
    typeof body.temperature === 'number' ? body.temperature : 0.6

  const upstreamUrl = `${baseURL.replace(/\/$/, '')}/chat/completions`

  const upstreamPayload = {
    model,
    messages: upstreamMessages,
    stream,
    temperature
  }

  // ── Non-streaming: kembalikan JSON penuh ───────────────────────
  if (!stream) {
    try {
      const res = await fetch(upstreamUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${apiKey}`
        },
        body: JSON.stringify(upstreamPayload)
      })

      if (!res.ok) {
        const txt = await res.text().catch(() => res.statusText)
        throw createError({
          statusCode: res.status,
          statusMessage: 'AI upstream error',
          message: `AI gagal merespon (${res.status}): ${txt.slice(0, 500)}`
        })
      }

      const data = await res.json()
      return {
        content: data?.choices?.[0]?.message?.content ?? '',
        raw: data
      }
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : 'Gagal menghubungi AI upstream.'
      throw createError({ statusCode: 502, statusMessage: 'Bad Gateway', message })
    }
  }

  // ── Streaming: proxy SSE secara langsung ke klien ──────────────
  setResponseHeader(event, 'Content-Type', 'text/event-stream')
  setResponseHeader(event, 'Cache-Control', 'no-cache, no-transform')
  setResponseHeader(event, 'Connection', 'keep-alive')
  setResponseHeader(event, 'X-Accel-Buffering', 'no')

  try {
    const res = await fetch(upstreamUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
        Accept: 'text/event-stream'
      },
      body: JSON.stringify(upstreamPayload)
    })

    if (!res.ok || !res.body) {
      const txt = await res.text().catch(() => res.statusText)
      throw createError({
        statusCode: res.status,
        statusMessage: 'AI upstream error',
        message: `AI gagal merespon (${res.status}): ${txt.slice(0, 500)}`
      })
    }

    // Stream langsung dari upstream ke klien (SSE sudah dalam format yang benar)
    return sendStream(event, res.body as unknown as ReadableStream)
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'statusCode' in err) {
      throw err
    }
    const message =
      err instanceof Error ? err.message : 'Gagal streaming dari AI upstream.'
    throw createError({
      statusCode: 502,
      statusMessage: 'Bad Gateway',
      message
    })
  }
})
