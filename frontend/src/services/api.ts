const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
export type Decision = 'ALLOW' | 'REVIEW REQUIRED' | 'BLOCK';
export interface AgentAction {
  agent_name: string; user_task: string; source_type: string; source_trust: string;
  external_content: string; proposed_action: string; action_target: string | null;
  requested_resources: string[]; data_sensitivity: string;
  requires_external_communication: boolean; requires_payment: boolean; explicit_user_approval: boolean;
}
export interface AnalysisResult {
  action_id: string; decision: Decision; risk_score: number; risk_level: string;
  threat_categories: string[]; triggered_signals: string[]; violated_policies: string[];
  explanation: string; recommended_next_step: string;
  contextual_analysis?: ContextualAnalysis;
}
export type ContextualAnalysis = {
  available: true; instruction_conflict: boolean; untrusted_instruction: boolean;
  intent_mismatch: boolean; threats: string[]; reasoning: string; recommendation: string;
  confidence: number; provider: 'featherless'; model: string;
} | { available: false; reason: string };
export interface Scenario { id: string; name: string; description: string; expected_decision: Decision; action: AgentAction }
export interface Agent { id: string; name: string; allowed_actions: string[]; allowed_resources: string[]; approval_actions: string[] }
export interface Policy { id: string; description: string }
export interface AuditRecord { action_id: string; created_at: string; action: Pick<AgentAction, 'agent_name' | 'proposed_action' | 'source_trust' | 'data_sensitivity'>; result: AnalysisResult }
export interface AuditPage { items: AuditRecord[]; total: number; limit: number; offset: number }
export interface HealthResponse { status: string; service: string; version: string }
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(`${API_URL}${path}`, { ...options, signal: controller.signal });
    if (!response.ok) throw new Error(`API request failed (${response.status}). Please retry or check the backend.`);
    return await response.json() as T;
  } catch (error) {
    if (error instanceof TypeError) throw new Error('Cannot reach TrustLayer API. Start the backend and check VITE_API_URL.');
    if (error instanceof DOMException && error.name === 'AbortError') throw new Error('The API took too long to respond. Check the Audit Log before retrying an analysis.');
    throw error;
  } finally { window.clearTimeout(timeout); }
}
export const getHealth = () => request<HealthResponse>('/api/health');
export const getScenarios = () => request<Scenario[]>('/api/scenarios');
export const getAgents = () => request<Agent[]>('/api/agents');
export const getPolicies = () => request<Policy[]>('/api/policies');
export const getAudit = (offset = 0, decision: Decision | '' = '', limit = 20) => request<AuditPage>(`/api/audit?offset=${offset}&limit=${limit}${decision ? `&decision=${encodeURIComponent(decision)}` : ''}`);
export const analyzeAction = (action: AgentAction) => request<AnalysisResult>('/api/actions/analyze?contextual=true', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(action) });
