// Chrome 扩展配置脚本
// 用法: 在 Chrome DevTools Console 中运行此脚本

const config = {
  relay: {
    enabled: true,
    relayServerUrl: 'ws://localhost:18792',
    gatewayUrl: 'ws://localhost:18789',
    gatewayToken: '7e17a6cde70df52635e7fffe92375dda7693a45ae9d2288a',
    autoConnect: true,
    reconnectAttempts: 3,
    reconnectDelay: 1000
  },
  browser: {
    profile: 'chrome-relay-profile',
    enableLogging: false,
    screenshotFormat: 'png',
    screenshotQuality: 90
  },
  features: {
    autoScreenshot: false,
    highlightElements: true,
    networkLogging: false,
    consoleLogging: false
  }
};

console.log('OpenClaw Browser Relay 配置');
console.log('==============================');
console.log('配置内容:', JSON.stringify(config, null, 2));

// 尝试保存到 localStorage
try {
  localStorage.setItem('openclaw-relay-config', JSON.stringify(config));
  console.log('✅ 配置已保存到 localStorage');
} catch (e) {
  console.log('⚠️ 无法保存到 localStorage:', e.message);
}

// 返回配置
config;
