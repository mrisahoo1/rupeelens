import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Drama, Lightbulb, Wand2 } from 'lucide-react';
import { api } from '../api';
import { currentMonth } from '../lib';
import { Badge, Card, Input } from '../components/ui';

const toneClass:any = { warning:'border-saffronx/25 bg-saffronx/10', positive:'border-emeraldx/25 bg-emeraldx/10', info:'border-white/10 bg-white/7' };

export default function Insights(){
  const [month,setMonth]=useState(currentMonth());
  const {data=[]}=useQuery({queryKey:['insights',month], queryFn:()=>api.insights(month)});
  return <div className="space-y-7"><Card className="p-7"><div className="flex flex-wrap items-end justify-between gap-4"><div><Badge tone="good">Insight Arcade</Badge><h2 className="mt-4 text-3xl font-black">Small money stories, sharper decisions.</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-white/50">These are deterministic insights from your normalized transactions. Optional Ollama can rewrite answers in Budget Lab, but these cards stay auditable.</p></div><Input className="max-w-44" type="month" value={month} onChange={e=>setMonth(e.target.value)}/></div></Card><div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{data.map((i:any,idx:number)=><motion.div key={i.title} initial={{opacity:0,y:16}} animate={{opacity:1,y:0}} transition={{delay:idx*.04}}><Card className={`min-h-60 p-6 ${toneClass[i.severity] || toneClass.info}`}><div className="mb-7 flex items-start justify-between"><div className="text-4xl">{i.emoji || '✨'}</div><Badge tone={i.severity==='warning'?'warn':i.severity==='positive'?'good':'default'}>{i.severity}</Badge></div><div className="text-sm uppercase tracking-[.18em] text-white/35">{i.metric || 'signal'}</div><h3 className="mt-3 text-2xl font-black leading-tight">{i.title}</h3><p className="mt-3 text-sm leading-6 text-white/58">{i.body}</p><div className="mt-5 flex items-center gap-2 text-xs text-white/35"><Wand2 size={14}/> Evidence-led, no invented transactions</div></Card></motion.div>)}</div>{!data.length && <Card className="p-10 text-center"><Drama className="mx-auto mb-4 text-emeraldx"/><h3 className="text-2xl font-black">No insights yet</h3><p className="mt-2 text-white/50">Upload or seed transactions and this page will become more interesting.</p></Card>}</div>
}
