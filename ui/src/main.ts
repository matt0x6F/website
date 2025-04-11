import './assets/main.css'

import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura';
import primeui from 'tailwindcss-primeui'
import ToastService from 'primevue/toastservice';
import ConfirmationService from 'primevue/confirmationservice';

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import 'primeicons/primeicons.css'

const app = createApp(App)

app.use(createPinia())
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

app.mount('#app')
