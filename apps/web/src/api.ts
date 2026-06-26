const API_URL = import.meta.env.VITE_API_URL || '/api';
export type User = { id: number; username: string; role: string; account_type: 'main' | 'demo' };
export const tokenStore = {
  get: () => sessionStorage.getItem('rupeelens_session_hint'),
  set: () => sessionStorage.setItem('rupeelens_session_hint', '1'),
  clear: () => sessionStorage.removeItem('rupeelens_session_hint')
};
async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (!(init.body instanceof FormData)) headers.set('Content-Type', 'application/json');
  const res = await fetch(`${API_URL}${path}`, { ...init, headers, credentials: 'include' });
  if (!res.ok) throw new Error((await res.text()) || res.statusText);
  return res.json();
}
export const api = {
  login: (username: string, password: string) => request<{access_token:string; user:User}>('/auth/login', { method:'POST', body: JSON.stringify({username,password}) }),
  logout: () => request<{ok:boolean}>('/auth/logout', { method:'POST' }),
  me: () => request<User>('/auth/me'),
  summary: (m: string) => request<any>(`/dashboard/summary?month=${m}`), charts: (m: string) => request<any>(`/dashboard/charts?month=${m}`),
  transactions: (q='') => request<any[]>(`/transactions${q}`), patchTx: (id:number, body:any) => request(`/transactions/${id}`, {method:'PATCH', body:JSON.stringify(body)}), manual: (body:any) => request('/transactions/manual',{method:'POST', body:JSON.stringify(body)}),
  insights: (m:string) => request<any[]>(`/insights?month=${m}`), askAssistant: (body:any) => request<any>('/assistant/query',{method:'POST', body:JSON.stringify(body)}), budgets: () => request<any[]>('/budgets'), addBudget: (b:any) => request('/budgets',{method:'POST', body:JSON.stringify(b)}),
  accounts: () => request<any[]>('/accounts'), addAccount: (a:any) => request('/accounts',{method:'POST', body:JSON.stringify(a)}), rules: () => request<any[]>('/rules'), addRule: (r:any) => request('/rules',{method:'POST', body:JSON.stringify(r)}), uploads: () => request<any[]>('/uploads'), confirmUpload: (id:number) => request(`/uploads/${id}/confirm`,{method:'POST'}), integrations: () => request<any[]>('/integrations'), report: (m:string) => request<any>(`/reports/monthly?month=${m}`),
  upload: (form: FormData) => request<any[]>('/uploads', { method:'POST', body:form })
};
