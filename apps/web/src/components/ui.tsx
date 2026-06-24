import type { ButtonHTMLAttributes, HTMLAttributes, InputHTMLAttributes, ReactNode, SelectHTMLAttributes } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../lib';

export const Card = ({className='', children, ...props}: HTMLAttributes<HTMLElement> & {children: ReactNode}) => <section className={cn('glass card p-5', className)} {...props}>{children}</section>;

export const Surface = ({className='', children, ...props}: HTMLAttributes<HTMLElement> & {children: ReactNode}) => <section className={cn('rounded-md border border-white/10 bg-black/18 p-4', className)} {...props}>{children}</section>;

export const Button = ({className='', ...props}: ButtonHTMLAttributes<HTMLButtonElement>) => <button className={cn('inline-flex min-h-10 items-center justify-center gap-2 rounded-md border border-emeraldx/40 bg-emeraldx px-4 py-2 text-sm font-black text-ink shadow-glow transition duration-200 hover:-translate-y-0.5 hover:shadow-[0_18px_50px_rgba(89,243,195,.18)] focus:outline-none focus:ring-4 focus:ring-emeraldx/25 disabled:opacity-50', className)} {...props} />;

export const GhostButton = ({className='', ...props}: ButtonHTMLAttributes<HTMLButtonElement>) => <button className={cn('inline-flex min-h-10 items-center justify-center gap-2 rounded-md border border-white/12 bg-white/6 px-4 py-2 text-sm font-bold text-white/82 transition duration-200 hover:-translate-y-0.5 hover:bg-white/10 focus:outline-none focus:ring-4 focus:ring-white/10 disabled:opacity-50', className)} {...props} />;

export const Input = ({className='', ...props}: InputHTMLAttributes<HTMLInputElement>) => <input className={cn('min-h-10 w-full rounded-md border border-white/12 bg-[#06100e]/70 px-3 py-2 text-sm text-white outline-none ring-emeraldx/30 transition placeholder:text-white/35 focus:border-emeraldx/45 focus:ring-4', className)} {...props} />;

export const Select = ({className='', ...props}: SelectHTMLAttributes<HTMLSelectElement>) => <select className={cn('min-h-10 w-full rounded-md border border-white/12 bg-[#06100e]/90 px-3 py-2 text-sm text-white outline-none transition focus:border-emeraldx/45 focus:ring-4 focus:ring-emeraldx/25', className)} {...props} />;

export const Badge = ({children, tone='default', className=''}:{children:ReactNode; tone?:'default'|'warn'|'good'|'danger'; className?: string}) => <span className={cn('inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-black', tone==='warn'?'border-saffronx/30 bg-saffronx/14 text-saffronx':tone==='good'?'border-emeraldx/30 bg-emeraldx/14 text-emeraldx':tone==='danger'?'border-red-400/30 bg-red-400/14 text-red-200':'border-white/12 bg-white/8 text-white/72', className)}>{children}</span>;

export const PageTitle = ({eyebrow,title,description,action}:{eyebrow:string; title:string; description:string; action?:ReactNode}) => <Card className="relative overflow-hidden p-6 sm:p-8"><div className="absolute right-0 top-0 h-36 w-36 bg-emeraldx/10 blur-3xl"/><div className="relative flex flex-col gap-5 md:flex-row md:items-end md:justify-between"><div><Badge tone="good">{eyebrow}</Badge><h2 className="mt-4 max-w-3xl text-3xl font-black sm:text-4xl">{title}</h2><p className="mt-3 max-w-2xl text-sm leading-6 text-white/56">{description}</p></div>{action && <div className="shrink-0">{action}</div>}</div></Card>;

export const EmptyState = ({icon, title, body, action}:{icon:ReactNode; title:string; body:string; action?:ReactNode}) => <Card className="p-10 text-center"><div className="mx-auto grid h-14 w-14 place-items-center rounded-md border border-emeraldx/25 bg-emeraldx/12 text-emeraldx">{icon}</div><h3 className="mt-5 text-2xl font-black">{title}</h3><p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-white/50">{body}</p>{action && <div className="mt-5 flex justify-center">{action}</div>}</Card>;

export const Reveal = ({children, delay=0, className=''}:{children:ReactNode; delay?:number; className?:string}) => <motion.div initial={{opacity:0,y:14}} animate={{opacity:1,y:0}} transition={{duration:.42, delay, ease:[.2,.8,.2,1]}} className={className}>{children}</motion.div>;
