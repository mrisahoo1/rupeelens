import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BarChart3, Upload, ReceiptText, Sparkles, WalletCards, RotateCcw, FileText, Landmark, Settings, ShieldCheck, PlugZap, LogOut, Menu, Bell, Shield } from 'lucide-react';
import { tokenStore, type User } from '../api';
import { Badge, GhostButton } from './ui';

const nav = [['Dashboard','/',BarChart3],['Upload Center','/upload',Upload],['Transactions','/transactions',ReceiptText],['Insights','/insights',Sparkles],['Budgets','/budgets',WalletCards],['Revisit Board','/revisit',RotateCcw],['Reports','/reports',FileText],['Accounts & Cards','/accounts',Landmark],['Rules','/rules',ShieldCheck],['BillPay & Integrations','/integrations',PlugZap],['Settings','/settings',Settings]] as const;

function NavItems(){ return <nav className="grid gap-1.5">{nav.map(([label,path,Icon])=><NavLink key={path} to={path} className={({isActive})=>`group flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-bold transition ${isActive?'border border-emeraldx/20 bg-emeraldx/12 text-emeraldx shadow-[inset_0_1px_0_rgba(255,255,255,.07)]':'text-white/58 hover:bg-white/7 hover:text-white'}`}><Icon className="shrink-0 transition group-hover:scale-105" size={17}/><span className="truncate">{label}</span></NavLink>)}</nav> }

export default function Layout({user}:{user:User}) {
  const navigate = useNavigate();
  const logout = () => { tokenStore.clear(); navigate('/login'); };
  return <div className="min-h-screen lg:flex">
    <aside className="hidden lg:sticky lg:top-0 lg:flex lg:h-screen lg:w-80 lg:flex-col lg:border-r lg:border-white/10 lg:bg-[#050b09]/82 lg:p-5 lg:backdrop-blur-2xl">
      <div className="mb-7 flex items-center gap-3">
        <div className="grid h-12 w-12 place-items-center rounded-md bg-emeraldx text-2xl font-black text-ink shadow-glow">₹</div>
        <div><div className="font-display text-2xl font-black">RupeeLens</div><div className="text-xs font-semibold text-white/42">Personal finance intelligence</div></div>
      </div>
      {user.account_type==='demo' && <div className="mb-4 rounded-md border border-saffronx/25 bg-saffronx/10 p-3 text-xs font-semibold leading-5 text-saffronx">Demo mode — isolated sample data only.</div>}
      <div className="mb-5 rounded-md border border-white/10 bg-white/5 p-3">
        <div className="flex items-center gap-2 text-xs font-black uppercase text-white/38"><Shield size={14}/> Secure session</div>
        <div className="mt-2 flex items-center justify-between gap-2"><span className="truncate text-sm font-black">{user.username}</span><Badge tone={user.account_type==='demo'?'warn':'good'}>{user.account_type}</Badge></div>
      </div>
      <div className="min-h-0 flex-1 overflow-auto pr-1"><NavItems /></div>
      <button onClick={logout} className="mt-5 flex w-full items-center gap-3 rounded-md border border-white/10 bg-white/5 px-3 py-2.5 text-sm font-bold text-white/60 transition hover:bg-white/10 hover:text-white"><LogOut size={17}/> Logout</button>
    </aside>

    <main className="relative flex-1 overflow-hidden">
      <div className="sticky top-0 z-30 border-b border-white/10 bg-[#050b09]/78 px-4 py-3 backdrop-blur-2xl lg:hidden">
        <div className="flex items-center justify-between gap-3"><div className="flex items-center gap-3"><div className="grid h-10 w-10 place-items-center rounded-md bg-emeraldx font-black text-ink">₹</div><div><div className="font-black">RupeeLens</div><div className="text-xs text-white/42">Command OS</div></div></div><GhostButton className="px-3"><Menu size={17}/></GhostButton></div>
        <div className="no-scrollbar mt-3 flex gap-2 overflow-auto pb-1">{nav.map(([label,path,Icon])=><NavLink key={path} to={path} className={({isActive})=>`inline-flex shrink-0 items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-bold ${isActive?'border-emeraldx/30 bg-emeraldx/14 text-emeraldx':'border-white/10 bg-white/5 text-white/60'}`}><Icon size={14}/>{label}</NavLink>)}</div>
      </div>
      <div className="mx-auto max-w-[1500px] p-4 sm:p-6 lg:p-8">
        <motion.header initial={{opacity:0,y:-8}} animate={{opacity:1,y:0}} className="mb-7 flex flex-wrap items-center justify-between gap-4">
          <div><p className="text-xs font-black uppercase text-emeraldx/80">See where your money actually goes</p><h1 className="mt-2 font-display text-3xl font-black sm:text-4xl">Personal finance intelligence</h1></div>
          <div className="flex items-center gap-2"><Badge tone={user.account_type==='demo'?'warn':'good'}>{user.username}</Badge><Badge>JWT protected</Badge><button className="grid h-10 w-10 place-items-center rounded-md border border-white/10 bg-white/6 text-white/62 transition hover:bg-white/10"><Bell size={17}/></button></div>
        </motion.header>
        <Outlet />
      </div>
    </main>
  </div>
}
