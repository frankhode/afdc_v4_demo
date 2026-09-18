(() => {
  const originalFetch = window.fetch.bind(window);

  window.fetch = async (...args) => {
    const response = await originalFetch(...args);
    const input = args[0];
    const url = input instanceof URL ? input.href : typeof input === 'string' ? input : (input?.url || '');
    if (!/\/data\/catalog\.json(?:[?#]|$)/.test(url)) return response;

    const data = await response.clone().json();
    let included = 0;

    for (const record of data.records || []) {
      for (const image of record.images || []) {
        if (!image?.id) continue;
        image.src = `assets/images/${image.id}.webp`;
        image.thumb = `assets/images/${image.id}.thumb.webp`;
        included += 1;
      }
    }

    if (data.meta) data.meta.imagesIncluded = included;

    const headers = new Headers(response.headers);
    headers.set('content-type', 'application/json; charset=utf-8');

    return new Response(JSON.stringify(data), {
      status: response.status,
      statusText: response.statusText,
      headers
    });
  };
})();
