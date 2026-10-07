import type { Decision } from './api';
export const decisions: Decision[] = ['ALLOW', 'REVIEW REQUIRED', 'BLOCK'];
export const decisionColor = (decision: Decision) => decision === 'ALLOW' ? '#4adeac' : decision === 'BLOCK' ? '#fb7185' : '#fbbf24';
export const readable = (text: string) => text.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
const explanations: Record<string, string> = {
  instruction_override: 'the source asks the agent to override its instructions',
  concealment_or_approval_bypass: 'the source asks the agent to hide an action or bypass approval',
  authority_spoofing: 'the source claims system or administrator authority',
  untrusted_data_transfer_instruction: 'untrusted content instructs the agent to transfer data',
  sensitive_external_transfer: 'the proposal would send sensitive data outside the trust boundary',
  unapproved_external_communication: 'external communication has no explicit user approval',
  unapproved_payment: 'the payment has no explicit user approval',
  untrusted_source_side_effect: 'untrusted content is associated with an external or payment action',
  unknown_agent: 'the agent has no registered permission profile',
  action_outside_profile: 'the proposed action exceeds the agent’s permissions',
  resource_outside_profile: 'the requested resources exceed the agent’s permissions',
  injection_policy_triggered: 'the prompt-injection policy was triggered',
  explicit_approval_missing: 'required user approval is missing',
  destination_missing: 'the proposal has no required destination',
};
export const plainExplanation = (text: string) => text.replace(/\b[a-z]+(?:_[a-z]+)+\b/g, token => explanations[token] || token.replace(/_/g, ' '));
