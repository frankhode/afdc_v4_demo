(() => {
  const originalFetch = window.fetch.bind(window);
  const imagePaths = {
    FO069829_001: 'assets/images/FO069829_001.jpg',
    FO069829_007: 'assets/images/FO069829_007.jpg',
    FO069829_008: 'assets/images/FO069829_008.jpg',
    FO077301_000: 'assets/images/FO077301_000.jpg',
    FO051084_000: 'assets/images/FO051084_000.jpg',
    FO063983_000: 'assets/images/FO063983_000.jpg'
  };

  window.fetch = async (...args) => {
    const response = await originalFetch(...args);
    const input = args[0];
    const url = input instanceof URL ? input.href : typeof input === 'string' ? input : (input?.url || '');
    if (!/\/data\/catalog\.json(?:[?#]|$)/.test(url)) return response;

    const data = await response.clone().json();
    let included = 0;
    for (const record of data.records || []) {
      for (const image of record.images || []) {
        const src = imagePaths[image.id];
        if (!src) continue;
        image.src = src;
        image.thumb = src;
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
