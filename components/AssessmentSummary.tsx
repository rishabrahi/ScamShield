'use client'
import Link from 'next/link'
import {useEffect,useState} from 'react'
import {auth} from '@/lib/auth'

type Assignment={uid:string,due:number|null,submitted:number|null,released:number,score?:number,title:string}
export default function AssessmentSummary(){
 const [data,setData]=useState<Assignment[]|null>(null)
 useEffect(()=>{
  if(!auth||sessionStorage.ssGuest==='yes')return
  const client=auth
  let mounted=true
  async function load(){
   try{
    const token=(await client.auth.getSession()).data.session?.access_token
    if(!token)return
    const base=(process.env.NEXT_PUBLIC_API_URL||'/api/v1').replace(/\/$/,'')
    const response=await fetch(base+'/arena',{headers:{Authorization:'Bearer '+token},cache:'no-store'})
    if(!response.ok)return
    const dashboard=await response.json()
    if(mounted)setData(dashboard.records.filter((r:Assignment)=>r.uid===dashboard.uid))
   }catch{if(mounted)setData(null)}
  }
  load()
  const timer=setInterval(load,30000)
  return()=>{mounted=false;clearInterval(timer)}
 },[])
 if(!data)return null
 const pending=data.filter(r=>!r.submitted)
 const next=pending.filter(r=>r.due&&r.due*1000>Date.now()).sort((a,b)=>a.due!-b.due!)[0]
 const result=data.filter(r=>r.released&&r.submitted).sort((a,b)=>b.submitted!-a.submitted!)[0]
 return <section className="panel"><h2>Assigned assessments</h2><p>{pending.length} outstanding · {data.length-pending.length} submitted</p>{next&&<p>Next deadline · {next.title} · {new Date(next.due!*1000).toLocaleString()}</p>}{result&&<p>Latest result · {result.title} · {result.score}%</p>}<Link href="/simulations/">Open Simulation Arena →</Link></section>
}
