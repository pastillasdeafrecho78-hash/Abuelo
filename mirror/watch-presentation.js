(() => {
  const carousel = document.querySelector('#relojes .watch-carousel');
  if (!carousel) return;

  const track = carousel.querySelector('.photo-track');
  const slides = [...track.querySelectorAll('.photo-slide')];
  const previous = carousel.querySelector('.watch-prev');
  const next = carousel.querySelector('.watch-next');
  const toggle = carousel.querySelector('.watch-toggle');
  if (slides.length < 2 || !previous || !next || !toggle) return;
  const locale = document.documentElement.lang.split('-')[0];
  const controls = {
    es: ['PAUSAR', 'REPRODUCIR'], en: ['PAUSE', 'PLAY'], pt: ['PAUSAR', 'REPRODUZIR'],
    fr: ['PAUSE', 'REPRENDRE'], it: ['PAUSA', 'RIPRODUCI'], de: ['PAUSE', 'ABSPIELEN'],
    nl: ['PAUZEREN', 'AFSPELEN'], ja: ['一時停止', '再生'], zh: ['暂停', '播放'], ko: ['일시정지', '재생'],
  }[locale] || ['PAUSAR', 'REPRODUCIR'];
  const t = window.HAT_T || ((key) => key);
  previous.setAttribute('aria-label', t('previous'));
  next.setAttribute('aria-label', t('next'));
  toggle.textContent = controls[0];
  toggle.setAttribute('aria-label', controls[0]);

  const desktop = matchMedia('(min-width: 851px)');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let inView = false;
  let pointerOver = false;
  let manuallyPaused = false;
  let timer;

  function currentIndex() {
    return slides.reduce((nearest, slide, index) =>
      Math.abs(slide.offsetLeft - slides[0].offsetLeft - track.scrollLeft) < Math.abs(slides[nearest].offsetLeft - slides[0].offsetLeft - track.scrollLeft)
        ? index : nearest, 0);
  }

  function show(index) {
    const target = slides[(index + slides.length) % slides.length];
    track.scrollTo({
      left: target.offsetLeft - slides[0].offsetLeft,
      behavior: reducedMotion.matches ? 'instant' : 'smooth',
    });
  }

  function canPlay() {
    return desktop.matches && !reducedMotion.matches && !manuallyPaused && inView &&
      !pointerOver && document.visibilityState === 'visible' && document.activeElement !== track;
  }

  function schedule(delay = 5000) {
    clearTimeout(timer);
    if (!canPlay()) return;
    timer = setTimeout(() => {
      show(currentIndex() + 1);
      schedule();
    }, delay);
  }

  function move(step) {
    show(currentIndex() + step);
    schedule(8000);
  }

  previous.addEventListener('click', () => move(-1));
  next.addEventListener('click', () => move(1));
  toggle.addEventListener('click', () => {
    manuallyPaused = !manuallyPaused;
    toggle.textContent = controls[manuallyPaused ? 1 : 0];
    toggle.setAttribute('aria-label', toggle.textContent);
    schedule();
  });

  carousel.addEventListener('pointerenter', () => { pointerOver = true; schedule(); });
  carousel.addEventListener('pointerleave', () => { pointerOver = false; schedule(); });
  track.addEventListener('focus', () => schedule());
  track.addEventListener('blur', () => schedule());
  document.addEventListener('visibilitychange', () => schedule());
  desktop.addEventListener('change', () => schedule());
  reducedMotion.addEventListener('change', () => schedule());

  new IntersectionObserver(([entry]) => {
    inView = entry.isIntersecting;
    schedule();
  }, { threshold: 0.35 }).observe(carousel);
})();
