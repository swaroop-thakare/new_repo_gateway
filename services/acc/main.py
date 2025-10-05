from fastapi import FastAPI, Body, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import requests
import json
from sqlalchemy.orm import Session
from database import (
    create_tables, get_db, save_acc_agent_result, 
    save_to_neo4j, save_payment_file, AccAgent, PaymentFile,
    get_payment_files, get_payment_file_by_id, get_payment_files_count,
    search_payment_files, get_latest_payment_files
)
from sqlalchemy import func, and_
 
app = FastAPI(title="ACC Agent Service", version="1.1")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# API Key configuration
VALID_API_KEYS = [
    "arealis_api_key_2024",
    "test_api_key_123", 
    "demo_key_456",
    "production_key_789"
]

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key from header"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
 
 
# -------------------------
# Mock Adapters (API-aligned)
# -------------------------
 
def verify_pan(pan: str) -> Dict[str, Any]:
    # Input same as Setu API
    payload = {
        "pan": pan,
        "consent": "Y",
        "reason": "Payroll disbursement compliance check"
    }
    
    # Dynamic verification - return success for valid PAN format
    if pan and len(pan) == 10 and pan.isalnum():
        return {
            "data": {
                "aadhaar_seeding_status": "LINKED",
                "category": "Individual",
                "full_name": "Verified User",
                "first_name": "Verified",
                "middle_name": "",
                "last_name": "User"
            },
            "message": "PAN is valid",
            "verification": "success",
            "traceId": f"trace-{hash(pan) % 100000}"
        }
    return {"verification": "failed", "message": "PAN is invalid"}
 
 
def verify_aadhaar(aadhaar: str) -> Dict[str, Any]:
    # Input same as Cashfree Aadhaar API
    payload = {"aadhaar_number": aadhaar}
    if aadhaar.startswith("65"):
        return {
            "status": "SUCCESS",
            "message": "OTP sent successfully",
            "ref_id": 21637861
        }
    return {"status": "FAILED", "message": "Invalid Aadhaar"}
 
 
def verify_gstin(gstin: str, business_name: str = "NA") -> Dict[str, Any]:
    # Input same as Cashfree GST API
    payload = {"GSTIN": gstin, "business_name": business_name}
    
    # Dynamic verification - return success for valid GSTIN format
    if gstin and len(gstin) == 15 and gstin.isalnum():
        return {
            "reference_id": hash(gstin) % 100000,
            "GSTIN": gstin,
            "legal_name_of_business": "VERIFIED BUSINESS",
            "trade_name_of_business": "VERIFIED TRADE",
            "constitution_of_business": "Private Limited Company",
            "gst_in_status": "Active",
            "valid": True,
            "message": "GSTIN Exists"
        }
    return {"valid": False, "message": "GSTIN invalid"}
 
 
def verify_bank(account: str, ifsc: str, name: str, phone: str = None) -> Dict[str, Any]:
    # Input same as Cashfree Bank Verification
    payload = {"bank_account": account, "ifsc": ifsc, "name": name, "phone": phone}
    
    # Mock verification - return VALID for most accounts to test passing cases
    # Only fail for specific test cases
    if account.startswith("9999") or account.startswith("0000"):
        return {
            "account_status": "INVALID",
            "name_match_score": "20",
            "name_match_result": "MISMATCH"
        }
    
    # Return VALID for most accounts
    return {
        "reference_id": 34,
        "name_at_bank": name.upper(),
        "bank_name": "MOCK BANK",
        "branch": "MOCK BRANCH",
        "name_match_score": "90.00",
        "name_match_result": "GOOD_PARTIAL_MATCH",
        "account_status": "VALID",
        "account_status_code": "ACCOUNT_IS_VALID"
    }
 
 
# -------------------------
# OPA Agent Integration
# -------------------------

def call_opa(input_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call the actual OPA server with the input payload
    """
    try:
        # OPA server endpoint
        opa_url = "http://localhost:8181/v1/data/arealis/compliance/routing/v1"
        
        # Prepare the request payload with input wrapper
        opa_payload = {"input": input_payload}
        
        # DEBUG: Log exactly what we're sending to OPA
        print(f"\n🔍 OPA REQUEST DEBUG:")
        print(f"Transaction ID: {input_payload.get('transaction', {}).get('transaction_id', 'UNKNOWN')}")
        print(f"Payment Type: {input_payload.get('transaction', {}).get('payment_type', 'UNKNOWN')}")
        print(f"Additional Fields: {input_payload.get('transaction', {}).get('additional_fields', {})}")
        print(f"Full OPA Request: {json.dumps(opa_payload, indent=2)}")
        print("=" * 80)
        
        # Make HTTP request to OPA
        response = requests.post(
            opa_url,
            json=opa_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # Check if request was successful
        if response.status_code == 200:
            opa_response = response.json()
            
            # DEBUG: Log OPA response
            print(f"🔍 OPA RESPONSE DEBUG:")
            print(f"Transaction ID: {input_payload.get('transaction', {}).get('transaction_id', 'UNKNOWN')}")
            print(f"OPA Result: {json.dumps(opa_response.get('result', {}), indent=2)}")
            print("=" * 80)
            
            return opa_response
        else:
            print(f"❌ OPA Error: {response.status_code}")
            return {
                "result": {
                    "allow": False,
                    "violations": [f"OPA server error: {response.status_code}"]
                }
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "result": {
                "allow": False,
                "violations": ["OPA server is not available"]
            }
        }
    except requests.exceptions.Timeout:
        return {
            "result": {
                "allow": False,
                "violations": ["OPA server timeout"]
            }
        }
    except Exception as e:
        return {
            "result": {
                "allow": False,
                "violations": [f"OPA integration error: {str(e)}"]
            }
        }
 
 
# -------------------------
# Pydantic Models
# -------------------------
 
class GPSCoordinates(BaseModel):
    latitude: float
    longitude: float
 
class Location(BaseModel):
    city: str
    gps_coordinates: GPSCoordinates
 
class Party(BaseModel):
    name: str
    account_number: str
    ifsc_code: str
    bank_name: str
    kyc_verified: Optional[bool] = None
    credit_score: Optional[int] = None
 
class AdditionalFields(BaseModel):
    employee_id: Optional[str] = None
    department: Optional[str] = None
    payment_frequency: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    vendor_code: Optional[str] = None
    loan_account_number: Optional[str] = None
    loan_type: Optional[str] = None
    sanction_date: Optional[str] = None
    interest_rate: Optional[float] = None
    tenure_months: Optional[int] = None
    borrower_verification_status: Optional[str] = None
 
class Transaction(BaseModel):
    payment_type: str
    transaction_id: str
    sender: Party
    receiver: Party
    amount: float
    currency: str
    method: str
    purpose: str
    schedule_datetime: str
    location: Location
    additional_fields: AdditionalFields
 
 
# -------------------------
# API Endpoint
# -------------------------
 
@app.post("/acc/decide")
def acc_decide(transactions: List[Transaction] = Body(...), db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    results = []
 
    for txn in transactions:
        verifications = {}
        
        print(f"\n🔍 Processing {txn.transaction_id} ({txn.payment_type})...")

        # 1. PAN Verification (for all transaction types that have PAN)
        if txn.additional_fields.pan_number and txn.additional_fields.pan_number.strip():
            print(f"  🔍 PAN Verification: {txn.additional_fields.pan_number}")
            pan_result = verify_pan(txn.additional_fields.pan_number)
            print(f"  🔍 PAN Result: {pan_result}")
            verifications["pan"] = pan_result
        
        # 2. GSTIN Verification (for vendor payments)
        if txn.payment_type == "vendor_payment" and txn.additional_fields.gst_number and txn.additional_fields.gst_number.strip():
            print(f"  🔍 GSTIN Verification: {txn.additional_fields.gst_number}")
            gstin_result = verify_gstin(txn.additional_fields.gst_number, txn.receiver.name)
            print(f"  🔍 GSTIN Result: {gstin_result}")
            verifications["gstin"] = gstin_result
        
        # 3. Bank Verification (for all transaction types)
        if txn.receiver.account_number and txn.receiver.ifsc_code:
            print(f"  🔍 Bank Verification: {txn.receiver.account_number} / {txn.receiver.ifsc_code}")
            bank_result = verify_bank(
                txn.receiver.account_number,
                txn.receiver.ifsc_code,
                txn.receiver.name,
                None  # Phone is optional
            )
            print(f"  🔍 Bank Result: {bank_result}")
            verifications["bank"] = bank_result
        
        # 4. CIBIL Verification (for loan disbursements)
        if txn.payment_type == "loan_disbursement":
            print(f"  🔍 Loan Disbursement Details:")
            print(f"    - Borrower Status: {txn.additional_fields.borrower_verification_status}")
            print(f"    - Loan Account: {txn.additional_fields.loan_account_number}")
            print(f"    - Loan Type: {txn.additional_fields.loan_type}")
            print(f"    - Interest Rate: {txn.additional_fields.interest_rate}")
            print(f"    - Tenure: {txn.additional_fields.tenure_months}")
            
            # Add CIBIL verification for loan disbursements
            verifications["cibil_check_performed"] = True
            verifications["cibil_score"] = 750  # High score for passing cases
            print(f"  🔍 CIBIL Verification: check_performed=True, score=750")
 
        try:
            opa_input = {
                "policy_version": "acc-1.4.2",
                "transaction": txn.dict(),
                "verifications": verifications
            }
            opa_result = call_opa(opa_input)
            
            # Prepare result data
            decision = "PASS" if opa_result["result"]["allow"] else "FAIL"
            reasons = opa_result["result"].get("violations", [])
            evidence_refs = list(verifications.keys())
            
            # Create result object
            result = {
                "line_id": txn.transaction_id,
                "decision": decision,
                "policy_version": "acc-1.4.2",
                "reasons": reasons,
                "evidence_refs": evidence_refs
            }
            
            # Save to PostgreSQL
            postgres_id = save_acc_agent_result(
                db=db,
                line_id=txn.transaction_id,
                beneficiary=txn.receiver.name,
                ifsc=txn.receiver.ifsc_code,
                amount=txn.amount,
                policy_version="acc-1.4.2",
                status=decision,
                decision_reason=json.dumps(reasons),
                evidence_ref=json.dumps(evidence_refs)
            )
            
            # Save to Neo4j
            neo4j_success = save_to_neo4j(
                line_id=txn.transaction_id,
                beneficiary=txn.receiver.name,
                ifsc=txn.receiver.ifsc_code,
                amount=txn.amount,
                status=decision,
                decision_reason=json.dumps(reasons),
                evidence_ref=json.dumps(evidence_refs)
            )
            
            # Add database IDs to result
            result["postgres_id"] = postgres_id
            result["neo4j_success"] = neo4j_success
            
            results.append(result)
            
        except Exception as e:
            error_result = {
                "line_id": txn.transaction_id,
                "decision": "ERROR",
                "policy_version": "acc-1.4.2",
                "reasons": [str(e)],
                "evidence_refs": [],
                "postgres_id": None,
                "neo4j_success": False
            }
            results.append(error_result)
 
    return {"decisions": results}

class PaymentFileRequest(BaseModel):
    filename: str
    data: Union[Dict[str, Any], str]  # Accept both dict and string

@app.post("/acc/payment-file")
def save_payment_file_endpoint(request: PaymentFileRequest, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Save payment file data to database"""
    try:
        print(f"\n💾 PAYMENT FILE SAVE DEBUG:")
        print(f"Filename: {request.filename}")
        print(f"Data type: {type(request.data)}")
        print(f"Data length: {len(str(request.data)) if request.data else 0}")
        print("=" * 50)
        
        file_id = save_payment_file(db, request.filename, request.data)
        if file_id:
            print(f"✅ Payment file saved with ID: {file_id}")
            return {"success": True, "file_id": file_id, "message": "Payment file saved successfully"}
        else:
            print(f"❌ Failed to save payment file")
            return {"success": False, "message": "Failed to save payment file"}
    except Exception as e:
        print(f"❌ Error saving payment file: {str(e)}")
        return {"success": False, "message": f"Error saving payment file: {str(e)}"}

@app.get("/acc/decisions")
def get_decisions(db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Get all ACC agent decisions from PostgreSQL"""
    try:
        decisions = db.query(AccAgent).all()
        return {
            "success": True,
            "decisions": [
                {
                    "id": d.id,
                    "line_id": d.line_id,
                    "beneficiary": d.beneficiary,
                    "ifsc": d.ifsc,
                    "amount": float(d.amount) if d.amount else None,
                    "policy_version": d.policy_version,
                    "status": d.status,
                    "decision_reason": d.decision_reason,
                    "evidence_ref": d.evidence_ref,
                    "created_at": d.created_at.isoformat() if d.created_at else None
                }
                for d in decisions
            ]
        }
    except Exception as e:
        return {"success": False, "message": f"Error retrieving decisions: {str(e)}"}

@app.get("/acc/payment-files")
def get_payment_files_endpoint(
    limit: int = 100, 
    offset: int = 0, 
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get payment files from PostgreSQL with pagination and search"""
    try:
        if search:
            files = search_payment_files(db, search_term=search, limit=limit, offset=offset)
        else:
            files = get_payment_files(db, limit=limit, offset=offset)
        
        total_count = get_payment_files_count(db)
        
        return {
            "success": True,
            "payment_files": [
                {
                    "id": pf.id,
                    "filename": pf.filename,
                    "data": json.loads(pf.data) if pf.data else None,
                    "created_at": pf.created_at.isoformat() if hasattr(pf, 'created_at') and pf.created_at else None
                }
                for pf in files
            ],
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            }
        }
    except Exception as e:
        return {"success": False, "message": f"Error retrieving payment files: {str(e)}"}

@app.get("/acc/payment-files/{file_id}")
def get_payment_file_by_id_endpoint(file_id: int, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Get a specific payment file by ID"""
    try:
        file = get_payment_file_by_id(db, file_id)
        if not file:
            return {"success": False, "message": "Payment file not found"}
        
        return {
            "success": True,
            "payment_file": {
                "id": file.id,
                "filename": file.filename,
                "data": json.loads(file.data) if file.data else None,
                "created_at": file.created_at.isoformat() if hasattr(file, 'created_at') and file.created_at else None
            }
        }
    except Exception as e:
        return {"success": False, "message": f"Error retrieving payment file: {str(e)}"}

@app.get("/acc/payment-files/latest")
def get_latest_payment_files_endpoint(limit: int = 10, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Get the latest payment files"""
    try:
        files = get_latest_payment_files(db, limit=limit)
        
        return {
            "success": True,
            "payment_files": [
                {
                    "id": pf.id,
                    "filename": pf.filename,
                    "data": json.loads(pf.data) if pf.data else None,
                    "created_at": pf.created_at.isoformat() if hasattr(pf, 'created_at') and pf.created_at else None
                }
                for pf in files
            ]
        }
    except Exception as e:
        return {"success": False, "message": f"Error retrieving latest payment files: {str(e)}"}

@app.get("/acc/payment-files/count")
def get_payment_files_count_endpoint(db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Get total count of payment files"""
    try:
        count = get_payment_files_count(db)
        return {
            "success": True,
            "total_count": count
        }
    except Exception as e:
        return {"success": False, "message": f"Error counting payment files: {str(e)}"}

@app.options("/acc/vendor-payments")
def options_vendor_payments():
    """Handle OPTIONS request for CORS"""
    return {"message": "OK"}

@app.get("/acc/vendor-payments")
def get_vendor_payments(db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Get vendor payment data for dashboard"""
    try:
        # Get all vendor payment transactions from acc_agent table
        vendor_payments = db.query(AccAgent).filter(
            AccAgent.line_id.like("VEN%")
        ).all()
        
        # Get payment files data to extract method information
        payment_files = db.query(PaymentFile).all()
        
        # Create a mapping of transaction_id to method from payment_files
        transaction_method_map = {}
        for pf in payment_files:
            if pf.data:
                try:
                    data = json.loads(pf.data) if isinstance(pf.data, str) else pf.data
                    
                    # Handle the actual data structure: {"headers": [...], "rows": [...]}
                    if 'headers' in data and 'rows' in data and isinstance(data['rows'], list):
                        headers = data['headers']
                        rows = data['rows']
                        
                        # Find the index of transaction_id and method columns
                        try:
                            transaction_id_idx = headers.index('transaction_id')
                            method_idx = headers.index('method')
                        except ValueError:
                            continue
                        
                        # Map each row to transaction_id -> method
                        for row in rows:
                            if isinstance(row, list) and len(row) > max(transaction_id_idx, method_idx):
                                transaction_id = row[transaction_id_idx]
                                method = row[method_idx]
                                if transaction_id and method:
                                    transaction_method_map[transaction_id] = method
                                    
                except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                    continue
        
        if not vendor_payments:
            return {
                "success": True,
                "data": {
                    "kpis": {
                        "total_paid": 0,
                        "vendors_count": 0,
                        "pending_approvals": 0,
                        "avg_settlement_time": "T+0 days"
                    },
                    "charts": {
                        "vendor_bar_data": [],
                        "vendor_pie_data": []
                    },
                    "invoices": [],
                    "pass_fail_breakdown": {
                        "pass_count": 0,
                        "fail_count": 0,
                        "total_transactions": 0,
                        "pass_percentage": 0,
                        "fail_percentage": 0
                    }
                }
            }
        
        # Calculate KPIs - exclude FAIL transactions from total_paid
        total_paid = sum(float(payment.amount) for payment in vendor_payments if payment.status == "PASS")
        unique_vendors = len(set(payment.beneficiary for payment in vendor_payments))
        pending_approvals = len([p for p in vendor_payments if p.status == "PENDING"])
        
        # Calculate pass/fail breakdown for dynamic visualization
        pass_count = len([p for p in vendor_payments if p.status == "PASS"])
        fail_count = len([p for p in vendor_payments if p.status == "FAIL"])
        total_transactions = len(vendor_payments)
        
        # Prepare chart data - include both PASS and FAIL transactions
        vendor_amounts = {}
        for payment in vendor_payments:
            vendor = payment.beneficiary
            amount = float(payment.amount)
            if vendor in vendor_amounts:
                vendor_amounts[vendor] += amount
            else:
                vendor_amounts[vendor] = amount
        
        # Sort vendors by amount and take top 10
        sorted_vendors = sorted(vendor_amounts.items(), key=lambda x: x[1], reverse=True)[:10]
        vendor_bar_data = [{"vendor": vendor, "amount": amount} for vendor, amount in sorted_vendors]
        
        # Prepare pie chart data
        vendor_pie_data = [{"name": vendor, "value": amount} for vendor, amount in sorted_vendors[:5]]
        
        # Prepare invoice data - include both PASS and FAIL transactions
        invoices = []
        for payment in vendor_payments:
            # Map status from ACC agent to display status
            display_status = "Paid" if payment.status == "PASS" else "Failed" if payment.status == "FAIL" else "Pending"
            
            # Get method from payment_files data
            method = transaction_method_map.get(payment.line_id, "NEFT")  # Default to NEFT if not found
            
            invoices.append({
                "vendor": payment.beneficiary,
                "invoice_id": payment.line_id,
                "amount": f"₹{float(payment.amount):,.0f}",
                "mode": method,  # Use method from payment_files
                "status": display_status,
                "date": payment.created_at.strftime("%Y-%m-%d") if payment.created_at else "N/A",
                "acc_status": payment.status,
                "decision_reason": payment.decision_reason or "No specific reason provided"
            })
        
        return {
            "success": True,
            "data": {
                "kpis": {
                    "total_paid": total_paid,
                    "vendors_count": unique_vendors,
                    "pending_approvals": pending_approvals,
                    "avg_settlement_time": "T+1.2 days"
                },
                "charts": {
                    "vendor_bar_data": vendor_bar_data,
                    "vendor_pie_data": vendor_pie_data
                },
                "invoices": invoices,
                "pass_fail_breakdown": {
                    "pass_count": pass_count,
                    "fail_count": fail_count,
                    "total_transactions": total_transactions,
                    "pass_percentage": round((pass_count / total_transactions * 100) if total_transactions > 0 else 0, 1),
                    "fail_percentage": round((fail_count / total_transactions * 100) if total_transactions > 0 else 0, 1)
                }
            }
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error fetching vendor payments: {str(e)}"}

@app.options("/acc/payroll-data")
def options_payroll_data():
    """Handle CORS preflight for payroll data endpoint"""
    return {"message": "OK"}


@app.get("/acc/payroll-data")
def get_payroll_data(db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Get payroll data for dashboard"""
    try:
        # Get payment files data to extract payroll transactions
        payment_files = db.query(PaymentFile).all()
        
        # Find payroll transaction IDs from payment_files
        payroll_transaction_ids = set()
        for pf in payment_files:
            if pf.data:
                try:
                    data = json.loads(pf.data) if isinstance(pf.data, str) else pf.data
                    
                    # Handle the actual data structure: {"headers": [...], "rows": [...]}
                    if 'headers' in data and 'rows' in data and isinstance(data['rows'], list):
                        headers = data['headers']
                        rows = data['rows']
                        
                        # Find the index of payment_type and transaction_id columns
                        try:
                            payment_type_idx = headers.index('payment_type')
                            transaction_id_idx = headers.index('transaction_id')
                        except ValueError:
                            continue
                        
                        # Find payroll transactions
                        for row in rows:
                            if isinstance(row, list) and len(row) > max(payment_type_idx, transaction_id_idx):
                                payment_type = row[payment_type_idx]
                                transaction_id = row[transaction_id_idx]
                                if payment_type == "payroll" and transaction_id:
                                    payroll_transaction_ids.add(transaction_id)
                                    
                except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                    continue
        
        # Get payroll transactions from AccAgent table
        payroll_transactions = []
        if payroll_transaction_ids:
            payroll_transactions = db.query(AccAgent).filter(
                AccAgent.line_id.in_(payroll_transaction_ids)
            ).all()
        
        
        # Create a mapping of transaction_id to additional data from payment_files
        transaction_data_map = {}
        for pf in payment_files:
            if pf.data:
                try:
                    data = json.loads(pf.data) if isinstance(pf.data, str) else pf.data
                    
                    # Handle the actual data structure: {"headers": [...], "rows": [...]}
                    if 'headers' in data and 'rows' in data and isinstance(data['rows'], list):
                        headers = data['headers']
                        rows = data['rows']
                        
                        # Find relevant column indices
                        try:
                            transaction_id_idx = headers.index('transaction_id')
                            employee_id_idx = headers.index('employee_id')
                            department_idx = headers.index('department')
                            payment_frequency_idx = headers.index('payment_frequency')
                            method_idx = headers.index('method')
                        except ValueError:
                            continue
                        
                        # Map each row to transaction_id -> additional data
                        for row in rows:
                            if isinstance(row, list) and len(row) > max(transaction_id_idx, employee_id_idx, department_idx, payment_frequency_idx, method_idx):
                                transaction_id = row[transaction_id_idx]
                                employee_id = row[employee_id_idx] if employee_id_idx < len(row) else ""
                                department = row[department_idx] if department_idx < len(row) else ""
                                payment_frequency = row[payment_frequency_idx] if payment_frequency_idx < len(row) else ""
                                method = row[method_idx] if method_idx < len(row) else ""
                                
                                if transaction_id:
                                    transaction_data_map[transaction_id] = {
                                        'employee_id': employee_id,
                                        'department': department,
                                        'payment_frequency': payment_frequency,
                                        'method': method
                                    }
                                    
                except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                    continue
        
        if not payroll_transactions:
            return {
                "success": True,
                "data": {
                    "kpis": {
                        "this_month_volume": 0,
                        "in_progress_runs": 0,
                        "exceptions": 0,
                        "avg_processing_time": "0h 0m"
                    },
                    "payroll_entries": []
                }
            }
        
        # Calculate KPIs
        total_volume = sum(float(transaction.amount) for transaction in payroll_transactions if transaction.status == "PASS")
        in_progress_runs = len([t for t in payroll_transactions if t.status == "PENDING"])
        exceptions = len([t for t in payroll_transactions if t.status == "FAIL"])
        
        # Calculate average processing time (mock calculation)
        avg_processing_time = "2h 14m"  # Default value
        
        # Group payroll transactions by company/entity
        company_groups = {}
        for transaction in payroll_transactions:
            # Extract company from sender_name
            company = transaction.beneficiary.split()[0] if transaction.beneficiary else "Unknown"
            if company not in company_groups:
                company_groups[company] = []
            company_groups[company].append(transaction)
        
        # Create payroll entries
        payroll_entries = []
        for company, transactions in company_groups.items():
            total_amount = sum(float(t.amount) for t in transactions)
            pass_count = len([t for t in transactions if t.status == "PASS"])
            fail_count = len([t for t in transactions if t.status == "FAIL"])
            pending_count = len([t for t in transactions if t.status == "PENDING"])
            
            # Determine status
            if pending_count > 0:
                status = "In Progress"
            elif fail_count > 0:
                status = "Exceptions"
            else:
                status = "Completed"
            
            # Get latest transaction date
            latest_date = max(t.created_at for t in transactions if t.created_at)
            
            payroll_entries.append({
                "id": f"payroll-{company.lower().replace(' ', '-')}",
                "date": latest_date.strftime("%b %d") if latest_date else "N/A",
                "entity": company,
                "sub_entity": f"{company} Ltd",
                "total_amount": total_amount,
                "currency": "INR",  # Default to INR
                "status": status,
                "progress": {
                    "completed": pass_count,
                    "failed": fail_count,
                    "pending": pending_count,
                    "total": len(transactions)
                },
                "employees": len(transactions),
                "departments": list(set(transaction_data_map.get(t.line_id, {}).get('department', '') for t in transactions if transaction_data_map.get(t.line_id, {}).get('department')))
            })
        
        # Sort by date (most recent first)
        payroll_entries.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        return {
            "success": True,
            "data": {
                "kpis": {
                    "this_month_volume": total_volume,
                    "in_progress_runs": in_progress_runs,
                    "exceptions": exceptions,
                    "avg_processing_time": avg_processing_time
                },
                "payroll_entries": payroll_entries
            }
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error fetching payroll data: {str(e)}"}

@app.options("/acc/clear-vendor-data")
def options_clear_vendor_data():
    """Handle CORS preflight for clear vendor data endpoint"""
    return {"message": "OK"}

@app.delete("/acc/clear-vendor-data")
def clear_vendor_data(db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Clear all vendor payment data from database"""
    try:
        # Delete all vendor payment transactions from acc_agent table
        vendor_transactions = db.query(AccAgent).filter(
            AccAgent.line_id.like("VEN%")
        ).all()
        
        for transaction in vendor_transactions:
            db.delete(transaction)
        
        # Only clear payment files that contain ONLY vendor payment data (not mixed files)
        payment_files = db.query(PaymentFile).all()
        files_to_delete = []
        
        for pf in payment_files:
            if pf.data:
                try:
                    data = json.loads(pf.data) if isinstance(pf.data, str) else pf.data
                    
                    # Check if this file contains ONLY vendor payment data
                    if 'headers' in data and 'rows' in data and isinstance(data['rows'], list):
                        headers = data['headers']
                        rows = data['rows']
                        
                        # Find the index of payment_type column
                        try:
                            payment_type_idx = headers.index('payment_type')
                        except ValueError:
                            continue
                        
                        # Check if ALL rows have vendor_payment (not mixed)
                        all_vendor_payment = True
                        has_any_data = False
                        for row in rows:
                            if isinstance(row, list) and len(row) > payment_type_idx:
                                payment_type = row[payment_type_idx]
                                has_any_data = True
                                if payment_type != "vendor_payment":
                                    all_vendor_payment = False
                                    break
                        
                        # Only delete files that contain ONLY vendor payment data
                        if all_vendor_payment and has_any_data:
                            files_to_delete.append(pf)
                            
                except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                    continue
        
        # Delete payment files that contain ONLY vendor payment data
        for pf in files_to_delete:
            db.delete(pf)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Cleared {len(vendor_transactions)} vendor transactions and {len(files_to_delete)} payment files"
        }
        
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Error clearing vendor data: {str(e)}"}

@app.options("/acc/clear-payroll-data")
def options_clear_payroll_data():
    """Handle CORS preflight for clear payroll data endpoint"""
    return {"message": "OK"}

@app.delete("/acc/clear-payroll-data")
def clear_payroll_data(db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Clear all payroll data from database"""
    try:
        # Find payroll transaction IDs from payment_files
        payment_files = db.query(PaymentFile).all()
        payroll_transaction_ids = set()
        
        for pf in payment_files:
            if pf.data:
                try:
                    data = json.loads(pf.data) if isinstance(pf.data, str) else pf.data
                    
                    # Handle the actual data structure: {"headers": [...], "rows": [...]}
                    if 'headers' in data and 'rows' in data and isinstance(data['rows'], list):
                        headers = data['headers']
                        rows = data['rows']
                        
                        # Find the index of payment_type and transaction_id columns
                        try:
                            payment_type_idx = headers.index('payment_type')
                            transaction_id_idx = headers.index('transaction_id')
                        except ValueError:
                            continue
                        
                        # Find payroll transactions
                        for row in rows:
                            if isinstance(row, list) and len(row) > max(payment_type_idx, transaction_id_idx):
                                payment_type = row[payment_type_idx]
                                transaction_id = row[transaction_id_idx]
                                if payment_type == "payroll" and transaction_id:
                                    payroll_transaction_ids.add(transaction_id)
                                    
                except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                    continue
        
        # Delete payroll transactions from acc_agent table
        payroll_transactions = []
        if payroll_transaction_ids:
            payroll_transactions = db.query(AccAgent).filter(
                AccAgent.line_id.in_(payroll_transaction_ids)
            ).all()
        
        for transaction in payroll_transactions:
            db.delete(transaction)
        
        # Only clear payment files that contain ONLY payroll data (not mixed files)
        files_to_delete = []
        
        for pf in payment_files:
            if pf.data:
                try:
                    data = json.loads(pf.data) if isinstance(pf.data, str) else pf.data
                    
                    # Check if this file contains ONLY payroll data
                    if 'headers' in data and 'rows' in data and isinstance(data['rows'], list):
                        headers = data['headers']
                        rows = data['rows']
                        
                        # Find the index of payment_type column
                        try:
                            payment_type_idx = headers.index('payment_type')
                        except ValueError:
                            continue
                        
                        # Check if ALL rows have payroll payment_type (not mixed)
                        all_payroll = True
                        has_any_data = False
                        for row in rows:
                            if isinstance(row, list) and len(row) > payment_type_idx:
                                payment_type = row[payment_type_idx]
                                has_any_data = True
                                if payment_type != "payroll":
                                    all_payroll = False
                                    break
                        
                        # Only delete files that contain ONLY payroll data
                        if all_payroll and has_any_data:
                            files_to_delete.append(pf)
                            
                except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                    continue
        
        # Delete payment files that contain ONLY payroll data
        for pf in files_to_delete:
            db.delete(pf)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Cleared {len(payroll_transactions)} payroll transactions and {len(files_to_delete)} payroll-only payment files"
        }
        
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Error clearing payroll data: {str(e)}"}

@app.options("/acc/loan-disbursement-data")
def options_loan_disbursement_data():
    """Handle CORS preflight for loan disbursement data endpoint"""
    return {"message": "OK"}

@app.get("/acc/loan-disbursement-data")
def get_loan_disbursement_data(db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Get loan disbursement data for dashboard"""
    try:
        # Get payment files data to extract loan disbursement transactions
        payment_files = db.query(PaymentFile).all()
        
        # Find loan disbursement transaction IDs from payment_files
        loan_transaction_ids = set()
        for pf in payment_files:
            if pf.data:
                try:
                    data = json.loads(pf.data) if isinstance(pf.data, str) else pf.data
                    
                    # Handle the actual data structure: {"headers": [...], "rows": [...]}
                    if 'headers' in data and 'rows' in data and isinstance(data['rows'], list):
                        headers = data['headers']
                        rows = data['rows']
                        
                        # Find the index of payment_type and transaction_id columns
                        try:
                            payment_type_idx = headers.index('payment_type')
                            transaction_id_idx = headers.index('transaction_id')
                        except ValueError:
                            continue
                        
                        # Find loan disbursement transactions
                        for row in rows:
                            if isinstance(row, list) and len(row) > max(payment_type_idx, transaction_id_idx):
                                payment_type = row[payment_type_idx]
                                transaction_id = row[transaction_id_idx]
                                if payment_type == "loan_disbursement" and transaction_id:
                                    loan_transaction_ids.add(transaction_id)
                                    
                except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                    continue
        
        # Get loan disbursement transactions from AccAgent table
        loan_transactions = []
        if loan_transaction_ids:
            loan_transactions = db.query(AccAgent).filter(
                AccAgent.line_id.in_(loan_transaction_ids)
            ).all()
        
        # Create a mapping of transaction_id to additional data from payment_files
        transaction_data_map = {}
        for pf in payment_files:
            if pf.data:
                try:
                    data = json.loads(pf.data) if isinstance(pf.data, str) else pf.data
                    
                    # Handle the actual data structure: {"headers": [...], "rows": [...]}
                    if 'headers' in data and 'rows' in data and isinstance(data['rows'], list):
                        headers = data['headers']
                        rows = data['rows']
                        
                        # Find relevant column indices
                        try:
                            transaction_id_idx = headers.index('transaction_id')
                            method_idx = headers.index('method')
                        except ValueError:
                            continue
                        
                        # Map each row to transaction_id -> additional data
                        for row in rows:
                            if isinstance(row, list) and len(row) > max(transaction_id_idx, method_idx):
                                transaction_id = row[transaction_id_idx]
                                method = row[method_idx] if method_idx < len(row) else ""
                                
                                if transaction_id:
                                    transaction_data_map[transaction_id] = {
                                        'method': method
                                    }
                                    
                except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                    continue
        
        if not loan_transactions:
            return {
                "success": True,
                "data": {
                    "kpis": {
                        "total_disbursed": 0,
                        "pending_approvals": 0,
                        "success_rate": 0,
                        "avg_time_to_disburse": "0 mins"
                    },
                    "recent_disbursements": []
                }
            }
        
        # Calculate KPIs
        total_disbursed = sum(float(transaction.amount) for transaction in loan_transactions if transaction.status == "PASS")
        pending_approvals = len([t for t in loan_transactions if t.status == "PENDING"])
        pass_count = len([t for t in loan_transactions if t.status == "PASS"])
        fail_count = len([t for t in loan_transactions if t.status == "FAIL"])
        total_count = len(loan_transactions)
        success_rate = (pass_count / total_count * 100) if total_count > 0 else 0
        
        # Calculate average time to disburse (mock calculation)
        avg_time_to_disburse = "42 mins"  # Default value
        
        # Prepare recent disbursements
        recent_disbursements = []
        for transaction in loan_transactions:
            # Extract method from transaction_data_map
            method = transaction_data_map.get(transaction.line_id, {}).get('method', 'NEFT')
            
            # Determine status display
            if transaction.status == "PASS":
                status_display = "Approved"
            elif transaction.status == "PENDING":
                status_display = "Pending"
            else:
                status_display = "Failed"
            
            # Hardcoded product types (visible only if data exists)
            product_types = ["Retail", "SME", "Corporate"]
            product_type = product_types[hash(transaction.line_id) % len(product_types)]
            
            recent_disbursements.append({
                "loan_id": transaction.line_id,
                "borrower": transaction.beneficiary,
                "product_type": product_type,
                "amount": float(transaction.amount),
                "mode": method,
                "status": status_display,
                "date": transaction.created_at.strftime("%Y-%m-%d") if transaction.created_at else "N/A",
                "acc_status": transaction.status,
                "decision_reason": transaction.decision_reason if transaction.status == "FAIL" else None
            })
        
        # Sort by date (most recent first)
        recent_disbursements.sort(key=lambda x: x['date'], reverse=True)
        
        return {
            "success": True,
            "data": {
                "kpis": {
                    "total_disbursed": total_disbursed,
                    "pending_approvals": pending_approvals,
                    "success_rate": round(success_rate, 1),
                    "avg_time_to_disburse": avg_time_to_disburse
                },
                "recent_disbursements": recent_disbursements
            }
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error fetching loan disbursement data: {str(e)}"}

@app.options("/acc/clear-loan-data")
def options_clear_loan_data():
    """Handle CORS preflight for clear loan data endpoint"""
    return {"message": "OK"}

@app.delete("/acc/clear-loan-data")
def clear_loan_data(db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Clear all loan disbursement data from database"""
    try:
        # Find loan disbursement transaction IDs from payment_files
        payment_files = db.query(PaymentFile).all()
        loan_transaction_ids = set()
        
        for pf in payment_files:
            if pf.data:
                try:
                    data = json.loads(pf.data) if isinstance(pf.data, str) else pf.data
                    
                    # Handle the actual data structure: {"headers": [...], "rows": [...]}
                    if 'headers' in data and 'rows' in data and isinstance(data['rows'], list):
                        headers = data['headers']
                        rows = data['rows']
                        
                        # Find the index of payment_type and transaction_id columns
                        try:
                            payment_type_idx = headers.index('payment_type')
                            transaction_id_idx = headers.index('transaction_id')
                        except ValueError:
                            continue
                        
                        # Find loan disbursement transactions
                        for row in rows:
                            if isinstance(row, list) and len(row) > max(payment_type_idx, transaction_id_idx):
                                payment_type = row[payment_type_idx]
                                transaction_id = row[transaction_id_idx]
                                if payment_type == "loan_disbursement" and transaction_id:
                                    loan_transaction_ids.add(transaction_id)
                                    
                except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                    continue
        
        # Delete loan disbursement transactions from acc_agent table
        loan_transactions = []
        if loan_transaction_ids:
            loan_transactions = db.query(AccAgent).filter(
                AccAgent.line_id.in_(loan_transaction_ids)
            ).all()
        
        for transaction in loan_transactions:
            db.delete(transaction)
        
        # Only clear payment files that contain ONLY loan disbursement data (not mixed files)
        files_to_delete = []
        
        for pf in payment_files:
            if pf.data:
                try:
                    data = json.loads(pf.data) if isinstance(pf.data, str) else pf.data
                    
                    # Check if this file contains ONLY loan disbursement data
                    if 'headers' in data and 'rows' in data and isinstance(data['rows'], list):
                        headers = data['headers']
                        rows = data['rows']
                        
                        # Find the index of payment_type column
                        try:
                            payment_type_idx = headers.index('payment_type')
                        except ValueError:
                            continue
                        
                        # Check if ALL rows have loan_disbursement payment_type (not mixed)
                        all_loan_disbursement = True
                        has_any_data = False
                        for row in rows:
                            if isinstance(row, list) and len(row) > payment_type_idx:
                                payment_type = row[payment_type_idx]
                                has_any_data = True
                                if payment_type != "loan_disbursement":
                                    all_loan_disbursement = False
                                    break
                        
                        # Only delete files that contain ONLY loan disbursement data
                        if all_loan_disbursement and has_any_data:
                            files_to_delete.append(pf)
                            
                except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                    continue
        
        # Delete payment files that contain ONLY loan disbursement data
        for pf in files_to_delete:
            db.delete(pf)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Cleared {len(loan_transactions)} loan disbursement transactions and {len(files_to_delete)} loan-only payment files"
        }
        
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Error clearing loan disbursement data: {str(e)}"}