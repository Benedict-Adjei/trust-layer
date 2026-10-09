import { useState } from 'react';
import { Bot, LockKeyhole } from 'lucide-react';
import { getAgents, getPolicies } from '../services/api';
import { Empty, ErrorState, Loading } from './shared';
import { readable } from '../services/presentation';
import { useResource } from '../services/useResource';

const loadPolicies = async () => { const [agents, policies] = await Promise.all([getAgents(), getPolicies()]); return { agents, policies }; };

export default function Policies() {
  const [retry, setRetry] = useState(0);
  const { data, error } = useResource(loadPolicies, String(retry));
  if (error) return <ErrorState message={error} retry={() => setRetry(v => v + 1)} />;
  if (!data) return <Loading />;
  return <><div className="section-heading"><h2>Agent permission profiles</h2><p>Least-privilege boundaries for every registered assistant.</p></div><div className="agent-grid">{data.agents.map(agent => <section className="panel agent-card" key={agent.id}><div className="agent-icon"><Bot size={24} /></div><h2>{agent.name}</h2><span className="small-tag">REGISTERED PROFILE</span><h3>Allowed actions</h3><div className="chips">{agent.allowed_actions.map(a => <code key={a}>{a}</code>)}</div><h3>Allowed resources</h3><div className="chips">{agent.allowed_resources.map(r => <code key={r}>{r}</code>)}</div><h3>Requires explicit approval</h3>{agent.approval_actions.length ? <ul className="evidence">{agent.approval_actions.map(a => <li key={a}>{readable(a)}</li>)}</ul> : <p className="muted">No profile-specific approval actions.</p>}</section>)}</div>{!data.agents.length && <Empty title="No agent profiles available" />}<section className="panel"><div className="panel-heading"><div><h2>Security policies</h2><p className="muted">Enforced by the deterministic backend.</p></div><LockKeyhole className="accent" /></div><div className="policy-list">{data.policies.map((policy, i) => <article key={policy.id}><span className="policy-number">{String(i + 1).padStart(2, '0')}</span><div><h3>{readable(policy.id)}</h3><p>{policy.description}</p></div></article>)}</div>{!data.policies.length && <Empty title="No policies available" />}<p className="footnote">Profiles and policies are read-only. User approval cannot override injection, resource, or sensitive-transfer blocks.</p></section></>;
}
