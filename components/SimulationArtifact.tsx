import {Mail,MessageSquare,Phone,Shield,Globe,FileText,QrCode,KeyRound,Wallet,Bell} from 'lucide-react'

const artifacts=[
 ['SMS phishing','Messages','Northstar Parcel','Delivery paused','Parcel NS-104 · Unrequested handling charge','Track parcel',MessageSquare],
 ['WhatsApp scam','Chat','Unknown number','I changed my number','Can you send the money now? I cannot take a call.','Reply',MessageSquare],
 ['Banking notification','Payment notification','Riverstone Bank','Approve transaction?','Pending payment · 850 demo credits','Approve payment',Bell],
 ['Fake KYC','Identity verification','Willow Wallet','Identity update required','An agent is requesting your one-time verification code.','Continue verification',Wallet],
 ['Email phishing','Inbox','Lumen Benefits','Your refund is ready','Unexpected refund notice · Sender identity unverified','Claim refund',Mail],
 ['Malicious website','Browser','Prize Garden','You have a reward','Permission requested · Notifications and software installation','Install reward app',Globe],
 ['Password security','Account setup','Aster Club','Create your password','Your email and club memberships are separate accounts.','Password setup',KeyRound],
 ['Social engineering','Incoming call','Elm IT support','Unexpected authentication request','The caller asks you to approve a prompt you did not initiate.','MFA approval requested',Phone],
 ['QR phishing','Parking meter','Meadow Parking','Scan to pay','A second payment sticker covers the operator’s original label.','Payment code',QrCode],
 ['Suspicious attachment','Attachment preview','Fern Office','Unexpected invoice','Invoice-demo.docm · Document requests macros','Attachment locked',FileText],
] as const
export default function SimulationArtifact({category}:{category:string}){
 const item=artifacts.find(a=>a[0]===category)
 if(!item)return null
 const [,channel,sender,title,body,action,Icon]=item
 return <aside className="artifact"><small><Shield size={14}/> Fictional {channel.toLowerCase()} preview</small><div><Icon size={22}/><strong>{sender}</strong></div><h3>{title}</h3><p>{body}</p><span>{action}</span></aside>
}

type ScenarioShelfProps={
 labs:{id:number,title:string,practice:number}[]
 records:{lab:number,submitted:number|null,start:number|null}[]
 launch:(id:number)=>void
 busy:boolean
}
export function ScenarioShelf({labs,records,launch,busy}:ScenarioShelfProps){
 const full=labs.find(l=>l.practice===1)
 function control(id:number){
  const record=records.find(r=>r.lab===id)
  return <button disabled={busy} onClick={()=>launch(id)}>{record?.submitted?'View submission':record?.start?'Resume assessment':'Start assessment'} →</button>
 }
 return <><div className="field-banner"><div><small>Comprehensive assessment</small><h2>Field assessment</h2><p>Work through all ten scenarios in one scored lab.</p></div>{full&&control(full.id)}</div>
 <h2>Practice by scenario</h2><div className="scenario-shelf">{artifacts.map(([category,channel,sender,title,body,,Icon])=>{
  const lab=labs.find(l=>l.practice===2&&l.title===category)
  return <article key={category}><div className="scenario-channel"><Icon size={20}/><small>{channel}</small></div><h3>{category}</h3><p>{sender} · {title}</p><details><summary>Inspect scenario</summary><p>{body}</p></details>{lab&&control(lab.id)}</article>
 })}</div></>
}
