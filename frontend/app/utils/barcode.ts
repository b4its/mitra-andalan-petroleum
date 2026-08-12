import bwipjs from 'bwip-js'

/**
 * Generate QR Code sebagai data URL PNG.
 * Dipakai untuk tanda tangan pada dokumen marketing.
 */
export function generateBarcodeDataUrl(text: string): string {
  if (!text || typeof document === 'undefined') return ''
  try {
    const canvas = document.createElement('canvas')
    bwipjs.toCanvas(canvas, {
      bcid: 'qrcode',
      text: text.trim(),
      scale: 5
    })
    return canvas.toDataURL('image/png')
  } catch {
    return ''
  }
}
