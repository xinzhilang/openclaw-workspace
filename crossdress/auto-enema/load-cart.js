document.title='凑单清单';
var cartDiv = document.createElement('div');
cartDiv.id = 'carthelper';
cartDiv.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.95);z-index:99999;overflow:auto;padding:20px;color:white;font-family:Arial,sans-serif';
var closeBtn = document.createElement('button');
closeBtn.textContent = '\u2715';
closeBtn.style.cssText = 'position:fixed;top:10px;right:10px;padding:8px 15px;background:#444;color:white;border:none;border-radius:5px;cursor:pointer;font-size:18px;z-index:100000';
closeBtn.onclick = function() { cartDiv.remove(); };
cartDiv.appendChild(closeBtn);

var title = document.createElement('h1');
title.style.cssText = 'color:#ff6a00;text-align:center;font-size:24px';
title.textContent = '\uD83D\uDED2 \u51D1\u5355\u6E05\u5355 \u2014 \u70B9\u51FB\u76F4\u63A5\u6253\u5F00';
cartDiv.appendChild(title);

var note = document.createElement('p');
note.style.cssText = 'text-align:center;color:#aaa;font-size:13px';
note.textContent = '\u2757 Ctrl+\u70B9\u51FB = \u591A\u6807\u7B7E\u9875\u6253\u5F00\uFF0C\u7136\u540E\u5206\u522B\u52A0\u5230\u8D2D\u7269\u8F66';
cartDiv.appendChild(note);

var items = [
  {store:'\u8F69\u7279\u4F73\u7535\u5B50', name:'YF-S401 \u6D41\u91CF\u8BA1', price:'\u00A57', url:'https://item.taobao.com/item.htm?id=651170176593'},
  {store:'\u8F69\u7279\u4F73\u7535\u5B50', name:'LM2596 \u964D\u538B\u6A21\u5757', price:'\u00A53', url:'https://item.taobao.com/item.htm?id=561098111071'},
  {store:'\u8F69\u7279\u4F73\u7535\u5B50', name:'IRF520 MOSFET \u6A21\u5757', price:'\u00A55', url:'https://shop257979230.taobao.com/search.htm?search=y&keyword=IRF520'},
  {store:'CFsensor', name:'XGZP6847 0~100kPa \u6C14\u8DEF', price:'\u00A525', url:'https://item.taobao.com/item.htm?id=544126074568'},
  {store:'CFsensor', name:'XGZP6847 0~40kPa \u6C34\u8DEF', price:'\u00A522', url:'https://item.taobao.com/item.htm?id=546435913388'},
  {store:'\u767E\u4E58\u7535\u5B50', name:'12V\u5E38\u95ED\u7535\u78C1\u9600', price:'\u00A55.5', url:'https://item.taobao.com/item.htm?id=885255418295'}
];

var lastStore = '';
items.forEach(function(item) {
  if (item.store !== lastStore) {
    var h2 = document.createElement('h2');
    h2.style.cssText = 'color:#ddd;margin-top:20px;font-size:18px;border-bottom:1px solid #333;padding-bottom:5px';
    h2.textContent = '\uD83D\uDCE6 ' + item.store;
    cartDiv.appendChild(h2);
    lastStore = item.store;
  }
  var a = document.createElement('a');
  a.href = item.url;
  a.target = '_blank';
  a.style.cssText = 'display:inline-block;background:#ff6a00;color:white;padding:12px 20px;margin:6px 4px;border-radius:6px;text-decoration:none;font-size:15px;min-width:260px;font-weight:bold';
  a.innerHTML = item.name + ' <span style=color:#ffcc00;font-size:17px>' + item.price + '</span>';
  cartDiv.appendChild(a);
  cartDiv.appendChild(document.createElement('br'));
});

var total = document.createElement('div');
total.style.cssText = 'margin-top:25px;padding:15px;background:#333;border-radius:10px;text-align:center;font-size:22px';
total.innerHTML = '\uD83D\uDCB0 \u5408\u8BA1\u7EA6 <span style=color:#ff6a00;font-size:28px>\u00A594</span> \u542B\u8FD0\u8D39';
cartDiv.appendChild(total);

document.body.appendChild(cartDiv);
console.log('Shopping list loaded');
