(() => {
  const section = document.querySelector('#gorras');
  if (!section || !section.querySelector('.hat-open-product')) return;

  // Los IDs y las condiciones de preventa vienen de las páginas originales de producto.
  // La segunda foto de cada color está en secondaryImage para poder sustituirla fácilmente.
  const products = {
    green: { handle: 'gorra-verde', title: 'Gorra verde', total: 89900, reservePrice: 20000, balance: 69900, reserveId: '67732726513827', fullId: '67732726546595', secondaryImage: '/mirror/gorra-verde-segunda.png' },
    navy: { handle: 'gorra-azul', title: 'Gorra azul marino', total: 89900, reservePrice: 20000, balance: 69900, reserveId: '67732730347683', fullId: '67732730380451', secondaryImage: '/mirror/gorra-azul-segunda.png' },
    orange: { handle: 'gorra-naranja', title: 'Gorra naranja', total: 79900, reservePrice: 20000, balance: 59900, reserveId: '67732746305699', fullId: '67732746338467', secondaryImage: '/mirror/gorra-naranja-segunda.png' },
    white: { handle: 'gorra-blanca', title: 'Gorra blanca', total: 79900, reservePrice: 20000, balance: 59900, reserveId: '67732763148451', fullId: '67732763181219', secondaryImage: '/mirror/gorra-blanca-segunda.png' },
  };
  const isPreview = location.hostname === '127.0.0.1' || location.hostname === 'localhost' || location.pathname.startsWith('/mirror/');
  const shopRoot = (window.Shopify && window.Shopify.routes && window.Shopify.routes.root) || '/';
  const money = (cents) => '$' + (cents / 100).toLocaleString('es-MX', { maximumFractionDigits: 0 }) + ' MXN';
  const byId = (id) => document.getElementById(id);
  const primaryImage = (key) => section.querySelector('.hat-cap-' + key + ' img').getAttribute('src');
  const catalogByVariant = (id) => {
    for (const [key, product] of Object.entries(products)) {
      if (id === product.reserveId) return { key, product, price: product.reservePrice, payment: 'Apartado de preventa' };
      if (id === product.fullId) return { key, product, price: product.total, payment: 'Pago completo' };
    }
    return null;
  };

  const quick = document.createElement('dialog');
  quick.className = 'hat-quick-view';
  quick.id = 'hat-quick-view';
  quick.setAttribute('aria-labelledby', 'hat-quick-title');
  quick.innerHTML = [
    '<button class="hat-modal-close" type="button" aria-label="Cerrar vista de gorra">×</button>',
    '<div class="hat-quick-grid">',
    '<div class="hat-quick-gallery">',
    '<div class="hat-quick-slide" id="hat-quick-slide" aria-live="polite"></div>',
    '<div class="hat-quick-controls">',
    '<button type="button" class="hat-slide-arrow" id="hat-slide-prev" aria-label="Imagen anterior">‹</button>',
    '<span id="hat-slide-count">1 / 2</span>',
    '<button type="button" class="hat-slide-arrow" id="hat-slide-next" aria-label="Imagen siguiente">›</button>',
    '</div><div class="hat-slide-dots" id="hat-slide-dots"></div>',
    '</div>',
    '<div class="hat-quick-info">',
    '<p class="hat-quick-eyebrow">EL ABUELO PREFERIDO · PREVENTA</p>',
    '<h2 id="hat-quick-title"></h2>',
    '<p class="hat-quick-total" id="hat-quick-total"></p>',
    '<p class="hat-quick-note">Entrega en 45 días · Envíos a todo México</p>',
    '<form id="hat-quick-form">',
    '<label for="hat-quick-variant">FORMA DE PAGO</label>',
    '<select id="hat-quick-variant" name="id" required></select>',
    '<p class="hat-quick-payment" id="hat-quick-payment"></p>',
    '<label for="hat-quick-quantity">CANTIDAD</label>',
    '<input id="hat-quick-quantity" name="quantity" type="number" min="1" max="99" value="1" required>',
    '<button type="submit" class="hat-add-button">AGREGAR AL CARRITO</button>',
    '<p class="hat-quick-error" id="hat-quick-error" role="alert" hidden></p>',
    '</form>',
    '<p class="hat-quick-shipping">ENVÍO A TODA LA REPÚBLICA MEXICANA<br>GRATIS EN COMPRAS DE GORRAS DESDE $1,400 MXN</p>',
    '</div></div>'
  ].join('');
  document.body.append(quick);

  const drawer = document.createElement('div');
  drawer.className = 'hat-drawer';
  drawer.id = 'hat-cart-drawer';
  drawer.hidden = true;
  drawer.innerHTML = [
    '<button type="button" class="hat-drawer-backdrop" aria-label="Cerrar mini carrito"></button>',
    '<aside class="hat-drawer-panel" role="dialog" aria-modal="true" aria-labelledby="hat-drawer-title">',
    '<div class="hat-drawer-head"><div><span>EL ABUELO PREFERIDO</span><h2 id="hat-drawer-title">TU CARRITO</h2></div>',
    '<button type="button" class="hat-drawer-close" aria-label="Cerrar mini carrito">×</button></div>',
    '<div class="hat-drawer-items" id="hat-drawer-items"></div>',
    '<div class="hat-drawer-bottom"><p class="hat-drawer-total"><span>SUBTOTAL</span><strong id="hat-drawer-total"></strong></p>',
    '<p class="hat-drawer-note">Los apartados son de preventa. El saldo se paga antes de enviar y la entrega es en 45 días.</p>',
    '<button type="button" class="hat-keep-shopping">SEGUIR COMPRANDO</button>',
    '<a class="hat-cart-link" id="hat-cart-link" href="https://elabuelopreferido.com/cart">VER CARRITO</a>',
    '</div></aside>'
  ].join('');
  document.body.append(drawer);

  let activeKey = null;
  let activeSlide = 0;
  let returnFocus = null;
  let returnFocusByKeyboard = false;
  let startX = 0;
  const slide = byId('hat-quick-slide');
  const variant = byId('hat-quick-variant');
  const addButton = quick.querySelector('.hat-add-button');

  function showSlide(index) {
    if (!activeKey) return;
    activeSlide = (index + 2) % 2;
    const product = products[activeKey];
    const src = activeSlide === 0 ? primaryImage(activeKey) : product.secondaryImage;
    slide.replaceChildren();
    if (src) {
      const image = document.createElement('img');
      image.src = src;
      image.alt = product.title + (activeSlide === 0 ? ', vista principal' : ', segunda vista');
      slide.append(image);
    } else {
      const placeholder = document.createElement('div');
      placeholder.className = 'hat-next-photo';
      placeholder.innerHTML = '<span>02</span><strong>SEGUNDA IMAGEN</strong><small>Espacio listo para la próxima foto de esta gorra</small>';
      slide.append(placeholder);
    }
    byId('hat-slide-count').textContent = (activeSlide + 1) + ' / 2';
    const dots = byId('hat-slide-dots');
    dots.replaceChildren();
    for (let i = 0; i < 2; i++) {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'hat-slide-dot' + (i === activeSlide ? ' is-active' : '');
      dot.setAttribute('aria-label', 'Ver imagen ' + (i + 1));
      dot.setAttribute('aria-current', String(i === activeSlide));
      dot.addEventListener('click', () => showSlide(i));
      dots.append(dot);
    }
  }

  function updatePayment() {
    const product = products[activeKey];
    byId('hat-quick-payment').textContent = variant.value === product.reserveId
      ? 'PAGAS ' + money(product.reservePrice) + ' HOY · SALDO ' + money(product.balance) + ' ANTES DE ENVIAR'
      : 'PAGAS EL PRECIO TOTAL ' + money(product.total) + ' HOY';
  }

  function renderProduct(key) {
    const product = products[key];
    byId('hat-quick-title').textContent = product.title;
    byId('hat-quick-total').textContent = 'PRECIO TOTAL ' + money(product.total);
    const reserve = new Option('APARTA CON ' + money(product.reservePrice), product.reserveId);
    const full = new Option('PAGA COMPLETA ' + money(product.total), product.fullId);
    reserve.disabled = product.reserveAvailable === false;
    full.disabled = product.fullAvailable === false;
    variant.replaceChildren(reserve, full);
    variant.value = reserve.disabled ? product.fullId : product.reserveId;
    updatePayment();
    addButton.disabled = reserve.disabled && full.disabled;
    addButton.textContent = addButton.disabled ? 'AGOTADA' : 'AGREGAR AL CARRITO';
  }

  async function syncLiveProduct(key) {
    const product = products[key];
    if (isPreview || product.liveSynced) return;
    const response = await fetch(shopRoot + 'products/' + product.handle + '.js', { headers: { Accept: 'application/json' } });
    if (!response.ok) throw new Error('No se pudo verificar la disponibilidad actual de esta gorra. Inténtalo de nuevo.');
    const live = await response.json();
    const reserve = live.variants.find((item) => /APARTA/i.test(item.title));
    const full = live.variants.find((item) => /PAGA COMPLETA/i.test(item.title));
    if (!reserve || !full) throw new Error('Las opciones de preventa cambiaron. Recarga la página para continuar.');
    product.title = live.title;
    product.reserveId = String(reserve.id);
    product.fullId = String(full.id);
    product.reservePrice = Number(reserve.price);
    product.total = Number(full.price);
    product.balance = product.total - product.reservePrice;
    product.reserveAvailable = reserve.available;
    product.fullAvailable = full.available;
    product.liveSynced = true;
  }

  async function openQuick(key, trigger, byKeyboard) {
    activeKey = key;
    returnFocus = trigger;
    returnFocusByKeyboard = byKeyboard;
    byId('hat-quick-quantity').value = '1';
    byId('hat-quick-error').hidden = true;
    renderProduct(key);
    showSlide(0);
    quick.showModal();
    document.body.classList.add('hat-overlay-open');
    if (isPreview) return;
    addButton.disabled = true;
    addButton.textContent = 'VERIFICANDO…';
    try {
      await syncLiveProduct(key);
      if (activeKey === key && quick.open) renderProduct(key);
    } catch (error) {
      if (activeKey !== key || !quick.open) return;
      const message = byId('hat-quick-error');
      message.textContent = error.message;
      message.hidden = false;
      addButton.disabled = true;
      addButton.textContent = 'NO DISPONIBLE';
    }
  }

  function closeQuick() {
    quick.close();
  }

  section.querySelectorAll('.hat-open-product').forEach((button) => {
    button.addEventListener('click', (event) => openQuick(button.dataset.hatColor, button, event.detail === 0));
  });
  quick.querySelector('.hat-modal-close').addEventListener('click', closeQuick);
  quick.addEventListener('click', (event) => { if (event.target === quick) closeQuick(); });
  function restoreProductFocus() {
    if (!returnFocus || !returnFocus.isConnected) return;
    if (returnFocusByKeyboard) returnFocus.focus({ preventScroll: true });
    else requestAnimationFrame(() => returnFocus.blur());
  }
  quick.addEventListener('close', () => {
    if (!drawer.hidden) return;
    document.body.classList.remove('hat-overlay-open');
    restoreProductFocus();
  });
  byId('hat-slide-prev').addEventListener('click', () => showSlide(activeSlide - 1));
  byId('hat-slide-next').addEventListener('click', () => showSlide(activeSlide + 1));
  quick.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') showSlide(activeSlide - 1);
    if (event.key === 'ArrowRight') showSlide(activeSlide + 1);
  });
  slide.addEventListener('touchstart', (event) => { startX = event.changedTouches[0].screenX; }, { passive: true });
  slide.addEventListener('touchend', (event) => {
    const distance = event.changedTouches[0].screenX - startX;
    if (Math.abs(distance) > 50) showSlide(activeSlide + (distance < 0 ? 1 : -1));
  }, { passive: true });
  variant.addEventListener('change', updatePayment);

  function readPreviewCart() {
    try {
      const parsed = JSON.parse(localStorage.getItem('abuelo-quick-cart-v1') || '[]');
      return Array.isArray(parsed) ? parsed.filter((item) => catalogByVariant(String(item.id)) && Number.isInteger(item.quantity) && item.quantity > 0) : [];
    } catch { return []; }
  }
  function savePreviewCart(items) {
    localStorage.setItem('abuelo-quick-cart-v1', JSON.stringify(items));
  }
  async function addToCart(id, quantity) {
    if (isPreview) {
      const items = readPreviewCart();
      const existing = items.find((item) => item.id === id);
      if (existing) existing.quantity += quantity;
      else items.push({ id, quantity });
      savePreviewCart(items);
      return items;
    }
    const form = new FormData();
    form.append('form_type', 'product');
    form.append('id', id);
    form.append('quantity', String(quantity));
    const response = await fetch(shopRoot + 'cart/add.js', { method: 'POST', headers: { Accept: 'application/json' }, body: form });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.description || 'No se pudo agregar esta gorra al carrito.');
    }
    const cart = await fetch(shopRoot + 'cart.js', { headers: { Accept: 'application/json' } });
    if (!cart.ok) throw new Error('La gorra se agregó, pero no se pudo cargar el carrito.');
    return (await cart.json()).items;
  }

  function normalizeCart(items) {
    if (isPreview) return items.map((item) => {
      const data = catalogByVariant(String(item.id));
      return { id: String(item.id), quantity: item.quantity, title: data.product.title, payment: data.payment, price: data.price, image: primaryImage(data.key) };
    });
    return items.map((item) => ({
      id: String(item.variant_id || item.id),
      quantity: item.quantity,
      title: item.product_title || item.title,
      payment: item.variant_title || '',
      price: item.final_price == null ? item.price : item.final_price,
      image: item.image || (item.featured_image && item.featured_image.url) || '',
    }));
  }

  function updateCartBadge(count) {
    const bag = document.querySelector('.gold-bag');
    if (!bag) return;
    let badge = bag.querySelector('.cart-nav-count');
    if (!badge) {
      badge = document.createElement('span');
      badge.className = 'cart-nav-count';
      bag.append(badge);
    }
    badge.textContent = String(count);
  }

  function cartDestination(items) {
    if (!isPreview) return shopRoot + 'cart';
    if (!items.length) return 'https://elabuelopreferido.com/cart';
    const variants = items.map((item) => String(item.id) + ':' + item.quantity).join(',');
    return 'https://elabuelopreferido.com/cart/' + variants + '?storefront=true';
  }

  function renderDrawer(rawItems) {
    const items = normalizeCart(rawItems);
    const container = byId('hat-drawer-items');
    container.replaceChildren();
    if (!items.length) {
      const empty = document.createElement('p');
      empty.textContent = 'TU CARRITO ESTÁ VACÍO. ELIGE UNA GORRA PARA EMPEZAR.';
      container.append(empty);
    }
    for (const item of items) {
      const row = document.createElement('div');
      row.className = 'hat-drawer-item';
      const image = document.createElement('img');
      image.src = item.image;
      image.alt = item.title;
      const copy = document.createElement('div');
      const title = document.createElement('strong');
      title.textContent = item.title;
      const payment = document.createElement('span');
      payment.textContent = item.payment;
      const quantity = document.createElement('small');
      quantity.textContent = 'CANTIDAD ' + item.quantity;
      const price = document.createElement('b');
      price.textContent = money(item.price * item.quantity);
      copy.append(title, payment, quantity, price);
      row.append(image, copy);
      container.append(row);
    }
    byId('hat-drawer-total').textContent = money(items.reduce((sum, item) => sum + item.price * item.quantity, 0));
    drawer.querySelector('.hat-drawer-note').textContent = items.some((item) => catalogByVariant(item.id)?.payment === 'Apartado de preventa')
      ? 'Los apartados son de preventa. El saldo se paga antes de enviar y la entrega es en 45 días.'
      : 'Estos productos están en preventa. La entrega es en 45 días.';
    updateCartBadge(items.reduce((sum, item) => sum + item.quantity, 0));
    const destination = cartDestination(items);
    byId('hat-cart-link').href = destination;
    document.querySelectorAll('.cart-nav-link').forEach((link) => { link.href = destination; });
  }

  function openDrawer(items) {
    renderDrawer(items);
    drawer.hidden = false;
    document.body.classList.add('hat-overlay-open');
    drawer.querySelector('.hat-drawer-close').focus();
  }
  function closeDrawer() {
    drawer.hidden = true;
    document.body.classList.remove('hat-overlay-open');
    restoreProductFocus();
  }
  drawer.querySelector('.hat-drawer-close').addEventListener('click', closeDrawer);
  drawer.querySelector('.hat-drawer-backdrop').addEventListener('click', closeDrawer);
  drawer.querySelector('.hat-keep-shopping').addEventListener('click', closeDrawer);
  drawer.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeDrawer();
    if (event.key !== 'Tab') return;
    const controls = [...drawer.querySelectorAll('.hat-drawer-panel button,.hat-drawer-panel a,.hat-drawer-panel input')].filter((control) => !control.disabled && control.getClientRects().length);
    const first = controls[0];
    const last = controls[controls.length - 1];
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  byId('hat-quick-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!activeKey || !event.currentTarget.reportValidity()) return;
    const id = variant.value;
    const quantity = Number(byId('hat-quick-quantity').value);
    if (!catalogByVariant(id) || !Number.isInteger(quantity) || quantity < 1 || quantity > 99) return;
    addButton.disabled = true;
    addButton.textContent = 'AGREGANDO…';
    try {
      const items = await addToCart(id, quantity);
      quick.close();
      openDrawer(items);
    } catch (error) {
      const message = byId('hat-quick-error');
      message.textContent = error.message || 'No se pudo agregar esta gorra al carrito.';
      message.hidden = false;
    } finally {
      addButton.disabled = false;
      addButton.textContent = 'AGREGAR AL CARRITO';
    }
  });
  if (isPreview) {
    const stored = readPreviewCart();
    updateCartBadge(stored.reduce((sum, item) => sum + item.quantity, 0));
    document.querySelectorAll('.cart-nav-link').forEach((link) => { link.href = cartDestination(stored); });
  }
})();
