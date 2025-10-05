"""
PDR (Payment Decision Router) Models
Pydantic models for the PDR system including rail configurations, scoring, and decisions.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, time
from decimal import Decimal
from enum import Enum


# ========================================
# Enums for Type Safety
# ========================================

class PaymentType(str, Enum):
    PAYROLL = "payroll"
    VENDOR_PAYMENT = "vendor_payment"
    LOAN_DISBURSEMENT = "loan_disbursement"
    GENERAL_TRANSFER = "general_transfer"


class RailType(str, Enum):
    INSTANT = "INSTANT"
    BATCH = "BATCH"
    REALTIME = "REALTIME"


class SettlementType(str, Enum):
    INSTANT = "INSTANT"
    IMMEDIATE = "IMMEDIATE"
    BATCH = "BATCH"
    DELAYED = "DELAYED"


class DecisionStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"


class ExecutionStatus(str, Enum):
    PENDING = "PENDING"
    EXECUTING = "EXECUTING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


class IntentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ========================================
# Base Models
# ========================================

class GPSCoordinates(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")


class Location(BaseModel):
    city: str = Field(..., min_length=1, max_length=100)
    gps_coordinates: Optional[GPSCoordinates] = None


class Party(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    account_number: str = Field(..., min_length=1, max_length=50)
    ifsc_code: str = Field(..., min_length=11, max_length=11, pattern=r'^[A-Z]{4}0[A-Z0-9]{6}$')
    bank_name: str = Field(..., min_length=1, max_length=255)
    kyc_verified: Optional[bool] = None
    credit_score: Optional[int] = Field(None, ge=300, le=900)


# ========================================
# Intent Models (Input)
# ========================================

class AdditionalFields(BaseModel):
    """Flexible additional fields for different payment types"""
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


class Intent(BaseModel):
    """Payment intent from user/system"""
    transaction_id: str = Field(..., min_length=1, max_length=100)
    payment_type: PaymentType
    
    # Parties
    sender: Party
    receiver: Party
    
    # Transaction details
    amount: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)
    ifsc_code: str = Field(..., min_length=11, max_length=11, pattern=r'^[A-Z]{4}0[A-Z0-9]{6}$')
    method: Optional[str] = Field(None, max_length=50)
    purpose: str = Field(..., min_length=1, max_length=500)
    schedule_datetime: datetime
    
    # Location
    location: Optional[Location] = None
    
    # Additional fields
    additional_fields: Optional[AdditionalFields] = AdditionalFields()
    
    # Metadata
    status: IntentStatus = IntentStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ========================================
# ACC Models (Compliance)
# ========================================

class ACCDecision(BaseModel):
    """ACC (Anti-Compliance Check) decision result"""
    transaction_id: str
    line_id: str
    decision: DecisionStatus
    policy_version: str
    reasons: List[str] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
    compliance_penalty: float = Field(default=0.0, ge=0, le=100)
    risk_score: float = Field(default=0.0, ge=0, le=100)
    created_at: Optional[datetime] = None


# ========================================
# Rail Configuration Models
# ========================================

class RailConfig(BaseModel):
    """Rail configuration and characteristics"""
    rail_name: str = Field(..., min_length=1, max_length=50)
    rail_type: RailType
    
    # Amount constraints
    min_amount: Decimal = Field(default=Decimal('0'), ge=0)
    max_amount: Decimal = Field(default=Decimal('999999999'), gt=0)
    new_user_limit: Decimal = Field(default=Decimal('50000'), ge=0)
    
    # Operational constraints
    working_hours_start: time = Field(default=time(0, 0))
    working_hours_end: time = Field(default=time(23, 59, 59))
    working_days: List[int] = Field(default=[1, 2, 3, 4, 5, 6, 7])  # 1=Monday, 7=Sunday
    
    # Performance characteristics
    avg_eta_ms: int = Field(..., gt=0, description="Average ETA in milliseconds")
    cost_bps: Decimal = Field(default=Decimal('0'), ge=0, description="Cost in basis points")
    success_probability: float = Field(default=0.95, ge=0, le=1)
    
    # Settlement characteristics
    settlement_type: SettlementType = SettlementType.INSTANT
    settlement_certainty: float = Field(default=1.0, ge=0, le=1)
    
    # API configuration
    api_endpoint: Optional[str] = None
    api_method: str = Field(default="POST")
    api_headers: Dict[str, str] = Field(default_factory=dict)
    
    # Status and limits
    is_active: bool = Field(default=True)
    daily_limit: Decimal = Field(default=Decimal('999999999'))
    daily_limit_remaining: Optional[Decimal] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ========================================
# Scoring Models
# ========================================

class RailFeatures(BaseModel):
    """Raw features for a rail before normalization"""
    rail_name: str
    eta_ms: int
    cost_bps: float
    success_prob: float
    compliance_penalty: float
    risk_score: float
    critic_penalty_decay: float = Field(default=0.0, description="Recent failure penalty")
    window_bonus: float = Field(default=0.0, description="Load balancing bonus")
    amount_match_bonus: float = Field(default=0.5, description="How well rail fits amount")
    working_hours_penalty: float = Field(default=0.0, description="Penalty for waiting")
    settlement_certainty: float = Field(default=1.0, description="Settlement reliability")


class NormalizedFeatures(BaseModel):
    """Normalized features (0-1 scale) for scoring"""
    rail_name: str
    eta_n: float = Field(..., ge=0, le=1)
    cost_n: float = Field(..., ge=0, le=1)
    succ_n: float = Field(..., ge=0, le=1)
    comp_n: float = Field(..., ge=0, le=1)
    risk_n: float = Field(..., ge=0, le=1)
    crit_n: float = Field(..., ge=0, le=1)
    win_n: float = Field(..., ge=0, le=1)
    amt_n: float = Field(..., ge=0, le=1)
    wh_n: float = Field(..., ge=0, le=1)
    setl_n: float = Field(..., ge=0, le=1)


class ScoringWeights(BaseModel):
    """Weights for the scoring formula"""
    w_eta: float = Field(default=0.15, ge=0, le=1, description="Speed weight")
    w_cost: float = Field(default=0.12, ge=0, le=1, description="Cost weight")
    w_succ: float = Field(default=0.22, ge=0, le=1, description="Success probability weight")
    w_comp: float = Field(default=0.18, ge=0, le=1, description="Compliance weight")
    w_risk: float = Field(default=0.12, ge=0, le=1, description="Risk weight")
    w_crit: float = Field(default=0.05, ge=0, le=1, description="Critic penalty weight")
    w_win: float = Field(default=0.02, ge=0, le=1, description="Window bonus weight")
    w_amt: float = Field(default=0.08, ge=0, le=1, description="Amount match weight")
    w_wh: float = Field(default=0.04, ge=0, le=1, description="Working hours weight")
    w_setl: float = Field(default=0.02, ge=0, le=1, description="Settlement certainty weight")
    
    @validator('*', pre=True)
    def validate_weights_sum(cls, v, values):
        """Ensure weights sum to approximately 1.0"""
        if len(values) == 9:  # All weights are set
            total = sum(values.values()) + v
            if not (0.95 <= total <= 1.05):
                raise ValueError(f"Weights must sum to approximately 1.0, got {total}")
        return v


class RailScore(BaseModel):
    """Final score for a rail"""
    rail_name: str
    score: float = Field(..., ge=0, le=1)
    normalized_features: NormalizedFeatures
    raw_features: RailFeatures


# ========================================
# PDR Decision Models (Output)
# ========================================

class FallbackRail(BaseModel):
    """Fallback rail with score"""
    rail_name: str
    score: float


class PDRDecision(BaseModel):
    """PDR decision output"""
    transaction_id: str
    
    # Primary selection
    primary_rail: str
    primary_rail_score: float
    
    # Fallbacks (ordered by score)
    fallback_rails: List[FallbackRail] = Field(default_factory=list)
    
    # Scoring details for audit/explainability
    scoring_features: Dict[str, Any] = Field(default_factory=dict)
    scoring_weights: ScoringWeights = ScoringWeights()
    
    # Execution tracking
    execution_status: ExecutionStatus = ExecutionStatus.PENDING
    current_rail_attempt: Optional[str] = None
    attempt_count: int = Field(default=0, ge=0)
    
    # Results
    final_rail_used: Optional[str] = None
    final_utr_number: Optional[str] = None
    final_status: Optional[ExecutionStatus] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ========================================
# Rail Performance Tracking
# ========================================

class RailPerformance(BaseModel):
    """Track rail performance for learning"""
    rail_name: str
    transaction_id: str
    actual_eta_ms: Optional[int] = None
    success: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


# ========================================
# PDR Agent Input/Output Models
# ========================================

class DebitAccountDetails(BaseModel):
    """Debit account details"""
    debitAccountNumber: str = Field(..., description="Debit account number")
    accountHolderName: str = Field(..., description="Remitter name")
    ifscCode: str = Field(..., description="IFSC code")
    bankName: str = Field(..., description="Bank name")


class CreditAccountDetails(BaseModel):
    """Credit account details"""
    creditAccountNumber: str = Field(..., description="Credit account number")
    accountHolderName: str = Field(..., description="Beneficiary name")
    ifscCode: str = Field(..., description="IFSC code")
    bankName: str = Field(..., description="Bank name")


class BankResponse(BaseModel):
    """Bank API response"""
    responseCode: str = Field(..., description="Bank response code")
    isSuccess: bool = Field(..., description="Success flag")
    utrNumber: Optional[str] = Field(None, description="UTR number")


class PDRTaskRequest(BaseModel):
    """PDR Agent input schema"""
    task_type: str = "pdr"
    batch_id: str = Field(..., description="Batch ID")
    line_id: str = Field(..., description="Transaction ID")
    intent: str = Field(..., description="Classified intent")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk score")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    amount: float = Field(..., gt=0, description="Amount in INR")
    currency: str = Field(default="INR", description="Currency")
    DebitAccountDetails: DebitAccountDetails
    CreditAccountDetails: CreditAccountDetails
    transactionType: str = Field(..., description="Transaction type")
    sourceReferenceNumber: str = Field(..., description="Bank reference")
    evidence_ref: str = Field(..., description="S3 URI")
    policy_version: str = Field(default="pdr-1.0.1", description="Policy version")
    bank_response: Optional[BankResponse] = None


class RouteDetails(BaseModel):
    """Route details for routing plan"""
    channel: str = Field(..., description="Payment rail")
    psp: str = Field(..., description="Payment Service Provider")
    cost_bps: int = Field(..., ge=0, description="Cost in basis points")
    eta_ms: int = Field(..., gt=0, description="Estimated time in milliseconds")
    success_prob: float = Field(..., ge=0.0, le=1.0, description="Success probability")


class RoutingPlan(BaseModel):
    """Routing plan structure"""
    primary_route: RouteDetails
    fallback_routes: List[RouteDetails] = Field(default_factory=list)


class PDRTaskResult(BaseModel):
    """PDR Agent output schema"""
    task_type: str = "pdr_result"
    batch_id: str = Field(..., description="Batch ID")
    line_id: str = Field(..., description="Transaction ID")
    status: str = Field(..., description="Status (SUCCESS, FAILED, HOLD)")
    routing_plan: Optional[RoutingPlan] = None
    issues: List[str] = Field(default_factory=list, description="Issues if failed")
    evidence_ref: str = Field(..., description="S3 URI for results")
    timestamp: str = Field(..., description="Processing timestamp")


# ========================================
# Legacy API Request/Response Models
# ========================================

class PDRRequest(BaseModel):
    """Request to PDR service"""
    intents: List[Intent] = Field(..., min_items=1)
    force_recompute: bool = Field(default=False)
    scoring_weights: Optional[ScoringWeights] = None


class PDRResponse(BaseModel):
    """Response from PDR service"""
    decisions: List[PDRDecision]
    total_processed: int
    total_successful: int
    total_failed: int
    processing_time_ms: float


class RailExecutionRequest(BaseModel):
    """Request to execute a rail"""
    transaction_id: str
    rail_name: str
    intent: Intent
    retry_attempt: int = Field(default=0, ge=0)


class RailExecutionResponse(BaseModel):
    """Response from rail execution"""
    transaction_id: str
    rail_name: str
    success: bool
    utr_number: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: int
    response_data: Optional[Dict[str, Any]] = None


# ========================================
# Mock Rail API Models (Axis Bank Format)
# ========================================

class SubHeader(BaseModel):
    """Common sub-header for Axis Bank APIs"""
    requestUUID: str
    serviceRequestId: str
    serviceRequestVersion: str = "1.0"
    channelId: str = "TEST"


class DebitAccountInformation(BaseModel):
    """Debit account information"""
    debitAccountNumber: str
    debitAccountHolderName: Optional[str] = None
    debitNarration: Optional[str] = None


class CreditAccountInformation(BaseModel):
    """Credit account information"""
    creditAccountNumber: str
    creditAccountHolderName: Optional[str] = None
    creditNarration: Optional[str] = None
    ifscCode: str
    bankName: Optional[str] = None


class DebitAccountDetails(BaseModel):
    DebitAccountInformation: DebitAccountInformation


class CreditAccountDetails(BaseModel):
    CreditAccountInformation: CreditAccountInformation


# IMPS Models
class IMPSFundsTransferRequestBody(BaseModel):
    serviceProviderId: str = "serviceProviderId"
    requestId: str
    requestType: str = "R"
    remittorMobileNumber: str
    remittorMMId: str
    remittorName: str
    remittorAccountNumber: str
    beneficiaryIFSC: str
    beneficiaryAccountNo: str
    amount: str
    remarks: str
    txnInitChannel: str = "INET"
    checksum: str
    beneficiaryName: str


class IMPSFundsTransferRequest(BaseModel):
    IMPSFundsTransferRequestBody: IMPSFundsTransferRequestBody
    SubHeader: SubHeader


class IMPSFundsTransferResponseBody(BaseModel):
    responseCode: str
    isSuccess: bool
    failureReason: str
    requestId: str
    retrivalReferenceNo: str
    transactionDate: str
    beneficiaryName: Optional[str] = None
    checksum: str


class IMPSFundsTransferResponse(BaseModel):
    SubHeader: SubHeader
    IMPSFundsTransferResponseBody: IMPSFundsTransferResponseBody


# NEFT Models
class NEFTPaymentIntiationRequestBody(BaseModel):
    transactionAmount: str
    sourceReferenceNumber: str
    DebitAccountDetails: DebitAccountDetails
    CreditAccountDetails: CreditAccountDetails


class NEFTPaymentInitiationRequest(BaseModel):
    SubHeader: SubHeader
    NEFTPaymentIntiationRequestBody: NEFTPaymentIntiationRequestBody


class NEFTPaymentIntiationResponseBody(BaseModel):
    utrNumber: str
    code: str
    result: str


class NEFTPaymentInitiationResponse(BaseModel):
    SubHeader: SubHeader
    NEFTPaymentIntiationResponseBody: NEFTPaymentIntiationResponseBody


# RTGS Models (similar structure to NEFT)
class RTGSPaymentIntiationRequestBody(BaseModel):
    transactionAmount: str
    sourceReferenceNumber: str
    DebitAccountDetails: DebitAccountDetails
    CreditAccountDetails: CreditAccountDetails


class RTGSPaymentInitiationRequest(BaseModel):
    SubHeader: SubHeader
    RTGSPaymentIntiationRequestBody: RTGSPaymentIntiationRequestBody


class RTGSPaymentIntiationResponseBody(BaseModel):
    utrNumber: str
    code: str
    result: str


class RTGSPaymentInitiationResponse(BaseModel):
    SubHeader: SubHeader
    RTGSPaymentIntiationResponseBody: RTGSPaymentIntiationResponseBody


# IFT Models
class IFTPaymentIntiationRequestBody(BaseModel):
    transactionAmount: str
    sourceReferenceNumber: str
    remarks: str
    DebitAccountDetails: DebitAccountDetails
    CreditAccountDetails: CreditAccountDetails


class IFTPaymentInitiationRequest(BaseModel):
    SubHeader: SubHeader
    IFTPaymentIntiationRequestBody: IFTPaymentIntiationRequestBody


class IFTPaymentIntiationResponseBody(BaseModel):
    utrNumber: str
    code: str
    result: str


class IFTPaymentInitiationResponse(BaseModel):
    SubHeader: SubHeader
    IFTPaymentIntiationResponseBody: IFTPaymentIntiationResponseBody