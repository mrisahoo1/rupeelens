import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Bot, Gauge, PiggyBank, Send, Sparkles, Target } from 'lucide-react';
import { api } from '../api';
import { currentMonth, rupee } from '../lib';
import { Badge, Button, Card, Input, Select } from '../components/ui';

const categories=['Overall','Food & Dining','Groceries','Transport','Shopping','Subscriptions','Utilities','Travel','Fuel','Entertainment','Health & Pharmacy'];
const prompts=['How is my budget doing?','Where should I cut first?','Explain my UPI leakage','Which category deserves a budget?'];

export default function Budgets(){
  const qc=useQueryClient();
  const [month,setMonth]=useState(currentMonth());
  const [category,setCategory]=useState('Overall');
  const [amount,setAmount]=useState('');
  const [question,setQuestion]=useState('How is my budget doing?');
  const {data=[]}=useQuery({queryKey:['budgets'], queryFn:api.budgets});
  const add=useMutation({mutationFn:()=>api.addBudget({month,category,amount:Number(amount)}), onSuccess:()=>{setAmount(''); qc.invalidateQueries({queryKey:['budgets']})}});
  const ask=useMutation({mutationFn:()=>api.askAssistant({month, question})});
  return <div className="space-y-8">
    <section className="grid gap-5 xl:grid-cols-[1.05fr_.95fr]">
      <Card className="p-7"><div className="mb-6 flex items-start justify-between gap-4"><div><Badge tone="good">Budget Lab</Badge><h2 className="mt-4 text-3xl font-black">Plan the month, then interrogate it.</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-white/50">Budgets are guardrails. The assistant uses your uploaded transactions, exclusions, categories, and budgets to answer practical questions without mixing demo and main data.</p></div><PiggyBank className="text-emeraldx" size={34}/></div><div className="grid gap-3 md:grid-cols-[170px_1fr_1fr_auto]"><Input type="month" value={month} onChange={e=>setMonth(e.target.value)}/><Select value={category} onChange={e=>setCategory(e.target.value)}>{categories.map(c=><option key={c}>{c}</option>)}</Select><Input placeholder="Budget amount" value={amount} onChange={e=>setAmount(e.target.value)}/><Button onClick={()=>add.mutate()}><Target size={16}/> Save</Button></div></Card>
      <Card className="p-7"><div className="mb-4 flex items-center gap-3"><div className="rounded-md bg-emeraldx/12 p-2 text-emeraldx"><Bot/></div><div><h3 className="text-xl font-black">Ask RupeeLens</h3><p className="text-sm text-white/45">Deterministic by default. Uses local Ollama only if enabled.</p></div></div><div className="flex flex-wrap gap-2 pb-4">{prompts.map(p=><button key={p} onClick={()=>setQuestion(p)} className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white/65 hover:bg-white/10">{p}</button>)}</div><div className="flex gap-2"><Input value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Ask about budget, UPI, merchants..."/><Button onClick={()=>ask.mutate()} disabled={ask.isPending}><Send size={16}/></Button></div>{ask.data && <div className="mt-5 rounded-md border border-emeraldx/20 bg-emeraldx/8 p-4"><div className="mb-3 flex items-center justify-between"><Badge tone={ask.data.mode==='ollama'?'good':'default'}>{ask.data.mode}</Badge><Sparkles size={16} className="text-saffronx"/></div><p className="text-sm leading-6 text-white/72">{ask.data.answer}</p><div className="mt-4 grid gap-2 sm:grid-cols-3">{ask.data.cards?.map((c:any)=><div key={c.label} className="rounded-md bg-black/20 p-3"><div className="text-xs text-white/40">{c.label}</div><div className="mt-1 font-black">{c.value}</div></div>)}</div></div>}</Card>
    </section>
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">{data.map((b:any)=><Card key={b.id} className="p-5"><div className="flex items-center justify-between"><Badge>{b.month}</Badge><Gauge size={17} className="text-emeraldx"/></div><div className="mt-4 text-lg font-black">{b.category}</div><div className="mt-2 text-3xl font-black text-emeraldx">{rupee(b.amount)}</div><div className="mt-4 h-2 rounded-full bg-white/10"><div className="h-full rounded-full bg-emeraldx" style={{width:'42%'}}/></div></Card>)}</section>
  </div>
}
