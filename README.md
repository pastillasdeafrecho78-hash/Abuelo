# El Abuelo Preferido · copia local del sitio

Para ver la propuesta localmente:

```bash
cd /home/SalvadorTD/Desktop/el-abuelo-preferido-propuesta
python -m http.server 8765
```

Abre `http://localhost:8765/` o `http://localhost:8765/mirror/` para ver la copia fiel. El rediseño anterior, separado de esta copia, está en `propuesta/`.

## Captura

- Se descargaron 15 páginas HTML públicas: portada, carrito, experiencias, Tapalpa, marcas, contacto, términos, privacidad, colección de gorras y las seis fichas de producto.
- Se descargaron 63 recursos: imágenes, logotipos, tipografías, CSS y JavaScript.
- `original/products.json` conserva los seis productos publicados y sus variantes y precios.
- El servidor devolvió HTTP 429 en algunos intentos. Se obtuvo el HTML real de todas las páginas anteriores mediante la variante pública `?view=default` y reintentos.
- `mirror/` conserva los scripts propios de interacción del sitio y omite los de pago, analítica y captcha de Shopify, que no pueden ejecutarse desde localhost. Los archivos originales descargados siguen en `original/`.
- En la portada, cada gorra abre su galería. Al agregarla aparece el mini carrito; «Ver carrito» amplía ese mismo panel con el pedido, los datos de entrega y las condiciones, sin salir de la página.
- La copia guarda el carrito de prueba en este navegador. «Continuar al pago» prepara un enlace a Shopify con las variantes, cantidades y datos de entrega; el cobro real depende de la tienda y no se procesa en esta copia estática.

`capture_assets.py` y `build_mirror.py` documentan cómo se armó la referencia local.
