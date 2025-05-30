import './assets/main.css'

import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura';
import primeui from 'tailwindcss-primeui'
import ToastService from 'primevue/toastservice';
import ConfirmationService from 'primevue/confirmationservice';
import Tooltip from 'primevue/tooltip';

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import 'primeicons/primeicons.css'
import { createHead } from '@vueuse/head';

// Inject Umami analytics script only in production and if the website ID is set
if (import.meta.env.PROD && import.meta.env.VITE_UMAMI_WEBSITE_ID) {
  const script = document.createElement('script');
  script.defer = true;
  script.src = 'https://cloud.umami.is/script.js';
  script.setAttribute('data-website-id', import.meta.env.VITE_UMAMI_WEBSITE_ID);
  document.head.appendChild(script);
}

const app = createApp(App)

app.use(createPinia())
const head = createHead()
app.use(head)
app.use(router)
app.use(PrimeVue, {
    theme: {
        extend: {
            options: {
              cssLayer: {
                name: 'primevue', //any name you want. will be referenced on app.css
                order: 'tailwind-base, primeui, tailwind-utilities'
              }
            },
        },
        preset: Aura
    },
    ripple: true,
    plugins: [primeui]
})
app.use(ToastService)
app.use(ConfirmationService)
app.directive('tooltip', Tooltip)

router.afterEach((to) => {
  let title = typeof to.meta.title === 'function'
    ? to.meta.title(to)
    : to.meta.title
  if (!title) {
    title = 'ooo-yay.com'
  }
  document.title = title
})

app.mount('#app')
