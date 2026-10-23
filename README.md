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
- El carrito vacío se ve como en el sitio, pero el checkout, las cuentas y el envío real de formularios dependen de Shopify y no funcionan en esta copia estática.

`capture_assets.py` y `build_mirror.py` documentan cómo se armó la referencia local.
