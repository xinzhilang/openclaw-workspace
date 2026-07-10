const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: false,
    args: ['--start-maximized']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    locale: 'zh-CN',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });

  const page = await context.newPage();
  
  // 商品列表
  const items = [
    { name: 'YF-S401 流量计 ¥7', url: 'https://item.taobao.com/item.htm?id=651170176593', store: '轩特佳电子' },
    { name: 'LM2596 降压模块 ¥3', url: 'https://item.taobao.com/item.htm?id=561098111071', store: '轩特佳电子' },
    { name: 'IRF520 MOSFET ¥5', url: 'https://shop257979230.taobao.com/search.htm?search=y&keyword=IRF520', store: '轩特佳电子' },
    { name: 'XGZP6847 0~100kPa 气路 ¥25', url: 'https://item.taobao.com/item.htm?id=544126074568', store: 'CFsensor' },
    { name: 'XGZP6847 0~40kPa 水路 ¥22', url: 'https://item.taobao.com/item.htm?id=546435913388', store: 'CFsensor' },
    { name: '12V常闭电磁阀 ¥5.5', url: 'https://item.taobao.com/item.htm?id=885255418295', store: '百乘电子' }
  ];

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    console.log(`\n[${i+1}/${items.length}] ${item.store} → ${item.name}`);
    
    await page.goto(item.url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    // 截图
    await page.screenshot({ 
      path: `C:\\Users\\喜\\.openclaw\\workspace\\crossdress\\auto-enema\\item_${i+1}.png`,
      fullPage: true 
    });
    
    // 尝试加入购物车
    try {
      const addBtn = page.locator('button').filter({ hasText: /加入购物车/ }).first();
      const isVisible = await addBtn.isVisible({ timeout: 3000 });
      if (isVisible) {
        await addBtn.click();
        console.log(`  ✅ 已加入购物车`);
        await page.waitForTimeout(2000);
      } else {
        console.log(`  ⚠️ 无加入购物车按钮（可能是搜索页或需登录）`);
      }
    } catch(e) {
      console.log(`  ⚠️ ${e.message.slice(0, 60)}`);
    }
  }

  // 打开购物车
  console.log('\n📋 打开购物车...');
  await page.goto('https://cart.taobao.com/cart.htm', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: 'C:\\Users\\喜\\.openclaw\\workspace\\crossdress\\auto-enema\\cart_final.png' });
  
  console.log('\n✅ 流程完成！浏览器已打开购物车页面供你查看。');
  
  // 保持浏览器打开，不自动关闭
  await new Promise(() => {});
})().catch(err => {
  console.error('❌ 错误:', err.message);
  process.exit(1);
});
