'use client'
import {useEffect} from 'react'
import Link from 'next/link'

export default function ArenaBookmark(){
 useEffect(()=>{location.replace('/simulations/'+location.search+location.hash)},[])
 return <Link href="/simulations/">Open Simulations</Link>
}
