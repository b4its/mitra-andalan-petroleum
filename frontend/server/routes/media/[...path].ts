import { proxyRequest } from 'h3'

const TARGET = process.env.NUXT_MEDIA_PROXY_TARGET || 'http://127.0.0.1:8012/media'

export default defineEventHandler((event) => {
  const queryIndex = event.path.indexOf('?')
  const rawPath = queryIndex >= 0 ? event.path.slice(0, queryIndex) : event.path
  const query = queryIndex >= 0 ? event.path.slice(queryIndex) : ''
  const rest = rawPath.replace(/^\/media\/?/, '')
  const url = `${TARGET}/${rest}${query}`.replace(/\/\?/, '?').replace(/\/$/, '')
  return proxyRequest(event, url)
})
