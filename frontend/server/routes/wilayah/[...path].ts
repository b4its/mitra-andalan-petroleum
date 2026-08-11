import { proxyRequest } from 'h3'

const TARGET = 'https://wilayah.id/api'

export default defineEventHandler((event) => {
  const queryIndex = event.path.indexOf('?')
  const rawPath = queryIndex >= 0 ? event.path.slice(0, queryIndex) : event.path
  const query = queryIndex >= 0 ? event.path.slice(queryIndex) : ''
  const rest = rawPath.replace(/^\/wilayah\/?/, '')
  const url = `${TARGET}/${rest}${query}`.replace(/\/\?/, '?').replace(/\/$/, '')
  return proxyRequest(event, url)
})
