/* KZZ Football Live service worker — offline shell, fresh data.
   Same-origin GETs: stale-while-revalidate (assets + JSON). Navigation: network-first.
   ESPN API calls go straight to the network (cross-origin, untouched). */
const CACHE = 'kzz-v27';
const STATICS = ['./', './index.html', './app.js?v=27', './styles.css?v=27', './manifest.json',
  './icon-192.png', './icon-512.png', './og-image.png', './analyses.json'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(STATICS)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin || e.request.method !== 'GET') return;
  if (e.request.mode === 'navigate') {
    e.respondWith(
      fetch(e.request).then((r) => {
        if (r.ok) { const c = r.clone(); caches.open(CACHE).then((ch) => ch.put(e.request, c)); }
        return r;
      }).catch(() => caches.match(e.request).then((r) => r || caches.match('./index.html')))
    );
    return;
  }
  e.respondWith(
    caches.match(e.request).then((cached) => {
      const net = fetch(e.request).then((r) => {
        if (r.ok) { const c = r.clone(); caches.open(CACHE).then((ch) => ch.put(e.request, c)); }
        return r;
      }).catch(() => cached);
      return cached || net;
    })
  );
});
