(() => {
  const section = document.querySelector('#gorras');
  if (!section) return;

  const wrap = section.querySelector('.wrap');
  const colors = [...wrap.querySelectorAll(':scope > .hat-color')];
  if (colors.length !== 4) return;

  const eyebrow = wrap.querySelector(':scope > .eyebrow');
  const originalHeading = wrap.querySelector(':scope > h2');
  const originalIntro = originalHeading?.nextElementSibling;
  const lettering = wrap.querySelector(':scope > .hat-quote');
  if (!originalHeading || !originalIntro) return;
  const locale = document.documentElement.lang.split('-')[0];
  const translatedTagline = originalHeading.innerText.replace(/\s+/g, ' ').trim();
  const translatedTitle = document.querySelector('header a[href$="#gorras"]')?.textContent.trim();

  eyebrow.hidden = true;
  lettering.hidden = true;

  const heading = document.createElement('div');
  heading.className = 'hat-feature-heading';
  originalHeading.before(heading);
  originalHeading.textContent = locale === 'es' ? 'EL ESTILO SE LLEVA, LA ACTITUD TAMBIÉN' : translatedTagline;
  originalHeading.className = 'hat-feature-tagline';
  heading.append(originalHeading);

  const title = document.createElement('h2');
  title.className = 'hat-feature-title';
  title.textContent = locale === 'es' ? 'GORRAS' : (translatedTitle || 'CAPS');
  heading.append(title);
  originalIntro.classList.add('hat-feature-intro');
  heading.append(originalIntro);

  const pairs = document.createElement('div');
  pairs.className = 'hat-pairs';
  heading.after(pairs);

  const groups = [
    { name: 'Póngase a jalar', colors: [colors[0], colors[1]], keys: ['green', 'navy'], photoIndexes: [0, 0] },
    { name: 'No es mi pedo haber nacido rico', colors: [colors[2], colors[3]], keys: ['orange', 'white'], photoIndexes: [0, 1] },
  ];

  for (const group of groups) {
    const pair = document.createElement('div');
    pair.className = 'hat-pair';
    const name = document.createElement('h3');
    name.className = 'hat-pair-name';
    if (group.keys[0] === 'orange') {
      const lines = document.createElement('span');
      lines.append('No es mi pedo ', document.createElement('br'), 'haber nacido rico');
      name.append(lines);
    } else {
      name.textContent = group.name;
    }
    const stage = document.createElement('div');
    stage.className = 'hat-stage';
    stage.setAttribute('aria-label', group.name);
    const price = document.createElement('p');
    price.className = 'hat-pair-price';
    price.textContent = group.colors[0].querySelector('.hat-price strong').textContent.trim();
    const caption = document.createElement('p');
    caption.className = 'hat-pair-caption';
    caption.textContent = group.name;
    const productGrid = document.createElement('div');
    productGrid.className = 'hat-pair-products';
    productGrid.hidden = true;
    pair.append(name, stage, price, caption, productGrid);

    group.colors.forEach((color, index) => {
      const gallery = color.querySelector('.hat-gallery');
      const photo = gallery.children[group.photoIndexes[index]];
      photo.classList.add('hat-feature-cap', `hat-cap-${group.keys[index]}`);
      const openButton = photo.querySelector('.hat-zoom');
      openButton.classList.replace('hat-zoom', 'hat-open-product');
      if (locale === 'es') openButton.setAttribute('aria-label', `Ver gorra ${color.querySelector('.hat-color-heading h3').textContent.toLowerCase()} y opciones de compra`);
      openButton.dataset.hatColor = group.keys[index];
      stage.append(photo);
      productGrid.append(color);
    });

    pairs.append(pair);
  }
})();
