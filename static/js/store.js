
(() => {
 const loader=document.getElementById('loader');
 if(loader){const started=Date.now();const done=()=>{const wait=Math.max(0,30000-(Date.now()-started));setTimeout(()=>loader.classList.add('hide'),wait)};if(document.readyState==='complete')done();else window.addEventListener('load',done,{once:true});}
 const toggle=document.getElementById('chat-toggle'),panel=document.getElementById('chat-panel'),close=document.getElementById('chat-close');
 if(toggle&&panel){toggle.addEventListener('click',()=>panel.classList.toggle('open'));close.addEventListener('click',()=>panel.classList.remove('open'));}
 const form=document.getElementById('chat-form');
 if(form)form.addEventListener('submit',async e=>{e.preventDefault();const input=document.getElementById('chat-input'),messages=document.getElementById('chat-messages'),msg=input.value.trim();if(!msg)return;messages.insertAdjacentHTML('beforeend',`<p class="user">${escapeHtml(msg)}</p>`);input.value='';try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});const d=await r.json();messages.insertAdjacentHTML('beforeend',`<p class="bot">${escapeHtml(d.reply)}</p>`);}catch{messages.insertAdjacentHTML('beforeend','<p class="bot">Sorry, I could not connect. Please contact us on WhatsApp.</p>');}messages.scrollTop=messages.scrollHeight;});
 function escapeHtml(s){return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
})();
