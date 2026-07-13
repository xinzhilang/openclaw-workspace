const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const userDataDir = path.join(__dirname, 'temp_profile');
  
  const browser = await chromium.launchPersistentContext(userDataDir, {
    headless: false,
    args: [
      '--start-maximized',
      '--disable-popup-blocking'
    ],
    viewport: null,
    locale: 'zh-CN'
  });

  const pages = browser.pages();
  const page = pages[0];

  // 先打开淘宝首页，可能不需要登录就能加购
  // 如果不行，导航到登录页让用户扫码

  const items = [
    { name: 'YF-S401 流量计 ¥7', url: 'https://item.taobao.com/item.htm?id=651170176593' },
    { name: 'LM2596 降压模块 ¥3', url: 'https://item.taobao.com/item.htm?id=561098111071' },
    { name: 'XGZP6847 0~100kPa ¥25', url: 'https://item.taobao.com/item.htm?id=544126074568' },
    { name: 'XGZP6847 0~40kPa ¥22', url: 'https://item.taobao.com/item.htm?id=546435913388' },
    { name: '12V常闭电磁阀 ¥5.5', url: 'https://item.taobao.com/item.htm?id=885255418295' }
  ];

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    console.log(`[${i+1}/${items.length}] ${item.name}`);
    
    try {
      await page.goto(item.url, { waitUntil: 'domcontentloaded', timeout: 20000 });
      await page.waitForTimeout(3000);
      
      // 检查是否有登录拦截
      const loginModal = page.locator('.login-popup, .login-dialog, #login').first();
      if (await loginModal.isVisible({ timeout: 1000 }).catch(() => false)) {
        console.log('  -> 需登录，请扫码');
        await page.waitForTimeout(15000); // 给用户15秒扫码
      }

      // 寻找加入购物车按钮
      const allBtns = page.locator('button');
      const btnCount = await allBtns.count();
      let found = false;
      
      for (let b = 0; b < btnCount; b++) {
        const text = await allBtns.nth(b).innerText().catch(() => '');
        if (text && text.includes('加入购物车')) {
          await allBtns.nth(b).click();
          console.log(`  ✅ 已加入购物车`);
          found = true;
          await page.waitForTimeout(2000);
          break;
        }
      }
      
      if (!found) {
        console.log(`  ⚠️ 无加入购物车按钮`);
        await page.screenshot({ path: path.join(__dirname, `miss_${i+1}.png`) });
      }
    } catch (e) {
      console.log(`  ❌ ${e.message.slice(0, 80)}`);
    }
  }

  console.log(`\n📋 打开购物车页面...`);
  await page.goto('https://cart.taobao.com/cart.htm', { waitUntil: 'domcontentloaded' });
  
  console.log(`\n✅ 完成！浏览器已打开，你可以查看购物车。`);

  await new Promise(() => {});
})().catch(err => {
  console.error('❌', err.message);
  process.exit(1);
});
