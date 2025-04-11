import { Configuration } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

type ApiConstructor<T> = new (config: Configuration) => T

export function useApiClient<T>(ApiClass: ApiConstructor<T>): T
export function useApiClient<T extends Record<string, ApiConstructor<any>>>(apiClasses: T): {
  [K in keyof T]: InstanceType<T[K]>
}
export function useApiClient<T>(input: ApiConstructor<T> | Record<string, ApiConstructor<any>>) {
  const auth = useAuthStore()
  
  const config = new Configuration({
    basePath: import.meta.env.VITE_API_URL,
    headers: auth.storedAccessToken ? {
      'Authorization': `Bearer ${auth.storedAccessToken}`
    } : undefined
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