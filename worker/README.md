# astroshkola-pay — Cloudflare Worker для оплати через monobank

Сайт (GitHub Pages) не може зберігати токен mono, тому рахунок створює цей воркер.

## Деплой (один раз)
```
cd worker
npx wrangler login                 # вхід у Cloudflare через браузер
npx wrangler deploy                # видасть URL виду https://astroshkola-pay.<акаунт>.workers.dev
npx wrangler secret put MONO_TOKEN # вставити токен з кабінету mono
```
Потім вписати URL воркера в `PAY_API` у `index.html` / `src/template.html`.

## Перевірка
```
curl -X POST https://astroshkola-pay.<акаунт>.workers.dev/invoice -H "Content-Type: application/json" \
  -d '{"parent":"Тест","email":"test@example.com","child":"Тест","date":"2015-01-01","time":"10:00","place":"Київ"}'
```
Відповідь: `{"pageUrl":"https://pay.mbnk.biz/...","invoiceId":"..."}`. Рахунок можна не оплачувати — він зникне через 3 дні.
