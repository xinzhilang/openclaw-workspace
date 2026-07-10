var btns = document.querySelectorAll('button');
var clicked = false;
for(var i = 0; i < btns.length; i++) {
  if(btns[i].innerText.indexOf('加入购物车') >= 0) {
    btns[i].click();
    clicked = true;
  }
}
if (clicked) '已点击加入购物车' + btns.length + ' of ' + btns.length + ' buttons scanned';
else '未找到加入购物车按钮';
