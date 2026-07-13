const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false, args: ['--window-size=1280,900'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  
  await page.goto('https://item.taobao.com/item.htm?id=761891658553', { timeout: 20000 });
  await page.waitForTimeout(4000);
  
  const info = await page.evaluate(() => {
    return {
      title: document.title,
      body: (document.body.innerText || '').substring(0, 500)
    };
  });
  
  console.log('标题:', info.title);
  console.log('内容:', info.body);
  
  await page.screenshot({ path: 'auto-enema/item_check.png' });
  
  console.log('\n截图已保存，5秒后关闭...');
  await page.waitForTimeout(5000);
  await browser.close();
})();
