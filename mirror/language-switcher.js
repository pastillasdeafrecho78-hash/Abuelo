(() => {
  const languages = {
    en: 'en',
    'pt-BR': 'pt',
    fr: 'fr',
    it: 'it',
    de: 'de',
    nl: 'nl',
    ja: 'ja',
    'zh-CN': 'zh',
    ko: 'ko',
  };
  const selectors = [...document.querySelectorAll('.lang-select[name="language_code"]')];
  if (!selectors.length) return;

  function destination(language) {
    if (language === 'es') return location.href;
    const prefix = languages[language];
    if (!prefix) return null;

    const page = location.pathname.replace(/^\/mirror\/?/, '').replace(/\.html$/, '');
    const path = page && page !== 'index' ? '/' + page : '';
    const url = new URL('https://elabuelopreferido.com/' + prefix + path);
    url.hash = location.hash;
    return url.href;
  }

  for (const select of selectors) {
    select.addEventListener('change', () => {
      const url = destination(select.value);
      if (url && url !== location.href) location.assign(url);
    });
    select.form?.addEventListener('submit', (event) => {
      event.preventDefault();
      const url = destination(select.value);
      if (url && url !== location.href) location.assign(url);
    });
  }
})();
