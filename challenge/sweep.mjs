import {evaluate,shifts,tolerance} from "../site/sampling.mjs";

const csv=process.argv[2]==="--rows";
if (process.argv.length>(csv?3:2)) throw Error("Use --rows or no arguments.");
const groups=[
  ["integer",Array.from({length:128},(_,i)=>i+1)],
  ["resonance",Array.from({length:60},(_,i)=>(i+5)*32)],
  ["half",Array.from({length:32},(_,i)=>i+0.5)]
];
const summary={inputs:0,evaluationsPerDecision:64,tolerance,groups:{}};
if(csv) console.log("group,k,phase,amplitude,method,estimate,witness,exact,accept,accurate");
for(const [name,frequencies] of groups) {
  const counts=Object.fromEntries(Object.keys(shifts).map(m=>[m,{accurate:0,inaccurate:0,falseAccept:0,falseReject:0}]));
  for(const k of frequencies) for(const amplitude of [0.1,1]) for(let i=0;i<16;i++){
    const phase=i/16;
    summary.inputs++;
    for(const method of Object.keys(shifts)){
      const result=evaluate({k,phase,amplitude},method);
      const c=counts[method];
      c[result.accurate?"accurate":"inaccurate"]++;
      if(result.accept && !result.accurate) c.falseAccept++;
      if(!result.accept && result.accurate) c.falseReject++;
      if(csv) console.log([name,k,phase,amplitude,method,result.estimate,result.witness,result.exact,+result.accept,+result.accurate].join(","));
    }
  }
  summary.groups[name]=counts;
}
if(!csv) console.log(JSON.stringify(summary,null,2));
