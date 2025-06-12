import { Configuration } from '@/lib/api'

type ApiConstructor<T> = new (config: Configuration) => T

/**
 * Creates an API client instance with the current authentication token.
 * 
 * @warning Do not call this function at the top level of a page or component.
 * It should be called close to where the API client is actually used (e.g., within
 * a method or effect) to ensure the auth token is current. Calling it at the top
 * level can lead to token invalidation issues as the function does not handle token
 * refresh automatically.
 * 
 * @example Good usage:
 * ```ts
 * function fetchData() {
 *   const api = useApiClient(MyApi)
 *   return api.getData()
 * }
 * ```
 * 
 * @example Bad usage:
 * ```ts
 * // DON'T do this at the top level
 * const api = useApiClient(MyApi)
 * ```
 */
export function useApiClient<T>(ApiClass: ApiConstructor<T>, cookie?: string): T
export function useApiClient<T extends Record<string, ApiConstructor<any>>>(apiClasses: T, cookie?: string): {
  [K in keyof T]: InstanceType<T[K]>
}
export function useApiClient<T>(input: ApiConstructor<T> | Record<string, ApiConstructor<any>>, cookie?: string) {
  const isServer = typeof window === 'undefined'
  const basePath = isServer
    ? import.meta.env.VITE_API_URL_INTERNAL || import.meta.env.VITE_API_URL
    : import.meta.env.VITE_API_URL

  const config = new Configuration({
    basePath,
    fetchApi: (url, options = {}) => {
      let baseHeaders: Record<string, string> = {};
      if (options.headers && typeof options.headers === 'object' && !Array.isArray(options.headers)) {
        baseHeaders = options.headers as Record<string, string>;
      }
      const headers: Record<string, string> = { ...baseHeaders };
      if (cookie && isServer) {
        headers['cookie'] = cookie;
      }
      return fetch(url, { ...options, headers, credentials: 'include' })
    }
  })

  if (typeof input === 'function') {
    return new input(config)
  }

  const apis = {} as { [K in keyof typeof input]: InstanceType<typeof input[K]> }
  for (const [key, ApiClass] of Object.entries(input)) {
    apis[key as keyof typeof input] = new ApiClass(config)
  }
  return apis
} 