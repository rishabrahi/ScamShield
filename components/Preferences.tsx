'use client'
import {useState,useEffect} from 'react'
import {Moon,Sun,Languages} from 'lucide-react'
import {useLanguage} from './I18n'
const names={en:'English',hi:'हिन्दी',bn:'বাংলা',mr:'मराठी',ta:'தமிழ்',te:'తెలుగు',gu:'ગુજરાતી',kn:'ಕನ್ನಡ',ml:'മലയാളം',pa:'ਪੰਜਾਬੀ',ur:'اردو',es:'Español'}
export default function Preferences(){const {lang,t,choose}=useLanguage();const [dark,set]=useState(false)
 useEffect(()=>{const value=localStorage.pgTheme==='dark';set(value);document.documentElement.dataset.theme=value?'dark':'light'},[])
 return <div className="prefs"><Languages size={16}/><select aria-label={t('Language')} value={lang} onChange={e=>choose(e.target.value)}>{Object.entries(names).map(([code,name])=><option value={code} key={code}>{name}</option>)}</select><button aria-label={t(dark?'Switch to light theme':'Switch to dark theme')} onClick={()=>{set(!dark);localStorage.pgTheme=dark?'light':'dark';document.documentElement.dataset.theme=localStorage.pgTheme}}>{dark?<Sun size={17}/>:<Moon size={17}/>}</button></div>}
