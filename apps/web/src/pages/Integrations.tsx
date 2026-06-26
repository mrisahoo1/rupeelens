import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { BellRing, CheckCircle2, FileText, Landmark, LockKeyhole, Mail, PlugZap, ShieldCheck, TimerReset, WalletCards } from 'lucide-react';
import { api } from '../api';
import { Badge, Card, EmptyState, PageTitle, Reveal, Surface } from '../components/ui';

const icons:any = {
  account_aggregator_sync: Landmark,
  bbps_bill_reminders: BellRing,
  upi_export_import: WalletCards,
  email_statement_import: Mail,
  recurring_bill_detection: TimerReset,
};

function statusTone(status:string){ return status === 'current' ? 'good' : 'warn'; }

function CapabilityCard({item, index}:{item:any; index:number}){
  const Icon = icons[item.id] || PlugZap;
  return <motion.div initial={{opacity:0,y:16}} animate={{opacity:1,y:0}} transition={{delay:index*.04}}>
    <Card className="flex min-h-[390px] flex-col p-6 transition duration-300 hover:-translate-y-1 hover:border-emeraldx/25">
      <div className="flex items-start justify-between gap-4">
        <div className="grid h-12 w-12 place-items-center rounded-md border border-white/10 bg-white/8 text-emeraldx"><Icon size={24}/></div>
        <div className="flex flex-col items-end gap-2"><Badge tone={statusTone(item.status)}>{item.status === 'current' ? 'current' : 'coming soon'}</Badge><Badge>{item.live ? 'live workflow' : 'stub only'}</Badge></div>
      </div>
      <div className="mt-6 text-xs font-black uppercase text-white/34">{item.provider}</div>
      <h3 className="mt-2 text-2xl font-black leading-tight">{item.name}</h3>
      <p className="mt-3 text-sm leading-6 text-white/56">{item.description}</p>

      <div className="mt-5 grid gap-3">
        <Surface className="p-3"><div className="mb-2 flex items-center gap-2 text-xs font-black uppercase text-white/38"><FileText size={14}/> Data flow</div><div className="flex flex-wrap gap-1.5">{item.data_flow?.slice(0,5).map((step:string, i:number)=><Badge key={step}>{i+1}. {step}</Badge>)}</div></Surface>
        <Surface className="p-3"><div className="mb-2 flex items-center gap-2 text-xs font-black uppercase text-white/38"><ShieldCheck size={14}/> Safeguards</div><ul className="space-y-1.5 text-xs leading-5 text-white/58">{item.safeguards?.slice(0,4).map((s:string)=><li key={s} className="flex gap-2"><CheckCircle2 className="mt-0.5 shrink-0 text-emeraldx" size={13}/>{s}</li>)}</ul></Surface>
      </div>

      <div className="mt-auto pt-5"><div className="mb-2 text-xs font-black uppercase text-white/34">Architecture boundary</div><div className="rounded-md border border-white/10 bg-black/18 p-3 text-xs leading-5 text-white/52">{item.endpoints?.slice(0,3).join(' · ')}</div></div>
    </Card>
  </motion.div>
}

export default function Integrations(){
  const {data=[], isLoading}=useQuery({queryKey:['integrations'], queryFn:api.integrations});
  const comingSoon = data.filter((item:any)=>item.status !== 'current').length;
  return <div className="space-y-7">
    <PageTitle eyebrow="BillPay & Integrations" title="Future rails, clearly separated from live money movement." description="This page documents the integration architecture RupeeLens is prepared for. BBPS payments, Account Aggregator sync, mailbox access, and bill reminders are explicitly coming soon and do not run in MVP." action={<Badge tone="warn">No real payments implemented</Badge>} />

    <Reveal><Card className="p-6 sm:p-7"><div className="grid gap-4 lg:grid-cols-[1fr_.8fr]"><div><div className="flex items-center gap-3"><div className="grid h-11 w-11 place-items-center rounded-md border border-saffronx/25 bg-saffronx/12 text-saffronx"><LockKeyhole size={22}/></div><div><h3 className="text-2xl font-black">Safety posture</h3><p className="mt-1 text-sm text-white/50">RupeeLens can prepare reminders and sync designs, but it will not initiate payments or claim provider access until a real compliant adapter is added.</p></div></div></div><div className="grid gap-3 sm:grid-cols-3"><Surface><div className="text-xs text-white/38">Current</div><div className="mt-1 text-2xl font-black">{data.filter((i:any)=>i.status==='current').length}</div></Surface><Surface><div className="text-xs text-white/38">Coming soon</div><div className="mt-1 text-2xl font-black">{comingSoon}</div></Surface><Surface><div className="text-xs text-white/38">Payment execution</div><div className="mt-1 text-2xl font-black text-saffronx">0</div></Surface></div></div></Card></Reveal>

    <section className="grid gap-5 lg:grid-cols-2 xl:grid-cols-3">{data.map((item:any, index:number)=><CapabilityCard key={item.id || item.name} item={item} index={index}/>)}</section>

    <Card className="p-6 sm:p-7"><h3 className="text-2xl font-black">Launch checklist before any live integration</h3><div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">{['Provider contract and compliance review','Encrypted token/consent storage','Audit logs and user revocation flow','Read-only reminders before payments'].map(item=><Surface key={item} className="flex items-start gap-3"><ShieldCheck className="mt-0.5 shrink-0 text-emeraldx" size={17}/><span className="text-sm leading-5 text-white/62">{item}</span></Surface>)}</div></Card>

    {!isLoading && !data.length && <EmptyState icon={<PlugZap/>} title="No integration metadata" body="The backend did not return integration capabilities. The page expects future-ready stubs, not live provider claims." />}
  </div>
}
