// API service for Arealis Gateway integration
const API_URL = process.env.NEXT_PUBLIC_AREALIS_API_URL || 'http://localhost:8000';
const API_KEY = process.env.NEXT_PUBLIC_AREALIS_API_KEY || 'arealis_api_key_2024';

export interface Transaction {
  payment_type: string;
  transaction_id: string;
  sender: {
    name: string;
    account_number: string;
    ifsc_code: string;
    bank_name: string;
    kyc_verified?: boolean;
    credit_score?: number;
  };
  receiver: {
    name: string;
    account_number: string;
    ifsc_code: string;
    bank_name: string;
    kyc_verified?: boolean;
    credit_score?: number;
  };
  amount: number;
  currency: string;
  method: string;
  purpose: string;
  schedule_datetime: string;
  location: {
    city: string;
    gps_coordinates: {
      latitude: number;
      longitude: number;
    };
  };
  additional_fields: {
    employee_id?: string;
    department?: string;
    payment_frequency?: string;
    invoice_number?: string;
    invoice_date?: string;
    gst_number?: string;
    pan_number?: string;
    vendor_code?: string;
    loan_account_number?: string;
    loan_type?: string;
    sanction_date?: string;
    interest_rate?: number;
    tenure_months?: number;
    borrower_verification_status?: string;
  };
}

export interface BatchResponse {
  success: boolean;
  batch_id: string;
  message: string;
  decisions?: Array<{
    line_id: string;
    decision: string;
    policy_version: string;
    reasons: string[];
    evidence_refs: string[];
    postgres_id: number;
    neo4j_success: boolean;
  }>;
}

export interface ApiError {
  success: false;
  message: string;
  error?: string;
}

class ArealisApiService {
  private baseUrl: string;
  private apiKey: string;

  constructor() {
    this.baseUrl = API_URL;
    this.apiKey = API_KEY;
    console.log('API Service initialized:', { baseUrl: this.baseUrl, apiKey: this.apiKey });
  }

  private getHeaders(): HeadersInit {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.apiKey}`,
      'X-API-Key': this.apiKey,
    };
  }

  async processBatch(transactions: Transaction[]): Promise<BatchResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/acc/decide`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(transactions),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      const data = await response.json();
      
      // Generate batch ID
      const batchId = `B-${new Date().toISOString().split('T')[0]}-${Date.now().toString().slice(-4)}`;
      
      return {
        success: true,
        batch_id: batchId,
        message: 'Batch processed successfully',
        decisions: data.decisions || []
      };
    } catch (error) {
      console.error('API Error:', error);
      return {
        success: false,
        batch_id: '',
        message: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  async savePaymentFile(filename: string, data: any): Promise<{ success: boolean; file_id?: number; message: string }> {
    try {
      const requestBody = {
        filename,
        data
      };
      
      console.log('Saving payment file:', { 
        filename, 
        dataType: typeof data, 
        dataLength: Array.isArray(data) ? data.length : (typeof data === 'string' ? data.length : 'not array/string'),
        dataPreview: typeof data === 'string' ? data.substring(0, 100) + '...' : data
      });
      console.log('Request body:', requestBody);
      
      const response = await fetch(`${this.baseUrl}/acc/payment-file`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`;
        try {
          const errorData = await response.json();
          console.error('API Error Response:', errorData);
          
          // Handle different error formats
          if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map((err: any) => 
              `${err.loc ? err.loc.join('.') + ': ' : ''}${err.msg || err.message || JSON.stringify(err)}`
            ).join(', ');
          } else if (errorData.detail) {
            errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
          } else if (errorData.message) {
            errorMessage = errorData.message;
          } else {
            errorMessage = JSON.stringify(errorData);
          }
        } catch (e) {
          console.error('Error parsing API response:', e);
          errorMessage = response.statusText || `HTTP ${response.status}`;
        }
        throw new Error(errorMessage);
      }

      const result = await response.json();
      return {
        success: true,
        file_id: result.file_id,
        message: 'Payment file saved successfully'
      };
    } catch (error) {
      console.error('Save Payment File Error:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to save payment file'
      };
    }
  }

  async getPaymentFiles(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/acc/payment-files`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get Payment Files Error:', error);
      return { success: false, message: 'Failed to fetch payment files' };
    }
  }

  // Validate API key
  async validateApiKey(): Promise<boolean> {
    try {
      console.log('Validating API key:', { baseUrl: this.baseUrl, apiKey: this.apiKey });
      const headers = this.getHeaders();
      console.log('Request headers:', headers);
      
      const response = await fetch(`${this.baseUrl}/acc/decisions`, {
        method: 'GET',
        headers: headers,
      });
      
      console.log('API validation response:', { status: response.status, ok: response.ok });
      return response.ok;
    } catch (error) {
      console.error('API key validation error:', error);
      return false;
    }
  }
}

export const arealisApi = new ArealisApiService();
