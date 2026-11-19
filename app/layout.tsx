import I18n from '@/components/I18n'
import localFont from 'next/font/local'
import './globals.css'
const sans=localFont({src:'./dm-sans-latin-wght-normal.woff2',variable:'--sans'})
const serif=localFont({src:[{path:'./newsreader-latin-wght-normal.woff2',style:'normal'},{path:'./newsreader-latin-wght-italic.woff2',style:'italic'}],variable:'--serif'})
export const metadata={title:'ScamShield | Awareness studio',description:'Practice recognizing suspicious messages in a safe simulated inbox.'}
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en" className={sans.variable+' '+serif.variable}><body><I18n>{children}</I18n></body></html>}
