import { test, expect } from '@playwright/test';

const BASE = 'https://deepdell.com';
const PAGES = [
  '/',
  '/services.html',
  '/shopify-plus.html',
  '/ai.html',
  '/data.html',
  '/industries.html',
  '/contact.html',
  '/agentic-check.html',
  '/contact-card.html',
  '/game.html',
  '/commerce-calculator.html',
  '/privacy.html'
];

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

test('GA4 and consent mode are active on the production homepage', async ({ page }) => {
  await page.goto(BASE + '/', { waitUntil: 'networkidle', timeout: 30000 });
  await expect(page.locator('#deepdell-consent')).toBeVisible();

  const ga = await page.evaluate(() => ({
    tag: document.querySelector('script[src*="googletagmanager.com/gtag/js?id=G-K592HB9G99"]') !== null,
    gtag: typeof window.gtag === 'function',
    defaultDenied: Array.isArray(window.dataLayer) && window.dataLayer.some(
      item => item && item[0] === 'consent' && item[1] === 'default' &&
        item[2]?.analytics_storage === 'denied'
    )
  }));
  expect(ga.tag).toBe(true);
  expect(ga.gtag).toBe(true);
  expect(ga.defaultDenied).toBe(true);

  await page.getByRole('button', { name: 'Allow analytics' }).click();
  await expect(page.locator('#deepdell-consent')).toHaveCount(0);

  const accepted = await page.evaluate(() => ({
    granted: Array.isArray(window.dataLayer) && window.dataLayer.some(
      item => item && item[0] === 'consent' && item[1] === 'update' &&
        item[2]?.analytics_storage === 'granted'
    )
  }));
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

test('lead forms are wired to the Web3Forms helper', async ({ page }) => {
  for (const path of ['/contact.html', '/game.html', '/commerce-calculator.html', '/agentic-check.html']) {
    await page.goto(BASE + path, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await expect.poll(() => page.evaluate(() => typeof window.submitDeepdellForm === 'function')).toBe(true);
  }
});
