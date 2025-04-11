/* eslint-disable @typescript-eslint/no-explicit-any */
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  // Explicitly declare the component type with proper typing
  const component: DefineComponent<
    Record<string, unknown>, // props
    Record<string, unknown>, // public props
    any // setup/data/methods/computed etc
  >
  export default component
}

// Add support for Vite's static asset handling
declare module '*.svg' {
  const content: string
  export default content
}

declare module '*.png' {
  const content: string
  export default content
}

declare module '*.jpg' {
  const content: string
  export default content
} 