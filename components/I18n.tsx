'use client'
import {createContext,useContext,useEffect,useState,ReactNode} from 'react'
const supported=['en','hi','bn','mr','ta','te','gu','kn','ml','pa','ur','es']
type Dict=Record<string,string>
const Context=createContext({lang:'en',t:(value:string)=>value,choose:(value:string)=>{}})
export const useLanguage=()=>useContext(Context)
export default function I18n({children}:{children:ReactNode}){
 const [lang,set]=useState('en'),[dict,update]=useState<Dict>({})
 useEffect(()=>{const value=localStorage.getItem('pgLang');if(value&&supported.includes(value))set(value)},[])
 useEffect(()=>{let active=true
 if(lang==='en')update({})
 else import('../lib/locales/'+lang+'.json').then(module=>{if(active)update(module.default)})
 document.documentElement.lang=lang
 document.documentElement.dir=lang==='ur'?'rtl':'ltr'
 return ()=>{active=false}
 },[lang])
 return <Context.Provider value={{lang,t:value=>dict[value]??value,choose:value=>{localStorage.setItem('pgLang',value);set(value)}}}>{children}</Context.Provider>
}
