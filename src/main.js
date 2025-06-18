import { createApp } from 'vue'
import App from './app.vue'
import router from './router'
import './styles.css' // atau tailwind.css kamu
import { loginGoogle } from './api.js';

createApp(App).use(router).mount('#app')

document.querySelector('#loginBtn').addEventListener('click', async () => {
  const result = await loginGoogle({
    google_id: 'XYZ',
    name: 'John Doe',
    email: 'john@example.com',
    picture_url: 'https://...'
  });

  if (result.status === 'success') {
    localStorage.setItem('userId', result.data.userId);
    window.location.href = 'profile.html';
  } else {
    alert('Login gagal!');
  }
});
