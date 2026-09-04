/**
 * QI-Guard Client implementation for JavaScript / TypeScript.
 * Uses standard Fetch API with automated exponential retry and error parsing.
 */

import {
  ClientOptions,
  ContractRiskRequest,
  ContractRiskReport,
  BehavioralAnalysisRequest,
  BehavioralAnalysisReport,
  QuantumResilienceReport,
  BenchmarkReport
} from "./types.js";

declare const process: any;

export class QIGuardApiError extends Error {
  public status: number;
  public details?: any;

  constructor(message: string, status: number, details?: any) {
    super(message);
    this.name = "QIGuardApiError";
    this.status = status;
    this.details = details;
  }
}

export class QIGuardClient {
  private apiKey: string;
  private baseUrl: string;
  private timeoutMs: number;
  private maxRetries: number;

  constructor(options: ClientOptions = {}) {
    const envKey = typeof process !== "undefined" && process.env ? process.env.QIGUARD_API_KEY : undefined;
    const envUrl = typeof process !== "undefined" && process.env ? process.env.QIGUARD_API_URL : undefined;

    this.apiKey = options.apiKey || envKey || "";
    this.baseUrl = (options.baseUrl || envUrl || "https://stellar.quantuminfra.io/v1").replace(/\/+$/, "");
    this.timeoutMs = options.timeoutMs || 30000;
    this.maxRetries = options.maxRetries !== undefined ? options.maxRetries : 3;
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${path.startsWith("/") ? path : `/${path}`}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "Accept": "application/json",
      ...(options.headers as Record<string, string> || {})
    };

    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }

    let attempt = 0;
    let delay = 300;

    while (true) {
      attempt++;
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), this.timeoutMs);

      try {
        const response = await fetch(url, {
          ...options,
          headers,
          signal: controller.signal
        });

        clearTimeout(timer);

        if (response.ok) {
          return (await response.json()) as T;
        }

        // Retry on 429 Rate Limit or 503 Service Unavailable if attempts remaining
        if ((response.status === 429 || response.status === 503) && attempt <= this.maxRetries) {
          await new Promise((resolve) => setTimeout(resolve, delay));
          delay *= 2;
          continue;
        }

        let errBody: any = null;
        try {
          errBody = await response.json();
        } catch {
          errBody = await response.text();
        }

        const msg = (errBody && errBody.detail) || (errBody && errBody.message) || response.statusText;
        throw new QIGuardApiError(`QI-Guard API Error (${response.status}): ${msg}`, response.status, errBody);
      } catch (err: any) {
        clearTimeout(timer);
        if (err instanceof QIGuardApiError) {
          throw err;
        }
        if (attempt <= this.maxRetries) {
          await new Promise((resolve) => setTimeout(resolve, delay));
          delay *= 2;
          continue;
        }
        throw new QIGuardApiError(`Network error communicating with QI-Guard: ${err.message}`, 0, err);
      }
    }
  }

  /**
   * Submits a Soroban smart contract WASM bytecode or address for vulnerability analysis.
   */
  async analyzeContract(params: ContractRiskRequest): Promise<ContractRiskReport> {
    return this.request<ContractRiskReport>("/analyze/contract", {
      method: "POST",
      body: JSON.stringify(params)
    });
  }

  /**
   * Submits a Stellar address for behavioral anomaly analysis.
   */
  async analyzeBehavioral(params: BehavioralAnalysisRequest): Promise<BehavioralAnalysisReport> {
    return this.request<BehavioralAnalysisReport>("/analyze/behavioral", {
      method: "POST",
      body: JSON.stringify(params)
    });
  }

  /**
   * Retrieves quantum resilience and NIST PQC migration readiness score.
   */
  async getResilience(target: string): Promise<QuantumResilienceReport> {
    return this.request<QuantumResilienceReport>(`/resilience/${encodeURIComponent(target)}`, {
      method: "GET"
    });
  }

  /**
   * Retrieves side-by-side classical vs. hybrid model benchmark deltas for a job.
   */
  async getBenchmark(jobId: string): Promise<BenchmarkReport> {
    return this.request<BenchmarkReport>(`/benchmarks/${encodeURIComponent(jobId)}`, {
      method: "GET"
    });
  }

  /**
   * Retrieves project tier usage and quota limits.
   */
  async getUsage(projectId?: string): Promise<any> {
    const q = projectId ? `?project_id=${encodeURIComponent(projectId)}` : "";
    return this.request<any>(`/billing/usage${q}`, {
      method: "GET"
    });
  }
}
