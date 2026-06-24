import { useQuery } from '@tanstack/react-query';
import { api } from '../api';
import { Badge, Card } from '../components/ui';
export default function Integrations(){ const {data=[]}=useQuery({queryKey:['integrations'], queryFn:api.integrations}); return <div className="grid gap-4 md:grid-cols-2">{data.map((i:any)=><Card key={i.name}><Badge tone={i.status==='current'?'good':'warn'}>{i.status === 'current' ? 'current' : 'coming soon'}</Badge><h3 className="mt-4 text-xl font-black">{i.name}</h3><p className="mt-2 text-sm text-white/50">Future-ready service boundary only. RupeeLens makes no fake live API or payment claim in MVP.</p></Card>)}</div> }
