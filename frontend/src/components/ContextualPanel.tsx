import { ShieldCheck, Sparkles } from 'lucide-react';
import type { ContextualAnalysis } from '../services/api';
import { readable } from '../services/presentation';

const unavailableReasons: Record<string, string> = {
  disabled: 'The optional provider is disabled in backend configuration.',
  missing_api_key: 'The backend has no provider key configured.',
  missing_model: 'The backend has no provider model configured.',
  invalid_configuration: 'The backend provider configuration needs attention.',
  non_simulated_action: 'Only the code-defined synthetic demo actions can be sent to the provider.',
  timeout: 'The provider exceeded the response deadline.',
  provider_error: 'The provider could not complete this assessment.',
  invalid_response: 'The provider response failed strict validation.',
};

export default function ContextualPanel({ analysis }: { analysis?: ContextualAnalysis }) {
  if (!analysis || analysis.available === false) {
    return <section className="contextual-unavailable" aria-label="AI contextual analysis unavailable">
      <Sparkles size={19} /><div><h3>Contextual AI analysis unavailable — deterministic protection remains active.</h3><p>{analysis?.available === false ? unavailableReasons[analysis.reason] || 'The optional provider is unavailable.' : 'This earlier assessment did not request contextual evidence.'}</p></div>
    </section>;
  }
  return <section className="contextual-panel" aria-label="AI contextual analysis">
    <div className="panel-heading"><div><span className="eyebrow">ADDITIONAL REASONING</span><h2><Sparkles size={19} />AI Contextual Analysis</h2></div><span className="small-tag">ADVISORY ONLY</span></div>
    <p className="contextual-boundary"><ShieldCheck size={16} />Deterministic policy enforcement remains authoritative. AI evidence cannot change the verdict or authorize an action.</p>
    <dl className="contextual-indicators"><div><dt>Instruction conflict</dt><dd>{analysis.instruction_conflict ? 'Detected' : 'Not detected'}</dd></div><div><dt>Untrusted instruction</dt><dd>{analysis.untrusted_instruction ? 'Detected' : 'Not detected'}</dd></div><div><dt>Intent mismatch</dt><dd>{analysis.intent_mismatch ? 'Detected' : 'Not detected'}</dd></div><div><dt>Model confidence</dt><dd>{Math.round(analysis.confidence * 100)}%<small>Self-reported, not a safety guarantee</small></dd></div></dl>
    <div className="contextual-evidence"><h3>Contextual threats</h3>{analysis.threats.length ? <ul className="evidence">{analysis.threats.map(threat => <li key={threat}>{readable(threat)}</li>)}</ul> : <p className="muted">No contextual threats reported.</p>}<h3>AI reasoning</h3><p>{analysis.reasoning}</p><h3>Suggested safe action · advisory</h3><p>{analysis.recommendation}</p></div>
    <div className="contextual-model"><span>Provider: Featherless</span><span>Model: {analysis.model}</span></div><p className="footnote">Model output is untrusted evidence. Follow the deterministic recommended next action above.</p>
  </section>;
}
