(async () => {
  let r = await fetch('/bz');
  let t = await r.text();
  return '蜂鸣: ' + t;
})();
