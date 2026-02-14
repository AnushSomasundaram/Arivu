import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

import { setApiBaseUrl } from './lib/api'

const init = async () => {
    if ((window as any).electronAPI) {
        try {
            console.log('Fetching API config from Electron...')
            const config = await (window as any).electronAPI.getApiConfig()
            console.log('API config received:', config)
            if (config && config.baseUrl) {
                setApiBaseUrl(config.baseUrl)
            }
        } catch (e) {
            console.error('Failed to get API config:', e)
        }
    }

    app.mount('#app')
}

init()
