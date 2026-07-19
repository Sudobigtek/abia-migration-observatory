const CACHE_NAME = 'abia-obs-v1';
const urlsToCache = [
    '/pwa/dashboard/',
    '/pwa/manifest.json',
    '/static/icon-192.png'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            if (response) return response;
            return fetch(event.request).catch(() => {
                if (event.request.mode === 'navigate') {
                    return caches.match('/pwa/dashboard/');
                }
            });
        })
    );
});