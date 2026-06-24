import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api';
import { currentMonth } from '../lib';
import { Badge, Card, Input } from '../components/ui';
export default function Insights(){ const [month,setMonth]=useState(currentMonth()); const {data=[]}=useQuery({queryKey:['insights',month], queryFn:()=>api.insights(month)}); return <div className="grid gap-5"><Card><Input className="max-w-44" type="month" value={month} onChange={e=>setMonth(e.target.value)}/></Card><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{data.map((i:any)=><Card key={i.title}><Badge tone={i.severity==='warning'?'warn':i.severity==='positive'?'good':'default'}>{i.severity}</Badge><h3 className="mt-4 text-xl font-black">{i.title}</h3><p className="mt-2 text-sm leading-6 text-white/55">{i.body}</p></Card>)}</div></div> }
