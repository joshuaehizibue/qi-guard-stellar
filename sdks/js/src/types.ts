/**
 * TypeScript Type Definitions for QI-Guard Stellar MVP Client SDK.
 * Matches API_CONTRACT.md schema specifications.
 */

export type SeverityLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface RiskScore {
  classical: number;
  hybrid: number;
  delta: number;
}

export interface Finding {
  id: string;
  type: string;
  component?: string;
  severity: SeverityLevel;
  evidence: string[];
  remediation?: string;
  model_version?: string;
  quantum_contribution?: boolean;
}

export interface QuantumResilienceScore {
  score: number;
  status: "NOT_READY" | "TRANSITIONING" | "PQC_COMPLIANT";
}

export interface ContractRiskRequest {
  wasm_byte_code?: string;
  contract_address?: string;
  source_code_url?: string;
  network?: "testnet" | "mainnet" | string;
}

export interface ContractRiskReport {
  job_id: string;
  contract_id?: string;
  risk_score: RiskScore;
  severity: SeverityLevel;
  confidence: number;
  findings: Finding[];
  quantum_resilience: QuantumResilienceScore;
  timestamp: string;
}

export interface BehavioralTransaction {
  id?: string;
  ledger?: number;
  type?: string;
  amount?: number;
  asset?: string;
  destination?: string;
  timestamp?: string;
}

export interface BehavioralAnalysisRequest {
  address: string;
  analysis_window?: string;
  transactions?: BehavioralTransaction[];
}

export interface AnomalyFlag {
  code: string;
  description: string;
  severity: SeverityLevel;
  confidence: number;
}

export interface BehavioralAnalysisReport {
  job_id: string;
  address: string;
  analysis_window: string;
  anomaly_score: {
    classical: number;
    hybrid: number;
    delta: number;
  };
  risk_level: SeverityLevel;
  flags: AnomalyFlag[];
  timestamp: string;
}

export interface QuantumResilienceReport {
  target: string;
  target_type: "CONTRACT" | "ACCOUNT";
  resilience_score: number;
  status: "NOT_READY" | "TRANSITIONING" | "PQC_COMPLIANT";
  key_type: string;
  exposure_count: number;
  pqc_recommendations: string[];
  timestamp: string;
}

export interface BenchmarkMetrics {
  precision: number;
  recall: number;
  f1: number;
  latency_ms: number;
}

export interface BenchmarkReport {
  job_id: string;
  contract_id?: string;
  classical: BenchmarkMetrics;
  hybrid: BenchmarkMetrics;
  quantum_delta: {
    f1_improvement: number;
    latency_delta_ms: number;
    quantum_advantage_observed: boolean;
  };
}

export interface ClientOptions {
  apiKey?: string;
  baseUrl?: string;
  timeoutMs?: number;
  maxRetries?: number;
}
