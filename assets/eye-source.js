/* Pure browser port of the Eye → Space procedural ASCII animation.
   No external libraries, images, fonts, or server are required. */
'use strict';
const canvas=document.getElementById('scene'),ctx=canvas.getContext('2d',{alpha:false});
const RAMP=" .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$";
const TAU=Math.PI*2, clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)),mix=(a,b,t)=>a+(b-a)*t;
const ease=x=>{x=clamp(x);return x*x*(3-2*x)};
const ss=(a,b,x)=>ease((x-a)/(b-a));
const fract=x=>x-Math.floor(x);
const hash=(x,y=0)=>fract(Math.sin(x*127.1+y*311.7+5.31)*43758.5453);
function noise(x,y){const ix=Math.floor(x),iy=Math.floor(y),fx=ease(fract(x)),fy=ease(fract(y));return mix(mix(hash(ix,iy),hash(ix+1,iy),fx),mix(hash(ix,iy+1),hash(ix+1,iy+1),fx),fy)}
function fbm(x,y){return .55*noise(x,y)+.30*noise(x*2.31+13,y*2.31)+.15*noise(x*5.17,y*5.17)}
let W,H,cols,rows,cw,ch,scale,start=performance.now(),paused=false,pausedAt=0,last=0;
const stars=Array.from({length:3200},(_,i)=>({x:hash(i,1)*2-1,y:hash(i,2)*2-1,d:.06+hash(i,3)*.94,b:.1+.9*Math.pow(hash(i,4),3.5),phase:hash(i,5)*TAU,f:1+hash(i,6)*2.5,warm:hash(i,7)}));
let streaks=[],nextShooting=30,comet=false;
function resize(){const dpr=Math.min(devicePixelRatio||1,2);W=innerWidth;H=innerHeight;canvas.width=Math.round(W*dpr);canvas.height=Math.round(H*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);ch=Math.max(11,Math.min(17,H/38));cw=ch*.61;rows=Math.max(22,Math.floor(H/ch));cols=Math.max(40,Math.floor(W/cw));cw=W/cols;ch=H/rows;ctx.font=`bold ${Math.min(ch*.94,cw*1.65)}px Consolas, 'Courier New', monospace`;ctx.textAlign='center';ctx.textBaseline='middle';}
addEventListener('resize',resize);resize();
function restart(){start=performance.now();last=0;streaks=[];nextShooting=30;comet=false;for(let i=0;i<stars.length;i++)stars[i].d=.06+hash(i,3)*.94;paused=false}
addEventListener('keydown',e=>{if(e.key.toLowerCase()==='r')restart();if(e.code==='Space'){e.preventDefault();if(paused){start+=performance.now()-pausedAt;paused=false}else{pausedAt=performance.now();paused=true}}if(e.key==='Escape'){pausedAt=performance.now();paused=true}});
function lid(u,ou){const s=u/.78,cu=Math.pow(Math.max(0,1-Math.pow((s+.12)/(s<-.12?.88:1.12),2)),.8),cl=Math.pow(Math.max(0,1-Math.pow(s-.08,2)),.9),vc=.03*cl,vl=mix(vc,.2*cl,.35+.65*ou),vu=mix(vl,-.3*cu,ou);return [vu,vl,cu,cl]}
function heart(x,y,hm,t){const nc=fbm(x*3.5+6,y*3.5),nd=fbm(x*3.5+27,y*3.5+11),wob=1-.65*hm;let hx=x+wob*.4*(nc-.5),hy=-y+wob*.4*(nd-.5);const qcircle=Math.hypot(hx,hy)/.8-1,hh=hy+.12,f=Math.pow(hx*hx+hh*hh-1,3)-hx*hx*Math.pow(hh,3),qheart=.5*Math.cbrt(f),q=mix(qcircle,qheart,hm),ins=clamp(-q/(.8-.35*hm));let body=q<0?.5+.5*Math.sqrt(ins):Math.exp(-Math.max(q,0)*(3+2.5*hm))*.5;const texture=.75+.65*fbm(x*15+22,y*15+t*.09),rim=Math.exp(-Math.pow((q+.04)/.14,2));body=body*texture+rim*.13;return [body*mix(.92,1,ins),body*mix(.16,.58,ins),body*mix(.40,.78,ins)];}
function render(t,dt){const prog=ease((t-5.4)/28),idle=ease(t/5.4),z=Math.exp(Math.log(14)*prog)*(1+.05*idle+.004*Math.sin(t*.9)),zoomSpace=t<33.4?z:14*Math.exp(.03*(t-33.4));const starScale=Math.min(6,.085*Math.pow(zoomSpace,1.25));let blink=0;if(t>=4&&t<=4.36){const d=t-4;blink=d<.09?ease(d/.09):d<.12?1:1-ease((d-.12)/.24)}let ou=Math.min(1,ease((t-.9)/2.4)*(1+.035*Math.sin(Math.PI*ease((t-.9)/2.4))))*(1-.985*blink);
 const gazefade=1-ease((t-5.4)/2.5),gx=(.022*Math.sin(t*1.8)+.012*Math.sin(t*3.1))*gazefade,gy=(.011*Math.sin(t*1.4)-.03*blink)*gazefade;
 const rp=.098*(.76+.24*ease((t-1.8)/3.5))*(1+.025*Math.sin(1.9*t))*(1+.3*prog),full=rp*z*.72>1.03,starAmt=ease((t-6.9)/4.5),nebAmt=ease((t-8.9)/8),hm=ease((t-8.9)/26);
 const viewH=H,invz=1/z;const intensity=new Float32Array(rows*cols),allowed=new Uint8Array(rows*cols);const colors=new Float32Array(rows*cols*3);let step=Math.max(1,Math.ceil(Math.max(rows*cols/12000,1)));ctx.fillStyle='#010203';ctx.fillRect(0,0,W,H);let offx=gx*z,offy=gy*z;
 for(let r=0;r<rows;r++)for(let c=0;c<cols;c++){
 const i=r*cols+c,u0=((c+.5)*cw-W*.5)/viewH,v0=((r+.5)*ch-H*.5)/viewH,u=u0*invz,v=v0*invz,px=u-gx,py=v-gy,rad=Math.hypot(px,py),angle=Math.atan2(py,px),rn=clamp((rad-rp)/(.27-rp),0,1.3),ang=angle/TAU;
 let R=.004,G=.005,B=.012,pm=rad<rp,visible=full||pm;
 if(nebAmt>.002){const gs=Math.min(1.15,.085*Math.pow(z,1.25)),beat=1+.03*Math.sin(t*2.6)*hm*hm;const nc=heart((u0-offx)/(.17*gs*beat),(v0-offy)/(.17*gs*beat),hm,t),amount=1.25*Math.pow(nebAmt,1.3);R+=nc[0]*amount;G+=nc[1]*amount;B+=nc[2]*amount;}
 if(!full){let ir=.55*noise(ang*570+100,rn*19)+.45*noise(ang*970+50,rn*37),rim=ss(.62,1,rn),center=ss(0,.07,rn);let rr=(.80*(1-ss(.24,.58,rn))+.42*ss(.24,.58,rn))*(.45+1.05*ir)*(1-.82*rim)*(.55+.45*center),gg=(.45*(1-ss(.24,.58,rn))+.20*ss(.24,.58,rn))*(.45+1.05*ir)*(1-.82*rim),bb=.08*(.45+1.05*ir)*(1-rim);
 let er=rr,eg=gg,eb=bb;
 if(z<3.4){const s=u/.78,edges=lid(u,ou),vt=v+.055*s,inside=vt>=edges[0]&&vt<=edges[1],skintex=fbm(u*95+20,v*95+20),du=Math.max(edges[0]-vt,0),dl=Math.max(vt-edges[1],0),dist=Math.max(du,dl),sh=(.5+.5*ss(0,.3,dist))*(.9+.2*skintex),crease=Math.exp(-Math.pow((du-.075-.03*(1-ou))/.02,2)),brow=Math.exp(-Math.pow((vt+.42+.10*s*s)/.05,2));let sr=.62*sh*(1-.42*crease)*(1-.8*brow),sg=.4*sh*(1-.42*crease)*(1-.8*brow),sb=.29*sh*(1-.42*crease)*(1-.8*brow);if(!inside){er=sr;eg=sg;eb=sb}else if(rad>.27){let sclsh=.45+.55*ss(0,.22,vt-edges[0]);er=.8*sclsh;eg=.82*sclsh;eb=.86*sclsh;}visible=inside&&pm;
 if(!inside&&Math.abs(vt-edges[0])<.012){er=.08;eg=.045;eb=.035}
 }else{visible=pm;}
 if(pm){er=R;eg=G;eb=B;}if(rad<.27&&rad>rp&&z<3.4){const catchlight=Math.exp(-Math.pow((px-.075)/.036,2)-Math.pow((py+.04)/.036,2))*(1-ease((z-1.6)/2.4));er+=catchlight*1.5;eg+=catchlight*1.45;eb+=catchlight*1.4;}
 R=er;G=eg;B=eb;
 }
 let vign=1-.3*ss(.4,1,Math.hypot(u0,v0)),fade=ease(t/1.2);R=(1-Math.exp(-2*Math.max(0,R)))*vign*fade;G=(1-Math.exp(-2*Math.max(0,G)))*vign*fade;B=(1-Math.exp(-2*Math.max(0,B)))*vign*fade;
 const lum=clamp((.30*R+.60*G+.10*B)),dither=(hash(c,r)-.5)*.07,index=clamp(Math.floor((Math.pow(lum,.72)+dither)*(RAMP.length-1)),0,RAMP.length-1);intensity[i]=lum;allowed[i]=visible?1:0;colors[i*3]=R;colors[i*3+1]=G;colors[i*3+2]=B;
 if(index>0){ctx.fillStyle=`rgb(${Math.round(255*clamp(R*1.15))},${Math.round(255*clamp(G*1.15))},${Math.round(255*clamp(B*1.15))})`;ctx.fillText(RAMP[index],(c+.5)*cw,(r+.5)*ch)}
 }
 const vf=.010+.05*prog+(t>33.4?.015:0);for(let i=0;i<stars.length;i++){const s=stars[i];s.d-=vf*dt;if(s.d<.06){s.d+=.94;s.x=hash(i+Math.floor(t)*59,18)*2-1;s.y=hash(i+Math.floor(t)*73,19)*2-1;}
 if(starAmt<.003)continue;const sx=(s.x*starScale/s.d+offx)*H+W*.5,sy=(s.y*starScale/s.d+offy)*H+H*.5,c=Math.floor(sx/cw),r=Math.floor(sy/ch);if(c<0||c>=cols||r<0||r>=rows)continue;const at=r*cols+c;if(!allowed[at])continue;const alpha=ss(1,.82,s.d)*(.8+.2*Math.sin(t*s.f+s.phase))*starAmt,b=s.b*alpha*(1+.05/s.d);if(b<intensity[at]*.7||b<.10)continue;const power=clamp(.35+.9*b),warm=s.warm,col=`rgb(${Math.floor(255*power)},${Math.floor(255*power*(.82+.16*(1-warm)))},${Math.floor(255*power*(.55*warm+1*(1-warm)))})`;ctx.fillStyle=col;ctx.fillText(b>.85?'@':b>.42?'*':b>.2?'+':'.',(c+.5)*cw,(r+.5)*ch);if(b>.63){ctx.globalAlpha=clamp(b*.5);ctx.fillText('—',(c-.5)*cw,(r+.5)*ch);ctx.fillText('—',(c+1.5)*cw,(r+.5)*ch);ctx.fillText('|',(c+.5)*cw,(r-.5)*ch);ctx.fillText('|',(c+.5)*cw,(r+1.5)*ch);ctx.globalAlpha=1;}}
 if(t>nextShooting){nextShooting=t+2.2+hash(Math.floor(t),9)*2.3;streaks.push({x:(hash(t,1)-.5)*1.4,y:-.4,vx:hash(t,2)>.5?.7:-.7,vy:.5,age:0,life:1.2,tail:.18});}
 if(t>34.9&&!comet){comet=true;streaks.push({x:-.95,y:-.28,vx:.03,vy:.008,age:0,life:70,tail:.22});}
 for(const s of streaks){s.age+=dt;let headx=s.x+s.vx*s.age,heady=s.y+s.vy*s.age,vel=Math.hypot(s.vx,s.vy),dx=s.vx/vel,dy=s.vy/vel;for(let k=0;k<18;k++){const f=k/18,x=headx-dx*s.tail*f,y=heady-dy*s.tail*f,c=Math.floor((W/2+x*H)/cw),r=Math.floor((H/2+y*H)/ch);if(c<0||c>=cols||r<0||r>=rows||!allowed[r*cols+c])continue;ctx.globalAlpha=Math.max(0,(1-f)*Math.sin(Math.PI*clamp(s.age/s.life)));ctx.fillStyle='#d4e8ff';ctx.fillText(k===0?'@':k<7?'/':'.',(c+.5)*cw,(r+.5)*ch);}}ctx.globalAlpha=1;streaks=streaks.filter(s=>s.age<s.life);
 if(z<2.6){ctx.strokeStyle='#392319';ctx.lineWidth=Math.max(.7,ch*.08);for(let k=0;k<44;k++){let s=-.92+1.84*k/43,u=s*.78,edge=lid(u,ou),v=edge[0]-.055*s,len=(.07+.05*Math.sqrt(Math.max(0,1-s*s)))*z*H;let x=W/2+u*z*H,y=H/2+v*z*H;if(x<0||x>W||y<0||y>H)continue;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+s*len*.35,y-len*(1-.5*(1-ou)));ctx.stroke();}}
 }
function tick(now){if(!paused){const t=(now-start)/1000,dt=Math.min(.1,Math.max(0,t-last));last=t;render(t,dt)}requestAnimationFrame(tick)}requestAnimationFrame(tick);
