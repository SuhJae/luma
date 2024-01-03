const CACHE_NAME = "image-cache";
const urlsToCache = [
    '/api/v1/media/', // Replace with your actual URLs to cache
];

// Install event
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
            .catch(error => console.error('Error adding to cache', error))
    );
});

// Fetch event
self.addEventListener('fetch', event => {
    // Skip cache for non-HTTP/HTTPS requests
    if (!event.request.url.startsWith('http')) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(cachedResponse => {
                // Return cached response if available
                if (cachedResponse) {
                    return cachedResponse;
                }
                return fetch(event.request).then(response => {
                    // Don't cache if response is not OK or if it's a partial response
                    if (!response || response.status !== 200 || response.type !== 'basic' || response.status === 206) {
                        return response;
                    }

                    // Clone the response to cache it
                    const responseToCache = response.clone();

                    // Open cache and put the new response in
                    caches.open(CACHE_NAME)
                        .then(cache => {
                            cache.put(event.request, responseToCache);
                        });

                    return response;
                });
            })
    );
});

