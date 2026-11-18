import { useState } from 'react'
import { api } from '../api'
import { useApp } from '../store'
import { LANGS } from '../i18n'
import Orb from '../components/Orb'
import { Err } from '../components/ui'
const PROF = ['Student', 'Teacher', 'Professor', 'Researcher', 'Writer', 'Working Professional', 'Other']
export default function Auth() {
  const { login, guest } = useApp(); const [reg, setReg] = useState(false); const [err, setErr] = useState(''); const [busy, setBusy] = useState(false)
  const [f, setF] = useState<any>({ full_name: '', email: '', password: '', confirm_password: '', profession: 'Student', course: '', institution: '', interests: '', interface_language: localStorage.getItem('lang') || 'en' })
  const set = (k: string) => (e: any) => setF({ ...f, [k]: e.target.value })
  const submit = async (e: any) => {
    e.preventDefault(); setErr(''); setBusy(true)
    try { login(await api(reg ? '/auth/register' : '/auth/login', { method: 'POST', body: reg ? { ...f, institution: f.institution || null, interests: f.interests || null } : { email: f.email, password: f.password } })) }
    catch (x: any) { setErr(x.message) } finally { setBusy(false) } }
  return <div className="min-h-screen grid lg:grid-cols-2">
    <div className="hidden lg:flex flex-col items-center justify-center text-white p-10" style={{ background: 'var(--hero)' }}>
      <Orb state="idle" size={280} /><h1 className="text-4xl font-bold mt-12">EduNexus</h1><p className="opacity-90 mt-2 text-center">Your Personal AI Learning & Productivity Workspace</p></div>
    <div className="flex items-center justify-center p-6"><form onSubmit={submit} className="card p-7 w-full max-w-md space-y-3">
      <h2 className="text-xl font-semibold">{reg ? 'Create your account' : 'Welcome back'}</h2>
      {reg && <input className="input" placeholder="Full name" value={f.full_name} onChange={set('full_name')} required />}
      <input className="input" type="email" placeholder="Email" value={f.email} onChange={set('email')} required />
      <input className="input" type="password" placeholder="Password (min 8 characters)" value={f.password} onChange={set('password')} required />
      {reg && <>
        <input className="input" type="password" placeholder="Confirm password" value={f.confirm_password} onChange={set('confirm_password')} required />
        <select className="input" value={f.profession} onChange={set('profession')}>{PROF.map(p => <option key={p}>{p}</option>)}</select>
        <input className="input" placeholder="Course / Degree / Subject" value={f.course} onChange={set('course')} required />
        <input className="input" placeholder="Institution or organization (optional)" value={f.institution} onChange={set('institution')} />
        <input className="input" placeholder="Learning interests (optional)" value={f.interests} onChange={set('interests')} />
        <select className="input" value={f.interface_language} onChange={e => { set('interface_language')(e); guest({ lang: e.target.value }) }}>{Object.entries(LANGS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></>}
      <Err msg={err} />
      <button className="btn w-full justify-center" disabled={busy}>{busy ? 'Please wait…' : reg ? 'Register' : 'Log in'}</button>
      <button type="button" className="text-sm text-brand w-full" onClick={() => { setReg(!reg); setErr('') }}>{reg ? 'Already have an account? Log in' : 'New here? Create an account'}</button>
    </form></div></div>
}
