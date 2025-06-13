const CACHE_NAME = 'velora-cache-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/mobile.html',
  '/home.html',
  '/questions.html',
  '/style.css',
  '/assets/icon-192.png',
  '/assets/icon-512.png',
  '/styles.css'
  // tambahkan file lain yang perlu dicache jika ada
];

// Install service worker dan cache aset
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
      .catch(err => {
        console.error('Cache addAll error:', err);
      })
  );
});

// Ambil aset dari cache jika tersedia, fallback ke fetch
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        return response || fetch(event.request);
      })
  );
});
