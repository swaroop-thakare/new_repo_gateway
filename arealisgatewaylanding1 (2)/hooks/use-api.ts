/**
 * React hooks for Arealis Gateway v2 API integration
 */

import { useState, useEffect, useCallback } from 'react';
import { apiClient, type DashboardMetrics, type TransactionDetails, type WorkflowStatus, type AgentStatus } from '@/lib/api-client';

// Dashboard metrics hook
export function useDashboardMetrics() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getDashboardMetrics();
      setMetrics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch metrics');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  return { metrics, loading, error, refetch: fetchMetrics };
}

// Transactions hook
export function useTransactions(limit: number = 50, offset: number = 0) {
  const [transactions, setTransactions] = useState<TransactionDetails[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTransactions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getTransactions(limit, offset);
      setTransactions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch transactions');
    } finally {
      setLoading(false);
    }
  }, [limit, offset]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  return { transactions, loading, error, refetch: fetchTransactions };
}

// Transaction details hook
export function useTransactionDetails(transactionId: string | null) {
  const [details, setDetails] = useState<TransactionDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDetails = useCallback(async () => {
    if (!transactionId) return;
    
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getTransactionDetails(transactionId);
      setDetails(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch transaction details');
    } finally {
      setLoading(false);
    }
  }, [transactionId]);

  useEffect(() => {
    if (transactionId) {
      fetchDetails();
    }
  }, [transactionId, fetchDetails]);

  return { details, loading, error, refetch: fetchDetails };
}

// Workflow status hook
export function useWorkflowStatus(workflowId: string | null) {
  const [status, setStatus] = useState<WorkflowStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    if (!workflowId) return;
    
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getWorkflowStatus(workflowId);
      setStatus(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch workflow status');
    } finally {
      setLoading(false);
    }
  }, [workflowId]);

  useEffect(() => {
    if (workflowId) {
      fetchStatus();
      // Poll for status updates every 5 seconds
      const interval = setInterval(fetchStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [workflowId, fetchStatus]);

  return { status, loading, error, refetch: fetchStatus };
}

// Agent status hook
export function useAgentStatus() {
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAgents = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getAgentStatus();
      setAgents(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch agent status');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAgents();
    // Poll for agent status updates every 10 seconds
    const interval = setInterval(fetchAgents, 10000);
    return () => clearInterval(interval);
  }, [fetchAgents]);

  return { agents, loading, error, refetch: fetchAgents };
}

// Batch upload hook
export function useBatchUpload() {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uploadBatch = useCallback(async (batchData: any) => {
    try {
      setUploading(true);
      setError(null);
      const result = await apiClient.uploadBatch(batchData);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload batch';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setUploading(false);
    }
  }, []);

  return { uploadBatch, uploading, error };
}

// Health check hook
export function useHealthCheck() {
  const [healthy, setHealthy] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.healthCheck();
      setHealthy(data.status === 'healthy');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Health check failed');
      setHealthy(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  return { healthy, loading, error, refetch: checkHealth };
}
