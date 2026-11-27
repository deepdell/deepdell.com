import { test, expect } from '@playwright/test';

const BASE = 'https://deepdell.com';
const PAGES = [
  '/',
  '/services.html',
  '/shopify-plus.html',
  '/ai.html',
  '/data.html',
  '/automation.html',
  '/support.html',
  '/pricing.html',
  '/industries.html',
  '/contact.html',
  '/agentic-check.html',
  '/contact-card.html',
  '/game.html',
  '/commerce-calculator.html',
  '/privacy.html'
];

test('unknown URLs return the branded 404 page', async ({ page }) => {
  const response = await page.goto(BASE + '/this-page-does-not-exist', { waitUntil: 'domcontentloaded', timeout: 30000 });
  expect(response?.status()).toBe(404);
  await expect(page).toHaveTitle(/Page not found/);
});

test.describe.configure({ mode: 'serial' });

test('production pages load without browser errors', async ({ page }) => {
  const failures = [];
  page.on('pageerror', err => failures.push(err.message));
  for (const path of PAGES) {
    const response = await page.goto(BASE + path, { waitUntil: 'domcontentloaded', timeout: 30000 });
    expect(response?.status(), path).toBe(200);
    expect(await page.title(), path).toMatch(/.+/);
  }
  expect(failures, 'browser page errors').toEqual([]);
});

test('GA4 loads only after consent on the production homepage', async ({ page }) => {
  await page.goto(BASE + '/', { waitUntil: 'networkidle', timeout: 30000 });
  await expect(page.locator('#deepdell-consent')).toBeVisible();

  const before = await page.evaluate(() => ({
    tag: document.querySelector('script[src*="googletagmanager.com/gtag/js?id=G-K592HB9G99"]') !== null,
    gtag: typeof window.gtag === 'function',
    defaultDenied: Array.isArray(window.dataLayer) && window.dataLayer.some(
      item => item && item[0] === 'consent' && item[1] === 'default' &&
        item[2]?.analytics_storage === 'denied'
    )
  }));
  expect(before.tag, 'gtag.js must not load before consent').toBe(false);
  expect(before.gtag).toBe(true);
  expect(before.defaultDenied).toBe(true);

  await page.getByRole('button', { name: 'Allow analytics' }).click();
  await expect(page.locator('#deepdell-consent')).toHaveCount(0);

  const accepted = await page.evaluate(() => ({
    tag: document.querySelector('script[src*="googletagmanager.com/gtag/js?id=G-K592HB9G99"]') !== null,
    granted: Array.isArray(window.dataLayer) && window.dataLayer.some(
      item => item && item[0] === 'consent' && item[1] === 'update' &&
        item[2]?.analytics_storage === 'granted'
    )
  }));
  expect(accepted.tag).toBe(true);
  expect(accepted.granted).toBe(true);
});

test('consent rejection keeps analytics storage denied', async ({ page }) => {
  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.getByRole('button', { name: 'Reject' }).click();
  const denied = await page.evaluate(() => Array.isArray(window.dataLayer) && window.dataLayer.some(
    item => item && item[0] === 'consent' && item[1] === 'update' &&
      item[2]?.analytics_storage === 'denied'
  ));
  expect(denied).toBe(true);
  const tag = await page.evaluate(() => document.querySelector('script[src*="googletagmanager.com/gtag/js"]') !== null);
  expect(tag, 'gtag.js must not load after rejection').toBe(false);
});

test('mobile navigation opens and closes', async ({ browser }) => {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true });
  const page = await context.newPage();
  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  const menu = page.locator('.menu');
  await expect(menu).toHaveAttribute('aria-expanded', 'false');
  await menu.click();
  await expect(menu).toHaveAttribute('aria-expanded', 'true');
  await menu.click();
  await expect(menu).toHaveAttribute('aria-expanded', 'false');
  await context.close();
});

test('Agentic Check reaches and executes the production audit Worker', async ({ page }) => {
  await page.goto(BASE + '/agentic-check.html', { waitUntil: 'domcontentloaded', timeout: 30000 });
  const result = await page.evaluate(async () => {
    const api = 'https://deepdell-contact.deepdell-api.workers.dev';
    const config = await fetch(api + '/api/config').then(r => r.json());
    const auditResponse = await fetch(api + '/api/audit', {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
      body: JSON.stringify({url: 'https://deepdell.com'})
    });
    const audit = await auditResponse.json();
    return {config, audit};
  });
  expect(result.config.ok).toBe(true);
  expect(result.config.auditAvailable).toBe(true);
  expect(result.config.formProvider).toBe('web3forms');
  expect(result.config.contactAvailable).toBe(true);
  expect(typeof result.config.web3formsAccessKey).toBe('string');
  expect(result.config.web3formsAccessKey.length).toBeGreaterThan(10);
  expect(result.audit.ok).toBe(true);
  expect(result.audit.mode).toBe('server');
  expect(result.audit.results).toHaveLength(25);
});

test('Agentic audit returns discovery results when a public homepage blocks server-side fetching', async ({ page }) => {
  await page.goto(BASE + '/agentic-check.html', { waitUntil: 'domcontentloaded', timeout: 30000 });
  const audit = await page.evaluate(async () => {
    const response = await fetch('https://deepdell-contact.deepdell-api.workers.dev/api/audit', {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
      body: JSON.stringify({url: 'https://www.daraz.pk/'})
    });
    return response.json();
  });
  expect(audit.ok).toBe(true);
  expect(audit.results).toHaveLength(25);
  expect(audit.homepage).toBeTruthy();
});

test('lead forms are wired to the Web3Forms helper', async ({ page }) => {
  for (const path of ['/contact.html', '/game.html', '/commerce-calculator.html', '/agentic-check.html']) {
    await page.goto(BASE + path, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await expect.poll(() => page.evaluate(() => typeof window.submitDeepdellForm === 'function')).toBe(true);
  }
});

test('translated pages are published with correct language metadata', async ({ page }) => {
  const LANGS = { fr: 'ltr', de: 'ltr', es: 'ltr', it: 'ltr', ar: 'rtl', ms: 'ltr', id: 'ltr' };
  for (const [lang, dir] of Object.entries(LANGS)) {
    for (const path of ['/', '/services.html', '/contact.html']) {
      const response = await page.goto(`${BASE}/${lang}${path}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
      expect(response?.status(), `${lang}${path}`).toBe(200);
      const meta = await page.evaluate(() => ({
        lang: document.documentElement.lang,
        dir: document.documentElement.dir,
        alternates: document.querySelectorAll('link[rel="alternate"][hreflang]').length,
        switcher: document.querySelectorAll('.lang-menu a').length
      }));
      expect(meta.lang).toBe(lang);
      expect(meta.dir).toBe(dir);
      expect(meta.alternates).toBe(9);
      expect(meta.switcher).toBe(8);
    }
  }
});

test('pricing shows local currency defaults and the currency picker works', async ({ page }) => {
  const defaults = { ms: 'MYR', id: 'IDR', ar: 'AED', fr: 'EUR' };
  for (const [lang, cur] of Object.entries(defaults)) {
    await page.goto(`${BASE}/${lang}/pricing.html`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await expect(page.locator('#dd-cur')).toHaveValue(cur);
  }
  await page.goto(BASE + '/pricing.html', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.selectOption('#dd-cur', 'MYR');
  await expect(page.locator('.plan .amt').first()).toContainText('RM');
});

test('early sign-up popup opens from the footer, asks for consent and closes with Escape', async ({ page }) => {
  await page.goto(BASE + '/services.html', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await expect(page.locator('#dd-signup')).toBeHidden();
  await page.locator('footer [data-su-open]').click();
  await expect(page.locator('#dd-signup')).toBeVisible();
  await expect(page.locator('#dd-signup input[name="email"]')).toBeVisible();
  await expect(page.locator('#dd-signup input[name="phone"]')).not.toHaveAttribute('required', '');
  await expect(page.locator('#dd-signup input[name="consent"]')).toHaveAttribute('required', '');
  await page.keyboard.press('Escape');
  await expect(page.locator('#dd-signup')).toBeHidden();
});
