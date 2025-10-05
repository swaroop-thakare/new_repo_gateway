// API utility functions for fetching data from the ACC agent backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || 'arealis_api_key_2024';

export interface VendorPaymentData {
  kpis: {
    total_paid: number;
    vendors_count: number;
    pending_approvals: number;
    avg_settlement_time: string;
  };
  charts: {
    vendor_bar_data: Array<{ vendor: string; amount: number }>;
    vendor_pie_data: Array<{ name: string; value: number }>;
  };
  invoices: Array<{
    vendor: string;
    invoice_id: string;
    amount: string;
    mode: string;
    status: string;
    date: string;
    acc_status: string;
    decision_reason: string;
  }>;
  pass_fail_breakdown: {
    pass_count: number;
    fail_count: number;
    total_transactions: number;
    pass_percentage: number;
    fail_percentage: number;
  };
}

export interface PayrollData {
  kpis: {
    this_month_volume: number;
    in_progress_runs: number;
    exceptions: number;
    avg_processing_time: string;
  };
  payroll_entries: Array<{
    id: string;
    date: string;
    entity: string;
    sub_entity: string;
    total_amount: number;
    currency: string;
    status: string;
    progress: {
      completed: number;
      failed: number;
      pending: number;
      total: number;
    };
    employees: number;
    departments: string[];
  }>;
}

export interface LoanDisbursementData {
  kpis: {
    total_disbursed: number;
    pending_approvals: number;
    success_rate: number;
    avg_time_to_disburse: string;
  };
  recent_disbursements: Array<{
    loan_id: string;
    borrower: string;
    product_type: string;
    amount: number;
    mode: string;
    status: string;
    date: string;
    acc_status: string;
    decision_reason?: string;
  }>;
}

export async function fetchVendorPayments(): Promise<VendorPaymentData | null> {
  try {
    console.log('🔍 Fetching vendor payments from:', `${API_BASE_URL}/acc/vendor-payments`);
    
    const response = await fetch(`${API_BASE_URL}/acc/vendor-payments`, {
      method: 'GET',
      mode: 'cors',
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    console.log('📡 Response status:', response.status);
    console.log('📡 Response headers:', response.headers);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ HTTP error:', response.status, errorText);
      throw new Error(`HTTP error! status: ${response.status}: ${errorText}`);
    }

    const result = await response.json();
    console.log('📊 API Response:', result);
    
    if (result.success) {
      return result.data;
    } else {
      console.error('API returned error:', result.message);
      return null;
    }
  } catch (error) {
    console.error('Error fetching vendor payments:', error);
    return null;
  }
}

export function formatCurrency(amount: number): string {
  if (amount >= 10000000) { // 1 crore
    return `₹${(amount / 10000000).toFixed(1)} Cr`;
  } else if (amount >= 100000) { // 1 lakh
    return `₹${(amount / 100000).toFixed(1)} L`;
  } else {
    return `₹${amount.toLocaleString()}`;
  }
}

export async function fetchPayrollData(): Promise<PayrollData | null> {
  try {
    console.log('🔍 Fetching payroll data from:', `${API_BASE_URL}/acc/payroll-data`);
    
    const response = await fetch(`${API_BASE_URL}/acc/payroll-data`, {
      method: 'GET',
      mode: 'cors',
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    console.log('📡 Response status:', response.status);
    console.log('📡 Response headers:', response.headers);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ HTTP error:', response.status, errorText);
      throw new Error(`HTTP error! status: ${response.status}: ${errorText}`);
    }

    const result = await response.json();
    console.log('📊 API Response:', result);
    
    if (result.success) {
      return result.data;
    } else {
      console.error('API returned error:', result.message);
      return null;
    }
  } catch (error) {
    console.error('Error fetching payroll data:', error);
    return null;
  }
}

export async function fetchLoanDisbursementData(): Promise<LoanDisbursementData | null> {
  try {
    console.log('🔍 Fetching loan disbursement data from:', `${API_BASE_URL}/acc/loan-disbursement-data`);
    
    const response = await fetch(`${API_BASE_URL}/acc/loan-disbursement-data`, {
      method: 'GET',
      mode: 'cors',
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    console.log('📡 Response status:', response.status);
    console.log('📡 Response headers:', response.headers);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ HTTP error:', response.status, errorText);
      throw new Error(`HTTP error! status: ${response.status}: ${errorText}`);
    }

    const result = await response.json();
    console.log('📊 API Response:', result);
    
    if (result.success) {
      return result.data;
    } else {
      console.error('API returned error:', result.message);
      return null;
    }
  } catch (error) {
    console.error('Error fetching loan disbursement data:', error);
    return null;
  }
}
