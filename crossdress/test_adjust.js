(async () => {
  // 先把水量加50
  let r1 = await fetch('/p?volume=350');
  let t1 = await r1.text();
  // 读实时状态
  let r2 = await fetch('/q');
  let t2 = await r2.json();
  return '调整结果: ' + t1 + ' | 实时状态: ' + JSON.stringify(t2);
})();
