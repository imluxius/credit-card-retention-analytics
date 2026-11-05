// Optional end-to-end checks against the real generated dashboard, opened offline.
const { chromium } = require('playwright');
const { execFileSync } = require('node:child_process');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const root = path.resolve(__dirname, '..');
const expected = JSON.parse(execFileSync(process.env.PYTHON || 'python', ['-c', `
import csv, json
from pathlib import Path
rows = list(csv.DictReader(Path('data/raw/BankChurners.csv').open()))
cards = [''] + sorted({r['Card_Category'] for r in rows})
incomes = [''] + sorted({r['Income_Category'] for r in rows})
out=[]
for card in cards:
 for income in incomes:
  subset=[r for r in rows if (not card or r['Card_Category']==card) and (not income or r['Income_Category']==income)]
  lost=sum(r['Attrition_Flag']=='Attrited Customer' for r in subset)
  bands=[]
  for lo,hi in [(0,40),(40,60),(60,80),(80,1000000)]:
   group=[r for r in subset if lo<=int(r['Total_Trans_Ct'])<hi]
   bands.append({'customers':len(group),'churned':sum(r['Attrition_Flag']=='Attrited Customer' for r in group)})
  out.append({'card':card,'income':income,'customers':len(subset),'churned':lost,'bands':bands})
print(json.dumps(out))
`], { cwd: root, encoding: 'utf8' }));

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 });
  const errors = [], requests = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
  page.on('request', req => { if (/^https?:/.test(req.url())) requests.push(req.url()); });
  try {
    await page.goto(pathToFileURL(path.join(root, 'dashboard/index.html')).href);
    assert.equal(await page.locator('#customers').innerText(), '10,127');
    assert.equal(await page.locator('#rate').innerText(), '16.07%');
    for (const e of expected) {
      await page.selectOption('#card', e.card);
      await page.selectOption('#income', e.income);
      const actual = await page.evaluate(() => window.dashboardState);
      assert.equal(actual.customers, e.customers, `population ${e.card}/${e.income}`);
      assert.equal(actual.churned, e.churned, `attrited ${e.card}/${e.income}`);
      assert.equal(actual.churn_rate, e.customers ? e.churned / e.customers : null);
      actual.segments.forEach((r, i) => {
        assert.equal(r.customers, e.bands[i].customers);
        assert.equal(r.churned, e.bands[i].churned);
      });
    }
    // Deliberate unavailable combination verifies the zero-population UI.
    await page.evaluate(() => {
      const select = document.getElementById('card');
      select.add(new Option('Test empty category', '__empty__'));
      select.value = '__empty__';
      select.dispatchEvent(new Event('change'));
    });
    assert.equal(await page.locator('#customers').innerText(), '0');
    assert.equal(await page.locator('#rate').innerText(), '—');
    assert.equal(await page.locator('#transactions').innerText(), '—');
    assert.ok(!(await page.locator('body').innerText()).includes('NaN'));
    await page.click('#reset');
    assert.equal(await page.locator('#customers').innerText(), '10,127');
    await page.selectOption('#card', 'Blue');
    await page.selectOption('#income', 'Unknown');
    const downloadPromise = page.waitForEvent('download');
    await page.click('#export');
    const download = await downloadPromise;
    const downloadedPath = await download.path();
    const exported = fs.readFileSync(downloadedPath, 'utf8');
    assert.ok(exported.includes('"Blue","Unknown"'));
    assert.equal(exported.split('\r\n').length, 5);
    assert.ok(!exported.includes('CLIENTNUM'));
    // Reconcile actual downloaded rows, not just the in-page state.
    const decoded = JSON.parse(execFileSync(process.env.PYTHON || 'python', ['-c',
      'import csv,json,sys; print(json.dumps(list(csv.DictReader(open(sys.argv[1])))))', downloadedPath],
      { encoding: 'utf8' }));
    const filteredExpected = expected.find(e => e.card === 'Blue' && e.income === 'Unknown');
    decoded.forEach((r, i) => {
      assert.equal(Number(r.customers), filteredExpected.bands[i].customers);
      assert.equal(Number(r.attrited), filteredExpected.bands[i].churned);
    });
    await page.click('#reset');
    await page.evaluate(() => {
      const option = document.querySelector('#card option[value="__empty__"]');
      option.remove();
    });
    const artifacts = path.join(root, 'artifacts');
    fs.mkdirSync(artifacts, { recursive: true });
    for (const width of [390, 820, 1440]) {
      await page.setViewportSize({ width, height: width === 390 ? 844 : 1100 });
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), `overflow at ${width}px`);
      await page.screenshot({ path: path.join(artifacts, `dashboard-${width}.png`), fullPage: true });
    }
    if (process.argv.includes('--update-preview')) {
      await page.screenshot({ path: path.join(root, 'reports/dashboard-preview.png'), fullPage: true });
    }
    assert.deepEqual(requests, [], 'dashboard must operate without network requests');
    assert.deepEqual(errors, [], 'browser console/page errors');
    const result = { filterCombinations: expected.length, viewports: [390, 820, 1440],
      downloadReconciled: true, emptyState: true, networkRequests: 0, consoleErrors: 0 };
    fs.writeFileSync(path.join(artifacts, 'browser-results.json'), JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exit(1); });
