import { Navigate, Route, Routes } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from './api';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import UploadCenter from './pages/UploadCenter';
import Transactions from './pages/Transactions';
import Insights from './pages/Insights';
import Budgets from './pages/Budgets';
import Revisit from './pages/Revisit';
import Reports from './pages/Reports';
import Accounts from './pages/Accounts';
import Rules from './pages/Rules';
import Settings from './pages/Settings';
import Integrations from './pages/Integrations';
function Protected() { const {data, isLoading, isError} = useQuery({queryKey:['me'], queryFn: api.me, retry:false}); if (isLoading) return <div className="grid min-h-screen place-items-center text-white/60">Opening RupeeLens...</div>; if (isError || !data) return <Navigate to="/login"/>; return <Layout user={data}/>; }
export default function App(){ return <Routes><Route path="/login" element={<Login/>}/><Route element={<Protected/>}><Route path="/" element={<Dashboard/>}/><Route path="/upload" element={<UploadCenter/>}/><Route path="/transactions" element={<Transactions/>}/><Route path="/insights" element={<Insights/>}/><Route path="/budgets" element={<Budgets/>}/><Route path="/revisit" element={<Revisit/>}/><Route path="/reports" element={<Reports/>}/><Route path="/accounts" element={<Accounts/>}/><Route path="/rules" element={<Rules/>}/><Route path="/integrations" element={<Integrations/>}/><Route path="/settings" element={<Settings/>}/></Route></Routes> }
