
(() => {
 const raw=document.getElementById('ad-products'); if(!raw)return;
 let products=[];try{products=JSON.parse(raw.textContent)}catch{}
 const category=document.getElementById('ad-category'),canvas=document.getElementById('ad-canvas'),ctx=canvas.getContext('2d'),preview=document.getElementById('ad-preview'),download=document.getElementById('ad-download'),status=document.getElementById('ad-status');
 let timer=null,recorded=null,stream=null;
 function draw(items,frame=0,elapsed=0){
   ctx.fillStyle='#070707';ctx.fillRect(0,0,1080,1920);
   ctx.fillStyle='#ed1028';ctx.fillRect(0,0,1080,18);
   ctx.fillStyle='#fff';ctx.font='bold 92px Arial';ctx.textAlign='center';ctx.fillText('HUSTLE NATION',540,145);
   ctx.fillStyle='#ed1028';ctx.font='bold 50px Arial';ctx.fillText((category.value||'COLLECTION').toUpperCase(),540,235);
   ctx.strokeStyle='#ed1028';ctx.lineWidth=5;ctx.strokeRect(85,285,910,1220);
   const p=items.length?items[frame%items.length]:null;
   if(p&&p.image){
     const img=new Image();img.onload=()=>{ctx.fillStyle='#111';ctx.fillRect(125,325,830,850);const scale=Math.min(830/img.width,850/img.height);const w=img.width*scale,h=img.height*scale;ctx.drawImage(img,125+(830-w)/2,325+(850-h)/2,w,h);drawText(p);};img.src='/static/uploads/'+p.image;
   } else {drawText(p);}
   function drawText(item){ctx.fillStyle='#fff';ctx.font='bold 58px Arial';ctx.fillText(item?item.name:'UPLOAD PRODUCT PHOTOS',540,1280);ctx.fillStyle='#ed1028';ctx.font='bold 72px Arial';ctx.fillText(item?'R'+item.price:'HUSTLE NATION',540,1390);ctx.fillStyle='#aaa';ctx.font='32px Arial';ctx.fillText(item?item.category:'THE HUSTLE NEVER STOPS',540,1460);}
   ctx.fillStyle='#fff';ctx.font='bold 55px Arial';ctx.fillText('SHOP THE DROP',540,1640);
   ctx.fillStyle='#aaa';ctx.font='32px Arial';ctx.fillText('WhatsApp 069 888 1104',540,1710);
   ctx.fillStyle='#ed1028';ctx.fillRect(160,1790,760,7);ctx.fillStyle='#fff';ctx.font='24px Arial';ctx.fillText('DEVELOPED BY OTSILE GRAPHICS © 2024',540,1850);
 }
 function selected(){return products.filter(p=>p.category===category.value&&p.active);}
 function makeStream(){return canvas.captureStream(25);}
 function startAd(){
   const items=selected();if(!items.length){status.textContent='No products in this category. Add products in Products & Inventory first.';return;}
   if(!window.MediaRecorder){status.textContent='This browser does not support video recording. Try Chrome on desktop.';return;}
   if(timer)clearInterval(timer);let frame=0,elapsed=0;draw(items,0);
   stream=makeStream();let chunks=[];let mime=MediaRecorder.isTypeSupported('video/webm;codecs=vp9')?'video/webm;codecs=vp9':'video/webm';
   const rec=new MediaRecorder(stream,{mimeType:mime});rec.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};rec.onstop=()=>{recorded=new Blob(chunks,{type:'video/webm'});status.textContent='Your 60-second category advert is ready. Tap Download Video.';stream.getTracks().forEach(t=>t.stop());};
   rec.start();status.textContent='Recording advert… 60 seconds. Keep this page open.';
   timer=setInterval(()=>{elapsed++;frame=Math.floor(elapsed/5)%items.length;draw(items,frame,elapsed);if(elapsed>=60){clearInterval(timer);rec.stop();}},1000);
 }
 preview?.addEventListener('click',startAd);
 download?.addEventListener('click',()=>{if(!recorded){status.textContent='Create the 60-second advert first.';return;}const a=document.createElement('a');a.href=URL.createObjectURL(recorded);a.download=(category.value||'hustle-nation').toLowerCase().replace(/[^a-z0-9]+/g,'-')+'-60sec-ad.webm';a.click();URL.revokeObjectURL(a.href);});
 category?.addEventListener('change',()=>draw(selected(),0));
 draw(selected(),0);
})();
