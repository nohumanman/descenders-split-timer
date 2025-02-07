/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Plugins
import { registerPlugins } from '@/plugins'

// Components
import App from './App.vue'

// Composables
import { createApp } from 'vue'

import router from './router';
import socket from './socket';

const app = createApp(App)
    .use(router)
    .use({
        install(app) {
            app.config.globalProperties.$socket = socket;
        }
    })

registerPlugins(app)

app.mount('#app')
