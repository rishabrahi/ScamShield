import {auth} from './auth'
import type {Entry} from './data'
const base = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/,'')
async function request(path:string,entry?:Entry){
 const token=(await auth!.auth.getSession()).data.session?.access_token
 if(!token)throw new Error('Sign in required')
 const res=await fetch(base+path,{method:entry?'POST':'GET',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:entry?JSON.stringify(entry):undefined})
 if(!res.ok)throw new Error('Progress unavailable')
 return res.json()
}
export async function readHistory():Promise<Entry[]>{
 if(base)return request('/responses/history')
 const {data,error}=await auth!.from('scamshield_attempts').select('lesson,decision,time_ms').order('time_ms')
 if(error)throw error
 return data.map(row=>({id:row.lesson,decision:row.decision,time:row.time_ms}))
}
export async function saveAttempt(entry:Entry){
 if(base){await request('/responses/',entry);return}
 const {error}=await auth!.from('scamshield_attempts').insert({lesson:entry.id,decision:entry.decision,time_ms:entry.time})
 if(error)throw error
}
