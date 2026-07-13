const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  await page.goto('https://s.taobao.com/search?q=%E6%B0%94%E5%8E%8B%E6%B0%B4%E5%8E%8B%E6%B6%B2%E5%8E%8B%E6%95%B0%E5%AD%97%E6%A8%A1%E6%8B%9F%E4%BF%A1%E5%8F%B73.3v+sop%E5%B0%81%E8%A3%85+200kpa+700kpa+%E5%8E%8B%E5%8A%9B%E4%BC%A0%E6%84%9F%E5%99%A8', { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForTimeout(3000);
  
  const items = await page.evaluate(() => {
    const results = [];
    const titles = document.querySelectorAll('.title a, .J_ItemTitle a, .item-title a, [class*=title] a');
    const prices = document.querySelectorAll('.price, .g_price, [class*=price]');
    const shops = document.querySelectorAll('.shop a, [class*=shop] a, .seller a');
    
    const links = document.querySelectorAll('a[href*="item.taobao.com"]');
    links.forEach((a, i) => {
      const parent = a.closest('[class*=item]') || a.parentElement.parentElement;
      const priceEl = parent ? parent.querySelector('[class*=price]') : null;
      const name = (a.textContent || '').trim().substring(0, 80);
      if (name && name.length > 5) {
        results.push({ name, price: priceEl ? priceEl.textContent.trim().substring(0, 20) : '?', url: a.href });
      }
    });
    return results.slice(0, 8);
  });

  console.log('\n=== 搜索结果 ===');
  items.forEach((item, i) => {
    console.log(`\n[${i+1}] ${item.name}`);
    console.log(`    价格: ${item.price}`);
    console.log(`    链接: ${item.url}`);
  });

  await page.screenshot({ path: 'auto-enema/pressure_search.png', fullPage: true });
  await browser.close();
})().catch(err => {
  console.error(err.message);
  process.exit(1);
});
