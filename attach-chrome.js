const playwright = require('playwright-core');
(async () => {
  try {
    const browser = await playwright.chromium.connectOverCDP('http://localhost:9222');
    const context = browser.contexts()[0];
    const pages = context.pages();
    console.log('您的标签页:');
    for (let i = 0; i < pages.length; i++) {
      const page = pages[i];
      const title = await page.title();
      const url = page.url();
      console.log(`${i+1}. ${title} - ${url}`);
    }
    // 示例: 百度搜 "iPhone 15 Pro"
    const page = pages[0] || await context.newPage();
    await page.goto('https://www.baidu.com');
    await page.fill('input[name="wd"]', 'iPhone 15 Pro');
    await page.press('input[name="wd"]', 'Enter');
    await page.screenshot({ path: 'search.png' });
    console.log('✅ 搜索完成，截图: search.png');
    // browser.close(); // 保持打开
  } catch (error) {
    console.error('错误:', error.message);
    if (error.message.includes('Target closed')) console.log('提示: Chrome 调试端口9222未运行，运行 Chrome --remote-debugging-port=9222');
  }
})();
