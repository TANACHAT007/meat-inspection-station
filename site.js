(function(){var r=document.documentElement,t=localStorage.getItem('mq_theme');if(t)r.dataset.theme=t;
document.addEventListener('DOMContentLoaded',function(){var b=document.getElementById('tbtn'),m=document.getElementById('mbtn'),l=document.getElementById('links');
if(b)b.onclick=function(){var d=r.dataset.theme==='dark'||(!r.dataset.theme&&matchMedia('(prefers-color-scheme:dark)').matches);r.dataset.theme=d?'light':'dark';try{localStorage.setItem('mq_theme',r.dataset.theme)}catch(e){}};
if(m)m.onclick=function(){l.classList.toggle('open')};
var p=location.pathname.split('/').pop()||'index.html';document.querySelectorAll('.links a').forEach(function(a){if(a.getAttribute('href')===p)a.classList.add('cur')});});})();
