import { createApp } from 'vue'
import App from './app.vue'
import router from './router'
import './styles.css' // atau tailwind.css kamu

createApp(App).use(router).mount('#app')
