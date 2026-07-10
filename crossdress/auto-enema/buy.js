const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: false,
    args: ['--start-maximized', '--disable-popup-blocking']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    locale: 'zh-CN'
  });

  const page = await context.newPage();

  // 打开淘宝首页
  await page.goto('https://www.taobao.com/', { waitUntil: 'domcontentloaded', timeout: 15000 });
  
  // 等用户登录：检测到页面顶部有用户名或导航到首页
  console.log('⏳ 请在打开的浏览器中扫码登录淘宝...');
  
  let loggedIn = false;
  for (let t = 0; t < 60; t++) {
    const url = page.url();
    if (url.includes('taobao.com') && !url.includes('login')) {
      const html = await page.content().catch(() => '');
      if (html.includes('13603113488xi') || html.includes('我的淘宝') || html.includes('购物车')) {
        loggedIn = true;
        console.log('✅ 登录成功！');
        break;
      }
    }
    await page.waitForTimeout(1000);
  }

  if (!loggedIn) {
    console.log('⚠️ 登录超时，尝试继续...');
  }

  const items = [
    { name: '① YF-S401 流量计 ¥7', url: 'https://item.taobao.com/item.htm?id=651170176593', shop: true },
    { name: '② LM2596 降压模块 ¥3', url: 'https://item.taobao.com/item.htm?id=561098111071', shop: true },
    { name: '③ 12V常闭电磁阀 ¥5.5', url: 'https://item.taobao.com/item.htm?id=885255418295', shop: true },
    { name: '④ XGZP6847 0~100kPa ¥25', url: 'https://item.taobao.com/item.htm?id=544126074568', shop: true },
    { name: '⑤ XGZP6847 0~40kPa ¥22', url: 'https://item.taobao.com/item.htm?id=546435913388', shop: true },
    { name: '⑥ IRF520 MOSFET ¥5', url: 'https://shop257979230.taobao.com/search.htm?search=y&keyword=IRF520', shop: false },
    { name: '⑦ 自锁急停按钮 ¥2', url: 'https://shop257979230.taobao.com/search.htm?search=y&keyword=%E8%87%AA%E9%94%81%E6%8C%89%E9%92%AE', shop: false },
    { name: '⑧ 硅胶管6mm ¥5', url: 'https://shop257979230.taobao.com/search.htm?search=y&keyword=%E7%A1%85%E8%83%B6%E7%AE%A16mm', shop: false }
  ];

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    console.log(`\n[${i+1}/${items.length}] ${item.name}`);
    
    await page.goto(item.url, { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(3000);
    
    if (item.shop) {
      // 等待"加入购物车"按钮出现 最多8秒
      let found = false;
      for (let w = 0; w < 16; w++) {
        try {
          const btn = page.locator('button').filter({ hasText: /加入购物车/ }).first();
          if (await btn.isVisible()) {
            await btn.click();
            console.log(`  ✅ 已加入购物车`);
            found = true;
            await page.waitForTimeout(2000);
            break;
          }
        } catch(e) {}
        await page.waitForTimeout(500);
      }
      if (!found) {
        console.log(`  ⚠️ 未找到加入购物车按钮，可能需要登录`);
        await page.screenshot({ path: `auto-enema/miss_${i+1}.png` });
      }
    } else {
      console.log(`  🔍 店铺搜索页已打开，请手动选品加购`);
    }
  }

  console.log(`\n📋 打开购物车...`);
  await page.goto('https://cart.taobao.com/cart.htm', { waitUntil: 'domcontentloaded' });
  console.log(`✅ 全部完成！浏览器窗口保持打开，请查看购物车。`);

  await new Promise(() => {});
})().catch(err => {
  console.error('❌', err.message);
  process.exit(1);
});
