'use client'
import {useState,FormEvent} from 'react'
import {auth} from '@/lib/auth'
import {useLanguage} from './I18n'
import Preferences from './Preferences'
import Link from 'next/link'
export default function Login({register}:{register:boolean}){
 const {t}=useLanguage(),[show,setShow]=useState(false),[busy,setBusy]=useState(false),[status,setStatus]=useState('')
 const dashboard=()=>{sessionStorage.removeItem('ssGuest');location.assign('/dashboard/')}
 async function submit(e:FormEvent<HTMLFormElement>){
  e.preventDefault()
  if(!auth){setStatus('Account sign-in is unavailable here. Continue as a guest.');return}
  setBusy(true)
  try{const data=new FormData(e.currentTarget),email=String(data.get('email')),password=String(data.get('password'))
   const result=register?await auth.auth.signUp({email,password,options:{emailRedirectTo:location.origin+'/dashboard/',data:{full_name:data.get('name'),department:data.get('department')}}}):await auth.auth.signInWithPassword({email,password})
   if(result.error)throw result.error
   if(result.data.session)dashboard();else setStatus('Check your email to confirm your account.')
  }catch{setStatus('Please try again.')}finally{setBusy(false)}
 }
 return <section className="auth panel"><Preferences/><p className="eyebrow">ScamShield / {t('Account access')}</p><h1>{t(register?'Create your account':'Welcome back')}</h1><form onSubmit={submit}>{register&&<><label>{t('Full name')}<input name="name" autoComplete="name" required/></label><label>{t('Department')}<input name="department"/></label></>}<label>{t('Email')}<input type="email" name="email" autoComplete="email" required/></label><label>{t('Password')}<input type={show?'text':'password'} name="password" autoComplete={register?'new-password':'current-password'} required minLength={register?8:1}/></label><button type="button" className="outline" onClick={()=>setShow(!show)}>{t(show?'Hide password':'Show password')}</button><button disabled={busy}>{t(busy?'Please wait…':register?'Register':'Sign in')}</button></form>
 <div className="actions"><button className="outline" onClick={async()=>{if(!auth){setStatus('Account sign-in is unavailable here. Continue as a guest.');return}sessionStorage.removeItem('ssGuest');try{const {error}=await auth.auth.signInWithOAuth({provider:'google',options:{redirectTo:location.origin+'/dashboard/'}});if(error)throw error}catch{setStatus('Please try again.')}}}>{t('Continue with Google')}</button><button onClick={()=>{sessionStorage.ssGuest='yes';location.assign('/dashboard/')}}>{t('Continue as guest')}</button></div><p role="status">{t(status)}</p><Link href={register?'/login/':'/register/'}>{t(register?'Sign in':'Create account')}</Link></section>
}
