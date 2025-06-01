import { Configuration } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

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
export function useApiClient<T>(ApiClass: ApiConstructor<T>): T
export function useApiClient<T extends Record<string, ApiConstructor<any>>>(apiClasses: T): {
  [K in keyof T]: InstanceType<T[K]>
}
export function useApiClient<T>(input: ApiConstructor<T> | Record<string, ApiConstructor<any>>) {
  const auth = useAuthStore()
  const isServer = typeof window === 'undefined'
  const basePath = isServer
    ? import.meta.env.VITE_API_URL_INTERNAL || import.meta.env.VITE_API_URL
    : import.meta.env.VITE_API_URL

  const config = new Configuration({
    basePath,
    accessToken: () => auth.storedAccessToken
  })
  console.log('useApiClient: token at instantiation:', auth.storedAccessToken)
  console.log('useApiClient: basePath at instantiation:', basePath)

  if (typeof input === 'function') {
    return new input(config)
  }

  const apis = {} as { [K in keyof typeof input]: InstanceType<typeof input[K]> }
  for (const [key, ApiClass] of Object.entries(input)) {
    apis[key as keyof typeof input] = new ApiClass(config)
  }
  return apis
} 