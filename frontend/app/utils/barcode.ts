import bwipjs from 'bwip-js'

/**
 * Generate barcode (Code128) sebagai data URL PNG.
 * Dipakai untuk tanda tangan yang dijadikan barcode pada dokumen marketing.
 */
export function generateBarcodeDataUrl(text: string): string {
  if (!text || typeof document === 'undefined') return ''
  try {
    const canvas = document.createElement('canvas')
    bwipjs.toCanvas(canvas, {
      bcid: 'code128',
      text: text.trim().toUpperCase(),
      scale: 3,
      height: 12,
      includetext: true,
      textxalign: 'center',
      textsize: 10
    })
    return canvas.toDataURL('image/png')
  } catch {
    return ''
  }
}
