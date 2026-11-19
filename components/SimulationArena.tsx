'use client'
import {useEffect,useState,type ReactNode,type FormEvent} from 'react'
import Link from 'next/link'
import {auth} from '@/lib/auth'
import {ScenarioShelf} from './SimulationArtifact'
import SimulationArtifact from '@/components/SimulationArtifact'
import './arena.css'

type Task={category:string,prompt:string,options:string[]}
type Detail={category:string,prompt:string,decision:string,safe:string,ok:boolean}
type RecordRow={id:number,lab:number,uid:string,title:string,due:number|null,start:number|null,submitted:number|null,released:number,passmark:number,score?:number,elapsed?:number,details?:Detail[],feedback?:string}
type Member={id:string,email:string,batch:string,active:number,instructor:number}
type State={uid:string,admin:boolean,owner:boolean,labs:{id:number,title:string,difficulty:string,practice:number}[],records:RecordRow[],members:Member[],notices:{message:string}[]}
type Call=(path:string,body?:unknown)=>Promise<any>
const endpoint=(process.env.NEXT_PUBLIC_API_URL||'/api/v1').replace(/\/$/,'')+'/arena'
const date=(seconds:number)=>new Date(seconds*1000).toLocaleDateString()
async function api(path:string,body?:unknown){
 const session=auth&&(await auth.auth.getSession()).data.session
 if(!session||sessionStorage.ssGuest==='yes')throw Error('Sign in with your learner account to access assessments.')
 const res=await fetch(endpoint+path,{method:body===undefined?'GET':'POST',cache:'no-store',headers:{Authorization:'Bearer '+session.access_token,'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)})
 if(!res.ok){const error=await res.json().catch(()=>({}));throw Error(typeof error.detail==='string'?error.detail:'The request could not be completed. Check your entries.')}
 return res.json()
}
function Analytics({records}:{records:RecordRow[]}){
 const [period,setPeriod]=useState('week')
 const scored=records.filter(r=>r.score!==undefined),done=records.filter(r=>r.submitted)
 const details=scored.flatMap(r=>r.details||[]),pct=(n:number,d:number)=>d?Math.round(n/d*100):0
 const groups=new Map<string,Detail[]>()
 details.forEach(d=>groups.set(d.category,[...(groups.get(d.category)||[]),d]))
 const ranks=[...groups].sort((a,b)=>pct(b[1].filter(d=>d.ok).length,b[1].length)-pct(a[1].filter(d=>d.ok).length,a[1].length))
 const trend=new Map<string,number[]>()
 scored.slice().sort((a,b)=>a.submitted!-b.submitted!).forEach(r=>{const dt=new Date(r.submitted!*1000);if(period==='week')dt.setUTCDate(dt.getUTCDate()-(dt.getUTCDay()+6)%7);const key=dt.toISOString().slice(0,period==='week'?10:7);trend.set(key,[...(trend.get(key)||[]),r.score!])})
 const bar=(label:string,value:number)=><div className="meter" key={label}><span>{label}</span><progress max="100" value={value}/><b>{value}%</b></div>
 return <section><h2>Performance profile</h2>{bar('Completion',pct(done.length,records.length))}{scored.length>0?<>{bar('Average score',Math.round(scored.reduce((s,r)=>s+r.score!,0)/scored.length))}{bar('Decision accuracy',pct(details.filter(d=>d.ok).length,details.length))}{bar('Error rate',pct(details.filter(d=>!d.ok).length,details.length))}<h3>Category performance</h3>{ranks.map(([k,v])=>bar(k,pct(v.filter(d=>d.ok).length,v.length)))}<p>Strongest category · {ranks[0]?.[0]}</p>{ranks.some(([,v])=>v.some(d=>!d.ok))&&<p>Focus next · {ranks.at(-1)?.[0]}</p>}<h3>Score history</h3>{scored.slice().reverse().map(r=>bar(r.title+' #'+r.id,Math.round(r.score!)))}<label>Trend interval<select value={period} onChange={e=>setPeriod(e.target.value)}><option value="week">Weekly</option><option value="month">Monthly</option></select></label>{[...trend].map(([k,v])=>bar(k,Math.round(v.reduce((s,n)=>s+n,0)/v.length)))}<p>Achievement · {scored.filter(r=>r.score!>=r.passmark).length} assessments passed</p></>:<p>Released scores appear here after assessment.</p>}</section>
}
const form=(e:FormEvent<HTMLFormElement>)=>{e.preventDefault();return Object.fromEntries(new FormData(e.currentTarget)) as Record<string,string>}
function Controls({state,run}:{state:State,run:Call}){
 const [definition,setDefinition]=useState<{id:number,title:string,difficulty:string,passmark:number,release:string,tasks:(Task&{correct:number,points:number})[]}|null>(null)
 const [editError,setEditError]=useState('')
 const [count,setCount]=useState(1)
 async function edit(id:number){
  try{
   const lab=id?await api('/labs/'+id):null
   setDefinition(lab);setCount(lab?.tasks.length||1);setEditError('')
  }catch(e){setEditError((e as Error).message)}
 }
 return <><section><h2>Lab design</h2><label>Choose a lab<select value={definition?.id||0} onChange={e=>edit(+e.target.value)}><option value={0}>Create a new lab</option>{state.labs.filter(l=>!l.practice).map(l=><option key={l.id} value={l.id}>{l.title}</option>)}</select></label>
 {editError&&<p role="alert">{editError}</p>}
 <form key={definition?.id||0} onSubmit={e=>{
  const submitter=(e.nativeEvent as SubmitEvent).submitter as HTMLButtonElement|null
  const f=form(e)
  const tasks=Array.from({length:count},(_,i)=>({
   category:f['category'+i],prompt:f['prompt'+i],options:[f['a'+i],f['b'+i],...(definition?.tasks[i]?.options.slice(2)||[])],
   correct:+f['correct'+i],points:+f['points'+i]
  }))
  void run(definition&&submitter?.value!=='copy'?'/labs/'+definition.id:'/labs',{title:f.title,difficulty:f.difficulty,passmark:+f.passmark,release:f.release,tasks})
 }}>
 <label>Lab title<input name="title" defaultValue={definition?.title} required maxLength={120}/></label>
 <label>Difficulty<select name="difficulty" defaultValue={definition?.difficulty}>{['Foundation','Intermediate','Advanced'].map(s=><option key={s}>{s}</option>)}</select></label>
 <label>Passing percentage<input type="number" name="passmark" min="0" max="100" defaultValue={definition?.passmark??70} required/></label>
 <label>Release results<select name="release" defaultValue={definition?.release}><option value="immediate">Immediately</option><option value="manual">After review</option></select></label>
 {Array.from({length:count},(_,i)=>{
  const task=definition?.tasks[i]
  return <fieldset key={i}><legend>Task {i+1}</legend>{['category','prompt','a','b'].map((k,j)=><label key={k}>{['Category','Educational scenario','Choice A','Choice B'][j]}<input name={k+i} defaultValue={[task?.category,task?.prompt,task?.options[0],task?.options[1]][j]} required/></label>)}<label>Safe choice<select name={'correct'+i} defaultValue={task?.correct??0}>{(task?.options||['A','B']).map((_,j)=><option key={j} value={j}>{String.fromCharCode(65+j)}</option>)}</select></label><label>Points<input name={'points'+i} type="number" min="1" max="100" defaultValue={task?.points??1} required/></label></fieldset>
 })}
 <button type="button" disabled={count>=50} onClick={()=>setCount(count+1)}>Add task</button>{count>1&&<button type="button" onClick={()=>setCount(count-1)}>Remove last task</button>}
 <button>{definition?'Save changes':'Create lab'}</button>{definition&&<button value="copy">Save as new version</button>}</form></section>
 <section><h2>Assign an assessment</h2><form onSubmit={e=>{const f=form(e);void run('/assign',{lab:+f.lab,uid:f.uid,batch:f.batch,due:Math.floor(new Date(f.due).getTime()/1000)})}}><label>Lab<select name="lab">{state.labs.map(l=><option key={l.id} value={l.id}>{l.title} · {l.difficulty}</option>)}</select></label><label>Learner<select name="uid"><option value="">Assign by batch</option>{state.members.map(m=><option key={m.id} value={m.id}>{m.email}</option>)}</select></label><label>Batch (for batch assignments)<input name="batch"/></label><label>Deadline<input type="datetime-local" name="due" required/></label><button>Assign lab</button></form></section>
 {state.owner&&<section><h2>Training access</h2>{state.members.map(m=><form key={m.id} onSubmit={e=>{const f=form(e);void run('/members/'+m.id,{batch:f.batch,active:!!f.active})}}><strong>{m.email}</strong><label>Batch<input defaultValue={m.batch} name="batch"/></label><label><input type="checkbox" name="active" defaultChecked={!!m.active}/> Active learner</label><button>Save access</button><button type="button" onClick={()=>run('/instructors/'+m.id,{instructor:!m.instructor})}>{m.instructor?'Remove instructor role':'Grant instructor role'}</button></form>)}</section>}</>
}
export default function SimulationArena({guest,children}:{guest:boolean,children:ReactNode}){
 const [step,go]=useState(0)
 const [state,set]=useState<State|null>(null),[msg,status]=useState(''),[tab,choose]=useState('Scenario library'),[uid,select]=useState(''),[attempt,open]=useState<{id:number,tasks:Task[]}|null>(null),[answers,answer]=useState<number[]>([]),[busy,lock]=useState(false)
 async function refresh(){set(await api(''))}
 useEffect(()=>{if(guest)return;let active=true;if(new URLSearchParams(location.search).get('view')==='studio')choose('Lab studio');const load=()=>api('').then(v=>{if(active){set(v);if(!v.admin)choose(old=>['Review','Lab studio'].includes(old)?'Scenario library':old)}}).catch(e=>{if(active){set(null);status(e.message)}});load();const id=setInterval(load,30000);return()=>{active=false;clearInterval(id)}},[guest])
 async function act(fn:()=>Promise<void>){if(busy)return;lock(true);status('');try{await fn()}catch(e){status((e as Error).message)}finally{lock(false)}}
 const run:Call=(p,b)=>act(async()=>{const result=await api(p,b);await refresh();status('assigned' in result?result.assigned+' new assignments created.':'Saved.')})
 const start=(id?:number,lab?:number)=>act(async()=>{const aid=id??(await api(lab?'/practice/'+lab:'/practice',{})).id;const tasks=await api('/attempt/'+aid,{});const draft:number[]=await api('/draft/'+aid);answer(draft.length?draft:Array(tasks.length).fill(-1));go(Math.max(0,draft.indexOf(-1)));open({id:aid,tasks});await refresh()})
 const records=state?.records.filter(r=>tab==='Review'?(uid===''||r.uid===uid):r.uid===state.uid)||[]
 const own=state?.records.filter(r=>r.uid===state.uid)||[]
 const launch=(lab:number)=>{
  const previous=own.find(r=>r.lab===lab)
  if(previous?.submitted){choose('Assignments');open(null);setTimeout(()=>document.getElementById('assessment-'+previous.id)?.scrollIntoView({block:'center'}),50);return}
  void start(previous?.id,lab)
 }
 const tabs=['Scenario library','Practice inbox',...(state?['Assignments','Profile']:[]),...(state?.admin?['Lab studio','Review']:[])]
 return <div className="simulation-hub"><header className="sim-heading"><div><p className="eyebrow">ScamShield / Educational simulations</p><h1>Simulation Arena</h1><p>Inspect the evidence, choose a safe action, and review your decisions.</p></div></header>
 <nav className="sim-switch" aria-label="Simulation tools">{tabs.map(s=><button key={s} aria-pressed={s===tab} onClick={()=>{choose(s);open(null);status('')}}>{s}</button>)}</nav>
 {msg&&<p role="status" className="sim-message">{msg}</p>}
 {tab==='Practice inbox'?children:<div className="arena">{tab==='Scenario library'&&!attempt?<><ScenarioShelf labs={state?.labs||[]} records={own} launch={launch} busy={busy}/>{guest?<p><Link href="/login/">Sign in</Link> to save assessed decisions and access assigned labs. Guest practice is available in the Practice inbox.</p>:!state?<p>Connecting to your assessment workspace…</p>:null}</>:!state?<Link href="/login/">Go to login</Link>:<><fieldset disabled={busy} className="body">{attempt?<section><h2>Assessment in progress</h2><p>{answers.filter(i=>i>=0).length} of {answers.length} decisions recorded</p><form onSubmit={e=>{e.preventDefault();if(answers.includes(-1))return;void act(async()=>{await api('/submit/'+attempt.id,{answers});open(null);choose('Assignments');await refresh();status('Assessment submitted.')})}}>{attempt.tasks.map((t,i)=>i===step&&<fieldset key={i}><legend>{i+1} · {t.category}</legend>{state.labs.some(l=>l.id===state.records.find(r=>r.id===attempt.id)?.lab&&l.practice>0)&&<SimulationArtifact category={t.category}/>}<p>{t.prompt}</p>{t.options.map((v,j)=><label key={j}><input type="radio" name={'t'+i} required checked={answers[i]===j} onChange={()=>answer(answers.map((n,k)=>i===k?j:n))}/>{v}</label>)}</fieldset>)}<div>{step>0&&<button type="button" onClick={()=>go(step-1)}>Previous</button>}{step<answers.length-1?<button type="button" disabled={answers[step]<0} onClick={()=>act(async()=>{await api('/draft/'+attempt.id,{answers});go(step+1)})}>Next decision</button>:<button disabled={answers.includes(-1)}>Submit assessment</button>}</div></form></section>:tab==='Lab studio'&&state.admin?<Controls state={state} run={run}/>:tab==='Profile'?<Analytics records={records}/>:<>{tab==='Assignments'?<section><h2>Practice lab</h2><p>Ten decisions across messages, banking alerts, QR codes and more.</p><button onClick={()=>choose('Scenario library')}>Browse simulations</button><h3>Notifications</h3>{state.notices.length?state.notices.map((n,i)=><p key={i}>{n.message}</p>):<p>No notifications yet.</p>}</section>:<section><label>Review learners<select value={uid} onChange={e=>select(e.target.value)}><option value="">All learners</option>{state.members.map(m=><option key={m.id} value={m.id}>{m.email}</option>)}</select></label><Analytics records={records}/></section>}<h2>{tab==='Review'?'Assignment tracking':'My assignments and results'}</h2>{!records.length&&<p>No assignments yet.</p>}{records.map(r=><section id={'assessment-'+r.id} key={r.id}><h3>{r.title}</h3>{tab==='Review'&&<p>{state.members.find(m=>m.id===r.uid)?.email}</p>}<p>{r.due?'Due '+new Date(r.due*1000).toLocaleString():'Self-paced'} · {r.submitted?'Submitted '+date(r.submitted):r.start?'In progress':'Assigned'}</p>{r.submitted?r.score===undefined?<p>Awaiting result release</p>:<><strong>{r.score}% · {r.score>=r.passmark?'Passed':'Practice recommended'}</strong><p>{r.elapsed}s elapsed · {r.details?.filter(d=>!d.ok).length} mistakes</p><details><summary>Review safety actions</summary>{r.details?.map((d,i)=><p key={i}><b>{d.category}</b> · {d.decision}<br/>Safe action · {d.safe}</p>)}</details>{r.feedback&&<p>Instructor feedback · {r.feedback}</p>}</>:tab==='Assignments'&&<button disabled={!!r.due&&r.due*1000<Date.now()} onClick={()=>start(r.id)}>Open assessment</button>}{tab==='Review'&&!r.submitted&&<form onSubmit={e=>{const f=form(e);void run('/deadline/'+r.id,{due:Math.floor(new Date(f.deadline).getTime()/1000)})}}><label>New deadline<input name="deadline" type="datetime-local" required/></label><button>Update deadline</button></form>}{tab==='Review'&&!!r.submitted&&<form onSubmit={e=>{const f=form(e);void run('/review/'+r.id,{feedback:f.feedback,released:!!f.released})}}><label>Feedback<textarea name="feedback" defaultValue={r.feedback}/></label><label><input type="checkbox" name="released" defaultChecked={!!r.released}/> Release to learner</label><button>Save review</button></form>}</section>)}</>}</fieldset></>}</div>}</div>
}
