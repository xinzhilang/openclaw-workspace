(async () => {
  // 开充气
  let r1 = await fetch('/ion');
  let t1 = await r1.text();
  
  // 等3秒
  await new Promise(r => setTimeout(r, 3000));
  
  // 读气压
  let r2 = await fetch('/q');
  let j2 = await r2.json();
  
  // 停止充气
  let r3 = await fetch('/ioff');
  let t3 = await r3.text();
  
  return '充气启动: ' + t1 + ' | 3秒后气压: ' + JSON.stringify(j2) + ' | 停止充气: ' + t3;
})();
