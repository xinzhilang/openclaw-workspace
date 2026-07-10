(async () => {
  let r = await fetch('/rst');
  let t = await r.text();
  return '流量清零: ' + t;
})();
