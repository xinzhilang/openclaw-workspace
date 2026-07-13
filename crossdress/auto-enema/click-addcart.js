var btn = document.querySelector('button');
var allButtons = document.querySelectorAll('button');
var addCartBtn = null;
for (var i = 0; i < allButtons.length; i++) {
  var t = allButtons[i].textContent || allButtons[i].innerText;
  if (t.indexOf('\u52a0\u5165\u8d2d\u7269\u8f66') >= 0) {
    addCartBtn = allButtons[i];
    break;
  }
}
if (addCartBtn) {
  addCartBtn.click();
  'OK - 已点击加入购物车';
} else {
  'NOT_FOUND';
}
