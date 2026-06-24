import { useQuery } from '@tanstack/react-query';
import { api } from '../api';
import { rupee } from '../lib';
import { Badge, Card } from '../components/ui';
export default function Revisit(){ const {data=[]}=useQuery({queryKey:['revisit'], queryFn:()=>api.transactions('?revisit=true')}); return <div className="grid gap-4">{data.map((t:any)=><Card key={t.id}><div className="flex flex-wrap items-center justify-between gap-3"><div><Badge tone="warn">Revisit later</Badge><h3 className="mt-3 text-xl font-black">{t.merchant_normalized}</h3><p className="text-sm text-white/45">{t.description_raw}</p><p className="mt-2 text-sm text-white/60">Why did I spend this? Was it necessary? Can I reduce this next month?</p></div><div className="text-2xl font-black">{rupee(t.amount)}</div></div></Card>)}</div> }
