from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import requests
import json
 
app = FastAPI(title="ACC Agent Service", version="1.1")
 
 
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
    # Stubbed output
    if pan == "ABCDE1234A":
        return {
            "data": {
                "aadhaar_seeding_status": "LINKED",
                "category": "Individual",
                "full_name": "John Doe",
                "first_name": "John",
                "middle_name": "Hartwell",
                "last_name": "Doe"
            },
            "message": "PAN is valid",
            "verification": "success",
            "traceId": "trace-123"
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
    if gstin.endswith("ZR"):
        return {
            "reference_id": 19,
            "GSTIN": gstin,
            "legal_name_of_business": "UJJIVAN SMALL FINANCE BANK LIMITED",
            "trade_name_of_business": "UJJIVAN SMALL FINANCE BANK",
            "constitution_of_business": "Public Limited Company",
            "gst_in_status": "Active",
            "valid": True,
            "message": "GSTIN Exists"
        }
    return {"valid": False, "message": "GSTIN invalid"}
 
 
def verify_bank(account: str, ifsc: str, name: str, phone: str = None) -> Dict[str, Any]:
    # Input same as Cashfree Bank Verification
    payload = {"bank_account": account, "ifsc": ifsc, "name": name, "phone": phone}
    if account.startswith("1718"):
        return {
            "reference_id": 34,
            "name_at_bank": "BHARATHTEST GKUMARUT",
            "bank_name": "YES BANK",
            "branch": "SANTACRUZ, MUMBAI",
            "name_match_score": "90.00",
            "name_match_result": "GOOD_PARTIAL_MATCH",
            "account_status": "VALID",
            "account_status_code": "ACCOUNT_IS_VALID"
        }
    return {
        "account_status": "INVALID",
        "name_match_score": "20",
        "name_match_result": "MISMATCH"
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
        
        # Make HTTP request to OPA
        response = requests.post(
            opa_url,
            json=opa_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # Check if request was successful
        if response.status_code == 200:
            return response.json()
        else:
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
def acc_decide(transactions: List[Transaction] = Body(...)):
    results = []
 
    for txn in transactions:
        verifications = {}
 
        if txn.additional_fields.pan_number:
            verifications["pan"] = verify_pan(txn.additional_fields.pan_number)
        # No direct Aadhaar verification as it's sensitive data
        if txn.additional_fields.gst_number:
            verifications["gstin"] = verify_gstin(txn.additional_fields.gst_number, txn.receiver.name)
        if txn.receiver.account_number and txn.receiver.ifsc_code:
            verifications["bank"] = verify_bank(
                txn.receiver.account_number,
                txn.receiver.ifsc_code,
                txn.receiver.name,
                None  # Phone is optional
            )
 
        try:
            opa_input = {
                "policy_version": "acc-1.4.2",
                "transaction": txn.dict(),
                "verifications": verifications
            }
            opa_result = call_opa(opa_input)
 
            results.append({
            "line_id": txn.transaction_id,
            "decision": "PASS" if opa_result["result"]["allow"] else "FAIL",
            "policy_version": "acc-1.4.2",
            "reasons": opa_result["result"].get("violations", []),
            "evidence_refs": list(verifications.keys())
        })
        except Exception as e:
            results.append({
                "line_id": txn.transaction_id,
                "decision": "ERROR",
                "policy_version": "acc-1.4.2",
                "reasons": [str(e)],
                "evidence_refs": []
            })
 
    return {"decisions": results}