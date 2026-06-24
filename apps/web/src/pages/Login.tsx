import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, BadgeIndianRupee, Banknote, CreditCard, Eye, Fingerprint, Gauge, LockKeyhole, ReceiptText, ShieldCheck, Sparkles, TrendingUp, WalletCards } from 'lucide-react';
import { api, tokenStore } from '../api';
import { Button, GhostButton, Input } from '../components/ui';

const insightCards = [
  { label: 'Food & Dining', value: '+18%', detail: 'Weekend ordering spike', icon: TrendingUp },
  { label: 'Subscriptions', value: '3', detail: 'Netflix, Spotify, Prime', icon: ReceiptText },
  { label: 'UPI this month', value: '₹12,430', detail: 'Small payments under watch', icon: BadgeIndianRupee },
  { label: 'Excluded safely', value: '₹48k', detail: 'Credit card payment removed', icon: ShieldCheck }
];

const rails = ['HDFC Regalia', 'ICICI Amazon Pay', 'Google Pay UPI', 'SBI Salary'];

export default function Login(){
  const [username,setUsername]=useState('');
  const [password,setPassword]=useState('');
  const [error,setError]=useState('');
  const [loading,setLoading]=useState(false);
  const nav=useNavigate();
  async function doLogin(u=username,p=password){
    setLoading(true); setError('');
    try{ const res=await api.login(u,p); tokenStore.set(res.access_token); nav('/'); }
    catch(e){ setError('Login failed. Check API URL, username, and password.'); }
    finally{ setLoading(false); }
  }
  return <main className="relative min-h-screen overflow-hidden bg-ink text-white">
    <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_12%,rgba(89,243,195,.28),transparent_28rem),radial-gradient(circle_at_90%_18%,rgba(255,180,84,.22),transparent_26rem),linear-gradient(145deg,#06100e,#0d1816_46%,#17150f)]" />
    <div className="absolute inset-x-0 top-0 h-28 bg-gradient-to-b from-white/10 to-transparent" />
    <div className="relative mx-auto grid min-h-screen max-w-7xl gap-8 px-5 py-8 lg:grid-cols-[1.1fr_.9fr] lg:px-8">
      <section className="flex min-h-[58vh] flex-col justify-between py-8 lg:min-h-screen lg:py-10">
        <motion.div initial={{opacity:0,y:16}} animate={{opacity:1,y:0}} className="flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-md bg-emeraldx text-2xl font-black text-ink shadow-glow">₹</div>
          <div><div className="font-display text-2xl font-black">RupeeLens</div><div className="text-xs uppercase text-emeraldx/80">Spend Intelligence OS</div></div>
        </motion.div>
        <motion.div initial={{opacity:0,y:28}} animate={{opacity:1,y:0}} transition={{delay:.08}} className="max-w-3xl">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/8 px-3 py-1 text-sm text-white/70 backdrop-blur"><Eye size={15}/> Statement chaos, made visible</div>
          <h1 className="font-display text-6xl font-black leading-[.92] sm:text-7xl xl:text-8xl">See where your money actually goes.</h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-white/58">Upload credit cards, UPI exports, bank statements, and manual spends. RupeeLens separates real lifestyle spend from transfers, refunds, and card payments.</p>
        </motion.div>
        <div className="grid gap-3 sm:grid-cols-4">{rails.map((r,i)=><motion.div key={r} initial={{opacity:0,y:18}} animate={{opacity:1,y:0}} transition={{delay:.16+i*.06}} className="rounded-md border border-white/10 bg-white/7 p-3 backdrop-blur"><CreditCard className="mb-3 text-emeraldx" size={18}/><div className="text-sm font-bold">{r}</div><div className="mt-1 text-xs text-white/38">isolated source</div></motion.div>)}</div>
      </section>
      <section className="flex items-center justify-center py-8">
        <motion.div initial={{opacity:0,scale:.96}} animate={{opacity:1,scale:1}} transition={{delay:.1}} className="w-full max-w-xl">
          <div className="glass card relative overflow-hidden p-5 shadow-glow">
            <div className="absolute right-4 top-4 rounded-full border border-emeraldx/30 bg-emeraldx/10 px-3 py-1 text-xs font-bold text-emeraldx">JWT protected</div>
            <div className="mb-6 flex items-center gap-3"><div className="grid h-12 w-12 place-items-center rounded-md bg-white/10"><Fingerprint className="text-emeraldx"/></div><div><h2 className="text-2xl font-black">Open your money cockpit</h2><p className="text-sm text-white/45">Main account uses `.env`; demo uses sample-only data.</p></div></div>
            <div className="grid gap-3"><Input placeholder="Username" autoComplete="username" value={username} onChange={e=>setUsername(e.target.value)}/><Input placeholder="Password" type="password" autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)} onKeyDown={e=>{if(e.key==='Enter') doLogin()}}/>{error && <p className="rounded-md border border-saffronx/25 bg-saffronx/10 px-3 py-2 text-sm text-saffronx">{error}</p>}<Button disabled={loading} onClick={()=>doLogin()}><LockKeyhole size={17}/> Login securely <ArrowRight size={16}/></Button><GhostButton disabled={loading} onClick={()=>doLogin('demo','demo123')}><Sparkles size={17}/> Explore demo dashboard</GhostButton></div>
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">{insightCards.map((item,i)=>{const Icon=item.icon; return <motion.div key={item.label} initial={{opacity:0,y:14}} animate={{opacity:1,y:0}} transition={{delay:.22+i*.06}} className="glass card p-4"><div className="flex items-start justify-between gap-3"><div><p className="text-xs uppercase text-white/38">{item.label}</p><div className="mt-2 text-2xl font-black">{item.value}</div><p className="mt-1 text-xs text-white/45">{item.detail}</p></div><div className="rounded-md bg-emeraldx/12 p-2 text-emeraldx"><Icon size={18}/></div></div></motion.div>})}</div>
          <div className="mt-4 grid grid-cols-3 gap-3 text-xs text-white/48"><div className="rounded-md border border-white/10 bg-white/5 p-3"><WalletCards size={16} className="mb-2 text-emeraldx"/>Cards tracked separately</div><div className="rounded-md border border-white/10 bg-white/5 p-3"><Banknote size={16} className="mb-2 text-saffronx"/>Transfers excluded</div><div className="rounded-md border border-white/10 bg-white/5 p-3"><Gauge size={16} className="mb-2 text-sky-300"/>Awareness score</div></div>
        </motion.div>
      </section>
    </div>
  </main>
}
