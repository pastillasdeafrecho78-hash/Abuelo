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
    const prefix = language === 'es' ? '' : languages[language];
    if (prefix === undefined) return null;
    const page = location.pathname.replace(/^\/mirror\/?/, '').replace(/^(en|pt|fr|it|de|nl|ja|zh|ko)\//, '') || 'index.html';
    const url = new URL('/mirror/' + (prefix ? prefix + '/' : '') + page, location.origin);
    url.search = location.search;
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
