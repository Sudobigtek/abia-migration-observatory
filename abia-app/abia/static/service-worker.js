const CACHE_NAME = 'abia-observatory-v1';
const STATIC_ASSETS = [
  '/public-dashboard/',
  '/public-dashboard/data-collection/',
  '/static/manifest.json',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js'
];

// Install: Cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    }).catch(() => console.log('Static cache skipped for some assets'))
  );
  self.skipWaiting();
});

// Activate: Clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)));
    })
  );
  self.clients.claim();
});

// Fetch: Cache-first for static, network-first for API
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  if (request.method === 'GET') {
    event.respondWith(
      caches.match(request).then((cached) => {
        return cached || fetch(request).then((response) => {
          return caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, response.clone());
            return response;
          });
        }).catch(() => {
          if (request.mode === 'navigate') {
            return caches.match('/public-dashboard/');
          }
        });
      })
    );
  }
});

// Background sync for queued form submissions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-forms') {
    event.waitUntil(syncQueuedForms());
  }
});

async function syncQueuedForms() {
  const db = await openIndexedDB();
  const tx = db.transaction('formQueue', 'readonly');
  const store = tx.objectStore('formQueue');
  const allForms = await store.getAll();
  
  for (const form of allForms) {
    try {
      const response = await fetch(form.url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: form.body
      });
      if (response.ok) {
        const delTx = db.transaction('formQueue', 'readwrite');
        await delTx.objectStore('formQueue').delete(form.id);
      }
    } catch (e) {
      console.log('Sync failed for form', form.id, 'will retry');
    }
  }
}

function openIndexedDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('AbiaObservatoryDB', 1);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('formQueue')) {
        db.createObjectStore('formQueue', { keyPath: 'id', autoIncrement: true });
      }
    };
    request.onsuccess = (event) => resolve(event.target.result);
    request.onerror = (event) => reject(event.target.error);
  });
}
