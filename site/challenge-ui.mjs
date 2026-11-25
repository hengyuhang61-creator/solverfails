import {cases,evaluate,regression,shifts,value} from "./sampling.mjs";
const $=id=>document.getElementById(id);
const q=new URLSearchParams(location.search);
const requested=Number(q.get("case")??1);
let index=Number.isInteger(requested)&&requested>=1&&requested<=cases.length?requested-1:0;
let method=q.get("method")==="staggered"?"staggered":"interleaved";
let choice=null;

function plot(input,revealed){
  const canvas=$("curve"), w=canvas.clientWidth, h=canvas.clientHeight, ratio=devicePixelRatio||1;
  canvas.width=Math.round(w*ratio);canvas.height=Math.round(h*ratio);
  const ctx=canvas.getContext("2d");ctx.scale(ratio,ratio);
  const x=t=>18+t*(w-36), y=v=>h-18-v*(h-36)/2;
  ctx.lineWidth=1;ctx.strokeStyle="#504963";
  for(const level of [0,1,2]){
    ctx.beginPath();ctx.moveTo(x(0),y(level));ctx.lineTo(x(1),y(level));ctx.stroke();
    ctx.fillStyle="#c0b9d1";ctx.fillText(level,3,y(level)+4);
  }
  if(revealed){
    ctx.strokeStyle="#a79abb";ctx.lineWidth=1.8;ctx.beginPath();
    for(let j=0;j<=1024;j++){const t=j/1024; const v=value(input,t/32);
      if(j===0)ctx.moveTo(x(t),y(v));else ctx.lineTo(x(t),y(v));}
    ctx.stroke();
  }
  for(const t of [0,1,shifts[method]]){
    ctx.fillStyle=t===0||t===1?"#daf391":"#ddbfff";ctx.beginPath();
    ctx.arc(x(t),y(value(input,t/32)),5,0,Math.PI*2);ctx.fill();
  }
}
function render(){
  const input=cases[index], result=evaluate(input,method), revealed=choice!==null;
  $("estimate").textContent=result.estimate.toFixed(4);$("witness").textContent=result.witness.toFixed(4);
  $("signal").textContent=result.accept?"PASS · the two sample means agree":"FAIL · the two sample means disagree";
  $("signal").dataset.pass=result.accept;
  $("votes").hidden=revealed;$("after").hidden=!revealed;$("curve-key").hidden=!revealed;
  $("method").value=method;
  $("formula").textContent=revealed?`f(x) = 1 + ${input.amplitude} cos(2π(${input.k}x + ${input.phase}))`:"The curve is hidden until you decide.";
  $("feedback").textContent=revealed?(choice===result.accurate?"Your decision matches the exact answer.":"The exact answer reverses your decision."):"";
  $("truth").textContent=`Exact area ${result.exact.toFixed(5)} · estimate error ${Math.abs(result.estimate-result.exact).toFixed(5)}.`;
  $("audit").textContent=result.accept===result.accurate?(result.accept?"This rule accepts an accurate estimate.":"This rule rejects an inaccurate estimate."):(result.accept?"False acceptance. The samples agree on a wrong answer.":"False rejection. The estimate is accurate despite the disagreement.");
  const link=new URL(location.href);link.searchParams.set("case",index+1);link.searchParams.set("method",method);
  $("share").href=link;history.replaceState(null,"",link);plot(input,revealed);
}
$("ship").onclick=()=>{choice=true;render();};$("hold").onclick=()=>{choice=false;render();};
$("method").onchange=()=>{method=$("method").value;render();};
$("next").onclick=()=>{index=(index+1)%cases.length;method="interleaved";choice=null;render();$("ship").focus();};
$("export").onclick=()=>{
  const blob=new Blob([regression(cases[index],method)],{type:"text/x-python"});
  const url=URL.createObjectURL(blob), a=document.createElement("a");a.href=url;a.download=`solverfails-case-${index+1}-${method}.py`;
  a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};
new ResizeObserver(()=>plot(cases[index],choice!==null)).observe($("curve"));
render();
