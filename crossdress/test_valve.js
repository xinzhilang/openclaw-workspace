(async () => {
  // 开阀
  let r1 = await fetch('/von');
  let t1 = await r1.text();
  await new Promise(r => setTimeout(r, 1000));
  // 读状态
  let r2 = await fetch('/q');
  let t2 = await r2.json();
  // 关阀
  let r3 = await fetch('/voff');
  let t3 = await r3.text();
  return '开阀: ' + t1 + ' | 状态: ' + JSON.stringify(t2) + ' | 关阀: ' + t3;
})();
