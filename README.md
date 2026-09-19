# ASTROшкола — лендінг

Персональна натальна карта дитини у PDF. Статичний сайт, GitHub Pages: https://cvvmaxs-wq.github.io/astroshkola/

- `index.html` — головна (картинки вбудовані base64)
- `oferta.html` — публічна оферта (з `Оферта.docx` замовниці)
- `thank-you.html` — сторінка після оплати (вказати як redirect/approve URL у платіжці)
- `src/template.html` — джерело `index.html`; `python src/build.py` збирає (потрібен Pillow і фото авторки)
- `src/shots.py` — скріншоти по секціях (Playwright + Edge)

## Оплата і заявки
- `PAYMENT_URL` у `<script>` внизу `index.html`/`template.html` — посилання на оплату monobank (790 грн). Порожнє = заглушка після заявки.
- Заявки з форми йдуть на `psy.astro.zhuravel@gmail.com` через formsubmit.co (`FORM_URL`). Перша заявка надсилає лист-активацію — треба натиснути Activate.
