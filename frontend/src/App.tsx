import { lazy, Suspense, useEffect, useState } from 'react';
import { Activity, BookOpen, ChevronRight, ClipboardList, LayoutDashboard, RefreshCw, ScanLine, ShieldCheck } from 'lucide-react';
import { getHealth } from './services/api';
import { Loading } from './components/shared';
import './App.css';

const Dashboard = lazy(() => import('./components/Dashboard'));
const SecurityConsole = lazy(() => import('./components/SecurityConsole'));
const AuditLog = lazy(() => import('./components/AuditLog'));
const Policies = lazy(() => import('./components/Policies'));
const About = lazy(() => import('./components/About'));

const pages = [
  { id: 'dashboard', title: 'Overview', icon: LayoutDashboard, description: 'Monitor security decisions across your agent workflows.' },
  { id: 'console', title: 'Security Console', icon: ScanLine, description: 'Inspect a proposal. Understand the risk. Decide what happens next.' },
  { id: 'audit', title: 'Audit Log', icon: ClipboardList, description: 'Trace every assessment back to its evidence and decision.' },
  { id: 'policies', title: 'Policies & Permissions', icon: ShieldCheck, description: 'Understand the boundaries that keep each assistant in scope.' },
  { id: 'about', title: 'About / Threat Model', icon: BookOpen, description: 'What TrustLayer detects, how it decides, and where its limits are.' },
];
const readPage = () => pages.some(p => p.id === window.location.hash.slice(1)) ? window.location.hash.slice(1) : 'dashboard';
export default function App() {
  const [page, setPage] = useState(readPage); const [revision, setRevision] = useState(0);
  const [health, setHealth] = useState<'checking' | 'online' | 'offline'>('checking');
  const [healthRetry, setHealthRetry] = useState(0);
  useEffect(() => { const change = () => setPage(readPage()); window.addEventListener('hashchange', change); return () => window.removeEventListener('hashchange', change); }, []);
  useEffect(() => { let active = true;
    async function check() { try { const data = await getHealth(); if (active) setHealth(data.status === 'healthy' ? 'online' : 'offline'); } catch { if (active) setHealth('offline'); } }
    void check(); const interval = window.setInterval(() => void check(), 30000);
    return () => { active = false; window.clearInterval(interval); };
  }, [healthRetry]);
  const current = pages.find(p => p.id === page)!;
  function navigate(id: string) { window.location.hash = id; setPage(id); window.scrollTo({ top: 0 }); }
  return <div className="app-shell"><a className="skip-link" href="#main-content" onClick={e => { e.preventDefault(); document.getElementById('main-content')?.focus(); }}>Skip to content</a><aside className="sidebar"><a className="brand" href="#dashboard" onClick={() => navigate('dashboard')}><span className="brand-mark"><ShieldCheck size={26} /></span><span>TrustLayer<small>AGENT SECURITY PLATFORM</small></span></a><span className="nav-label">WORKSPACE</span><nav aria-label="Main navigation">{pages.map(p => <a key={p.id} href={`#${p.id}`} className={p.id === page ? 'active' : ''} aria-current={p.id === page ? 'page' : undefined} onClick={() => navigate(p.id)}><p.icon size={18} />{p.title}{p.id === page && <ChevronRight size={15} className="nav-chevron" />}</a>)}</nav><div className="sidebar-note"><ShieldCheck size={20} /><strong>Analyze before execution</strong><p>Deterministic checks.<br />Explainable decisions.</p><span className="small-tag">LOCAL DEMO</span></div><div className="sidebar-footer">TrustLayer · v0.1<br /><span>Security at the action boundary</span></div></aside><div className="workspace"><header className="topbar"><span><Activity size={16} /> Agent security workspace</span><div><span className={`connection ${health}`} role="status"><i />{health === 'checking' ? 'Checking API' : health === 'online' ? 'API connected' : 'API unavailable'}</span><button className="icon-button" aria-label="Refresh API connection and page data" onClick={() => { setHealth('checking'); setHealthRetry(v => v + 1); setRevision(v => v + 1); }}><RefreshCw size={16} /></button></div></header><main id="main-content" tabIndex={-1}><div className="page-heading"><div><span className="eyebrow">TRUSTLAYER / {page.toUpperCase()}</span><h1>{current.title}</h1><p>{current.description}</p></div><span className="small-tag">ANALYSIS ONLY</span></div>{health === 'offline' && <div className="offline-banner" role="alert">The backend is unavailable. Start the configured FastAPI backend, then refresh the connection. No simulated results will be substituted.</div>}<Suspense fallback={<Loading />}>{page === 'dashboard' && <Dashboard revision={revision} openConsole={() => navigate('console')} />}{page === 'console' && <SecurityConsole refreshKey={healthRetry} onAnalyzed={() => setRevision(v => v + 1)} />}{page === 'audit' && <AuditLog revision={revision} />}{page === 'policies' && <Policies key={revision} />}{page === 'about' && <About />}</Suspense></main><footer className="workspace-footer"><span>TrustLayer keeps the decision visible.</span><span>No external actions are executed.</span></footer></div></div>;
}



