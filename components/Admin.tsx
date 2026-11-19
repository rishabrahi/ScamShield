'use client'
import Link from 'next/link'
export default function Admin(){
 return <section className="panel"><p className="eyebrow">Assessment administration</p><h1>Lab management</h1><p>Design labs, assign training, review submissions and compare learner progress.</p><Link href="/simulations/?view=studio">Open lab studio →</Link></section>
}
