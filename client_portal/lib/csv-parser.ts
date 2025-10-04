// CSV parsing utility for batch upload
export interface CSVRow {
  [key: string]: string;
}

export interface ParsedTransaction {
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

function parseCSVLine(line: string): string[] {
  // Simple and reliable CSV parsing
  const fields: string[] = [];
  let current = '';
  let inQuotes = false;
  
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      fields.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  
  // Add the last field
  fields.push(current.trim());
  
  // Process fields - remove quotes and handle empty values
  return fields.map(field => {
    let processed = field.trim();
    // Remove surrounding quotes if present
    if (processed.startsWith('"') && processed.endsWith('"') && processed.length > 1) {
      processed = processed.slice(1, -1);
    }
    return processed;
  });
}

export function parseCSV(csvText: string): ParsedTransaction[] {
  console.log('🔄 Starting CSV parsing...');
  console.log('Raw CSV text length:', csvText.length);
  
  const lines = csvText.split('\n').filter(line => line.trim());
  console.log('Total lines:', lines.length);
  
  if (lines.length < 2) {
    throw new Error('CSV file must have at least a header and one data row');
  }

  // Handle potential Byte Order Mark (BOM) character
  let headerLine = lines[0];
  if (headerLine.charCodeAt(0) === 0xFEFF) {
    headerLine = headerLine.substring(1);
  }

  // Parse headers with proper CSV handling
  const headers = parseCSVLine(headerLine);
  console.log('Headers count:', headers.length);
  console.log('Headers:', headers);
  
  const transactions: ParsedTransaction[] = [];

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line || line === '') continue;
    
    console.log(`\n🔄 Processing line ${i + 1}:`, line.substring(0, 100) + '...');
    
    // Parse CSV line with proper handling of consecutive commas
    let values = parseCSVLine(line);
    console.log(`Raw values count: ${values.length}, Headers count: ${headers.length}`);
    
    // CRITICAL FIX: Ensure values array matches headers length exactly
    if (values.length !== headers.length) {
      console.log(`⚠️ Column count mismatch: ${values.length} vs ${headers.length}`);
      
      // Pad with empty strings if too few columns
      while (values.length < headers.length) {
        values.push('');
      }
      
      // Truncate if too many columns
      if (values.length > headers.length) {
        values = values.slice(0, headers.length);
      }
      
      console.log(`✅ Adjusted to ${values.length} columns`);
    }

    // Create row object with exact field mapping
    const row: CSVRow = {};
    headers.forEach((header, index) => {
      row[header] = values[index] || '';
    });
    
    console.log(`✅ Row ${i + 1} mapped successfully`);
    console.log(`Key fields - PAN: "${row.pan_number}", Invoice: "${row.invoice_number}", Status: "${row.borrower_verification_status}"`);

    try {
      const transaction = parseRowToTransaction(row, i + 1);
      transactions.push(transaction);
      console.log(`✅ Successfully parsed transaction ${i + 1}: ${transaction.transaction_id}`);
    } catch (error) {
      console.error(`❌ Error parsing row ${i + 1}:`, error);
      console.warn(`⚠️ Skipping row ${i + 1} due to parsing error`);
      continue;
    }
  }

  console.log(`\n✅ CSV Parser: Successfully parsed ${transactions.length} transactions`);
  console.log('Transaction IDs:', transactions.map(t => t.transaction_id));
  return transactions;
}

function parseRowToTransaction(row: CSVRow, rowNumber: number): ParsedTransaction {
  console.log(`🔄 Parsing row ${rowNumber}...`);
  
  // Required fields validation - be more lenient
  const requiredFields = [
    'payment_type', 'transaction_id', 'sender_name', 'sender_account_number', 'sender_ifsc_code', 'sender_bank_name',
    'receiver_name', 'receiver_account_number', 'receiver_ifsc_code', 'receiver_bank_name',
    'amount', 'currency', 'method', 'purpose', 'schedule_datetime', 'city'
  ];

  const missingFields = [];
  for (const field of requiredFields) {
    if (!row[field] || row[field].trim() === '') {
      missingFields.push(field);
    }
  }

  if (missingFields.length > 0) {
    console.error(`❌ Missing fields in row ${rowNumber}:`, missingFields);
    console.error(`Available fields:`, Object.keys(row));
    throw new Error(`Missing required fields in row ${rowNumber}: ${missingFields.join(', ')}. Available fields: ${Object.keys(row).join(', ')}`);
  }

  // Parse numeric values
  const amount = parseFloat(row.amount);
  if (isNaN(amount) || amount <= 0) {
    throw new Error(`Invalid amount '${row.amount}' in row ${rowNumber}. Must be a positive number.`);
  }

  const latitude = row.latitude ? parseFloat(row.latitude) : 0;
  const longitude = row.longitude ? parseFloat(row.longitude) : 0;

  // Parse optional numeric fields
  const interestRate = row.interest_rate ? parseFloat(row.interest_rate) : undefined;
  const tenureMonths = row.tenure_months ? parseInt(row.tenure_months) : undefined;
  const creditScore = row.credit_score ? parseInt(row.credit_score) : undefined;

  // Parse boolean fields
  const kycVerified = row.kyc_verified ? row.kyc_verified.toLowerCase() === 'true' : undefined;
  const borrowerVerificationStatus = row.borrower_verification_status?.trim() || undefined;

  // Create transaction object with dynamic field mapping
  const transaction = {
    payment_type: row.payment_type.trim(),
    transaction_id: row.transaction_id.trim(),
    sender: {
      name: row.sender_name.trim(),
      account_number: row.sender_account_number.trim(),
      ifsc_code: row.sender_ifsc_code.trim(),
      bank_name: row.sender_bank_name.trim(),
      kyc_verified: kycVerified,
      credit_score: creditScore
    },
    receiver: {
      name: row.receiver_name.trim(),
      account_number: row.receiver_account_number.trim(),
      ifsc_code: row.receiver_ifsc_code.trim(),
      bank_name: row.receiver_bank_name.trim(),
      kyc_verified: kycVerified,
      credit_score: creditScore
    },
    amount,
    currency: row.currency.trim(),
    method: row.method.trim(),
    purpose: row.purpose.trim(),
    schedule_datetime: row.schedule_datetime.trim(),
    location: {
      city: row.city.trim(),
      gps_coordinates: {
        latitude,
        longitude
      }
    },
    additional_fields: {
      employee_id: row.employee_id?.trim() || undefined,
      department: row.department?.trim() || undefined,
      payment_frequency: row.payment_frequency?.trim() || undefined,
      invoice_number: row.invoice_number?.trim() || undefined,
      invoice_date: row.invoice_date?.trim() || undefined,
      gst_number: row.gst_number?.trim() || undefined,
      pan_number: row.pan_number?.trim() || undefined,
      vendor_code: row.vendor_code?.trim() || undefined,
      loan_account_number: row.loan_account_number?.trim() || undefined,
      loan_type: row.loan_type?.trim() || undefined,
      sanction_date: row.sanction_date?.trim() || undefined,
      interest_rate: interestRate,
      tenure_months: tenureMonths,
      borrower_verification_status: borrowerVerificationStatus
    }
  };

  console.log(`✅ Row ${rowNumber} parsed successfully: ${transaction.transaction_id}`);
  console.log(`Key fields - PAN: "${transaction.additional_fields.pan_number}", Invoice: "${transaction.additional_fields.invoice_number}", Status: "${transaction.additional_fields.borrower_verification_status}"`);
  
  return transaction;
}

export function generateCSVTemplate(): string {
  return `payment_type,transaction_id,sender_name,sender_account_number,sender_ifsc_code,sender_bank_name,receiver_name,receiver_account_number,receiver_ifsc_code,receiver_bank_name,amount,currency,method,purpose,schedule_datetime,city,latitude,longitude,employee_id,department,payment_frequency,invoice_number,invoice_date,gst_number,pan_number,vendor_code,loan_account_number,loan_type,sanction_date,interest_rate,tenure_months,borrower_verification_status
payroll,TXN001,ABC Corp,1234567890,HDFC0001234,HDFC Bank,John Doe,9876543210,SBIN0001234,State Bank of India,50000,INR,NEFT,Salary Payment,2025-10-02T10:00:00Z,Mumbai,19.076,72.8777,EMP001,IT,Monthly,,,,,ABCDE1234A,,,,,,,,
vendor_payment,TXN002,XYZ Ltd,2345678901,ICIC0001234,ICICI Bank,Jane Smith,8765432109,HDFC0005678,HDFC Bank,75000,INR,RTGS,Vendor Payment,2025-10-02T11:00:00Z,Delhi,28.6139,77.2090,,,,,INV001,2025-10-01,29ABCDE1234F1Z5,VENDOR001,,,,,,,
loan_disbursement,TXN003,Loan Bank,3456789012,SBIN0005678,State Bank of India,Bob Wilson,7654321098,PNB0001234,Punjab National Bank,100000,INR,NEFT,Loan Disbursement,2025-10-02T12:00:00Z,Bangalore,12.9716,77.5946,,,,,,,,LOAN001,Personal Loan,2025-10-01,12.5,24,APPROVED`;
}
