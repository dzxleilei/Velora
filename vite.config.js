// vite.config.js
export default {
  root: '.', // folder html kamu
  server: {
    port: 8080, // pakai port yang kamu inginkan
    proxy: {
      '/api': 'http://localhost:5000' // untuk API ke backend Flask
    }
  }
}
