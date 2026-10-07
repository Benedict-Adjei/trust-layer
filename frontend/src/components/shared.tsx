import { AlertTriangle, CheckCircle2, ShieldX } from 'lucide-react';
import type { AnalysisResult, Decision } from '../services/api';
import { decisionColor, plainExplanation, readable } from '../services/presentation';
import ContextualPanel from './ContextualPanel';
export function Badge({ decision }: { decision: Decision }) {
  return <span className={`badge ${decision === 'ALLOW' ? 'allow' : decision === 'BLOCK' ? 'block' : 'review'}`}>{decision === 'ALLOW' ? <CheckCircle2 size={13} /> : decision === 'BLOCK' ? <ShieldX size={13} /> : <AlertTriangle size={13} />}{decision}</span>;
}
export function ErrorState({ message, retry }: { message: string; retry?: () => void }) {
  return <div className="error-state" role="alert"><AlertTriangle size={18} /><span>{message}</span>{retry && <button className="secondary" onClick={retry}>Retry</button>}</div>;
}
export function Empty({ title, children }: { title: string; children?: React.ReactNode }) {
  return <div className="empty"><ShieldX size={28} /><h3>{title}</h3>{children}</div>;
}
export function Loading() { return <div className="loading" role="status"><span className="spinner" />Loading live API data…</div>; }
export function Result({ result }: { result: AnalysisResult }) {
  const color = decisionColor(result.decision);
  return <section className="panel result" aria-label="Analysis result">
    <div className="panel-heading"><div><span className="eyebrow">DETERMINISTIC VERDICT</span><h2>Action assessment</h2></div><Badge decision={result.decision} /></div>
    <div className="risk-summary"><div className="risk-ring" style={{ background: `conic-gradient(${color} ${result.risk_score * 3.6}deg, #243043 0deg)` }}><div><strong>{result.risk_score}<small>/100</small></strong><span>RISK SCORE</span></div></div><div><h3 style={{ color }}>{readable(result.risk_level)} risk</h3><p>{result.decision === 'ALLOW' ? 'Passed the current security checks.' : result.decision === 'BLOCK' ? 'The proposed action must be stopped.' : 'Human review is required before proceeding.'}</p><small>Analysis only · no action executed</small></div></div>
    <div className="evidence-grid">{[['Detected threats', result.threat_categories], ['Security signals', result.triggered_signals], ['Violated policies', result.violated_policies]].map(([title, values]) => <div key={title as string}><h3>{title as string}</h3>{(values as string[]).length ? <ul className="evidence">{(values as string[]).map(value => <li key={value}>{readable(value)}</li>)}</ul> : <p className="muted">None detected</p>}</div>)}</div>
    <div className="explanation"><h3>Why this decision?</h3><p>{plainExplanation(result.explanation)}</p></div><div className="next-action"><h3>Recommended next action</h3><p>{result.recommended_next_step}</p></div><ContextualPanel analysis={result.contextual_analysis} /><p className="record-id">Audit ID: {result.action_id}</p>
  </section>;
}
