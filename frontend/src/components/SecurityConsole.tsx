import { useState } from 'react';
import { ArrowRight, ScanLine } from 'lucide-react';
import { analyzeAction, getScenarios } from '../services/api';
import type { AnalysisResult } from '../services/api';
import { Badge, Empty, ErrorState, Loading, Result } from './shared';
import { readable } from '../services/presentation';
import { useResource } from '../services/useResource';

export default function SecurityConsole({ onAnalyzed, refreshKey }: { onAnalyzed: () => void; refreshKey: number }) {
  const [selected, setSelected] = useState('');
  const [runError, setRunError] = useState('');
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [retry, setRetry] = useState(0);
  const { data: scenarios, error } = useResource(getScenarios, `${refreshKey}-${retry}`);
  const scenario = scenarios?.find(item => item.id === selected) || scenarios?.find(item => item.id === 'safe-internal-update') || scenarios?.[0];
  async function run() {
    if (!scenario || running) return;
    setRunning(true); setRunError(''); setResult(null);
    try { setResult(await analyzeAction(scenario.action)); onAnalyzed(); }
    catch (e) { setRunError(e instanceof Error ? e.message : 'Analysis failed.'); }
    finally { setRunning(false); }
  }
  if (error) return <ErrorState message={error} retry={() => setRetry(v => v + 1)} />;
  if (!scenarios) return <Loading />;
  if (!scenario) return <Empty title="No scenarios available">The backend has no seeded scenarios.</Empty>;
  return <><div className="console-grid"><section className="panel"><div className="panel-heading"><div><span className="eyebrow">SCENARIO SIMULATOR</span><h2>Test the trust boundary</h2></div><ScanLine className="accent" /></div><p className="muted">Choose a backend scenario to inspect its proposed action.</p><label htmlFor="scenario">Security scenario</label><select id="scenario" value={scenario.id} disabled={running} onChange={e => { setSelected(e.target.value); setResult(null); setRunError(''); }}>{scenarios.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select><div className="scenario-description"><h3>{scenario.name}</h3><p>{scenario.description}</p><span className="expected">Expected outcome <Badge decision={scenario.expected_decision} /></span></div><dl className="facts"><div><dt>Agent</dt><dd>{scenario.action.agent_name}</dd></div><div><dt>Source</dt><dd>{readable(scenario.action.source_type)}</dd></div><div><dt>Trust</dt><dd>{readable(scenario.action.source_trust)}</dd></div><div><dt>Sensitivity</dt><dd>{readable(scenario.action.data_sensitivity)}</dd></div></dl><div className="task"><span className="eyebrow">USER TASK</span><p>{scenario.action.user_task}</p></div></section>
  <section className="panel"><div className="panel-heading"><div><span className="eyebrow">ACTION INSPECTOR</span><h2>Before anything happens</h2></div><span className="small-tag">SIMULATION</span></div><h3>Source content</h3><pre className="source-content">{scenario.action.external_content}</pre><dl className="facts"><div><dt>Proposed action</dt><dd><code>{scenario.action.proposed_action}</code></dd></div><div><dt>Destination</dt><dd>{scenario.action.action_target || 'No destination'}</dd></div><div><dt>Resources</dt><dd>{scenario.action.requested_resources.join(', ') || 'None requested'}</dd></div><div><dt>User approval</dt><dd>{scenario.action.explicit_user_approval ? 'Provided in scenario' : 'Not provided'}</dd></div><div><dt>External communication</dt><dd>{scenario.action.requires_external_communication ? 'Requested' : 'Not requested'}</dd></div><div><dt>Payment</dt><dd>{scenario.action.requires_payment ? 'Requested' : 'Not requested'}</dd></div></dl><button className="primary analyze" onClick={run} disabled={running}>{running ? <><span className="spinner" />Analyzing action…</> : <>Analyze action <ArrowRight size={17} /></>}</button><p className="footnote">Sends this proposal to the security API and records the verdict. Nothing is executed.</p></section></div>{runError && <ErrorState message={runError} />}{result && <Result result={result} />}</>;
}


