/**
 * API Client for Arealis Gateway v2 Backend Integration
 * 
 * This client handles communication between the Next.js frontend
 * and the Python backend services.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8020';

export interface TransactionData {
  transactionId: string;
  date: string;
  beneficiary: string;
  amount: number;
  currency: string;
  purpose: string;
  transactionType?: string;
  creditScore?: number;
  reference?: string;
}

export interface BatchData {
  batch_id: string;
  tenant_id: string;
  source: string;
  upload_ts: string;
  transactions: TransactionData[];
}

export interface WorkflowStatus {
  workflow_id: string;
  batch_id: string;
  status: string;
  current_layer?: string;
  current_agent?: string;
  start_time: string;
  last_update: string;
  errors: string[];
}

export interface DashboardMetrics {
  total_disbursed: number;
  loans_processed: number;
  success_rate: number;
  batches_awaiting: number;
}

export interface TransactionDetails {
  id: string;
  date: string;
  beneficiary: string;
  amount: number;
  currency: string;
  status: string;
  stage: string;
  product: string;
  creditScore: number;
  reference: string;
  workflow_id: string;
  processing_steps: Array<{
    step: string;
    status: string;
    timestamp: string;
    agent: string;
  }>;
  audit_trail: Array<{
    action: string;
    timestamp: string;
    actor: string;
  }>;
}

export interface AgentStatus {
  name: string;
  layer: string;
  status: string;
  dependencies: string[];
  last_run?: string;
  error_count: number;
  service_url?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Batch Management
  async uploadBatch(batchData: BatchData): Promise<{ workflow_id: string; batch_id: string; status: string; message: string }> {
    return this.request('/api/v1/batches/upload', {
      method: 'POST',
      body: JSON.stringify(batchData),
    });
  }

  async uploadBatchFile(file: File, tenantId: string, batchId?: string): Promise<{ message: string; batch_id: string }> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("tenant_id", tenantId);
    if (batchId) {
      formData.append("batch_id", batchId);
    }

    const response = await fetch(`${this.baseUrl}/api/v1/batches/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Failed to upload batch: ${errorData.detail || response.statusText}`);
    }
    return response.json();
  }

  async getWorkflowStatus(workflowId: string): Promise<WorkflowStatus> {
    return this.request(`/api/v1/workflows/${workflowId}/status`);
  }

  // Dashboard
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    return this.request('/api/v1/dashboard/metrics');
  }

  // Transactions
  async getTransactions(limit: number = 50, offset: number = 0): Promise<TransactionDetails[]> {
    return this.request(`/api/v1/transactions?limit=${limit}&offset=${offset}`);
  }

  async getTransactionDetails(transactionId: string): Promise<TransactionDetails> {
    return this.request(`/api/v1/transactions/${transactionId}`);
  }

  // Agents
  async getAgentStatus(): Promise<AgentStatus[]> {
    return this.request('/api/v1/agents');
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; service: string; version: string; timestamp: string }> {
    return this.request('/api/v1/health');
  }
}

// Create singleton instance
export const apiClient = new ApiClient();

// Export individual functions for easier imports
export const uploadBatchFile = (file: File, tenantId: string, batchId?: string) => 
  apiClient.uploadBatchFile(file, tenantId, batchId);

export const fetchDashboardMetrics = () => apiClient.getDashboardMetrics();
export const fetchTransactions = () => apiClient.getTransactions();
export const fetchAgentStatus = () => apiClient.getAgentStatus();
export const fetchWorkflowStatus = (workflowId: string) => apiClient.getWorkflowStatus(workflowId);
export const healthCheck = () => apiClient.healthCheck();

// Export types
export type {
  TransactionData,
  BatchData,
  WorkflowStatus,
  DashboardMetrics,
  TransactionDetails,
  AgentStatus,
};
