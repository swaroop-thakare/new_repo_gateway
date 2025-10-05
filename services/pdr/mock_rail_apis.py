"""
Mock Rail API Implementations
Simulates Axis Bank API endpoints for IMPS, NEFT, RTGS, IFT with realistic responses.
"""

import uuid
import random
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from decimal import Decimal

from models import (
    Intent, RailExecutionRequest, RailExecutionResponse,
    IMPSFundsTransferRequest, IMPSFundsTransferResponse,
    NEFTPaymentInitiationRequest, NEFTPaymentInitiationResponse,
    RTGSPaymentInitiationRequest, RTGSPaymentInitiationResponse,
    IFTPaymentInitiationRequest, IFTPaymentInitiationResponse,
    SubHeader, DebitAccountDetails, CreditAccountDetails,
    DebitAccountInformation, CreditAccountInformation,
    IMPSFundsTransferRequestBody, IMPSFundsTransferResponseBody,
    NEFTPaymentIntiationRequestBody, NEFTPaymentIntiationResponseBody,
    RTGSPaymentIntiationRequestBody, RTGSPaymentIntiationResponseBody,
    IFTPaymentIntiationRequestBody, IFTPaymentIntiationResponseBody
)


class MockRailAPIs:
    """
    Mock implementations of Axis Bank rail APIs.
    Simulates realistic success/failure scenarios with proper response formats.
    """
    
    def __init__(self):
        self.success_rates = {
            "IMPS": 0.96,
            "NEFT": 0.94,
            "RTGS": 0.99,
            "IFT": 0.99,
            "UPI": 0.98
        }
        
        # Track API call counts for simulation
        self.call_counts = {rail: 0 for rail in self.success_rates.keys()}
    
    def execute_rail(self, request: RailExecutionRequest) -> RailExecutionResponse:
        """
        Main entry point for rail execution.
        Routes to appropriate rail-specific implementation.
        """
        start_time = time.time()
        
        try:
            if request.rail_name == "IMPS":
                result = self._execute_imps(request)
            elif request.rail_name == "NEFT":
                result = self._execute_neft(request)
            elif request.rail_name == "RTGS":
                result = self._execute_rtgs(request)
            elif request.rail_name == "IFT":
                result = self._execute_ift(request)
            elif request.rail_name == "UPI":
                result = self._execute_upi(request)
            else:
                result = RailExecutionResponse(
                    transaction_id=request.transaction_id,
                    rail_name=request.rail_name,
                    success=False,
                    error_code="UNSUPPORTED_RAIL",
                    error_message=f"Rail {request.rail_name} is not supported",
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )
        except Exception as e:
            result = RailExecutionResponse(
                transaction_id=request.transaction_id,
                rail_name=request.rail_name,
                success=False,
                error_code="INTERNAL_ERROR",
                error_message=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        result.execution_time_ms = int((time.time() - start_time) * 1000)
        return result
    
    def _execute_imps(self, request: RailExecutionRequest) -> RailExecutionResponse:
        """Execute IMPS transfer"""
        self.call_counts["IMPS"] += 1
        
        # Simulate processing delay
        time.sleep(random.uniform(1.5, 3.0))
        
        # Determine success based on success rate and various factors
        success = self._should_succeed("IMPS", request)
        
        if success:
            # Generate mock IMPS request/response
            imps_request = self._build_imps_request(request)
            imps_response = self._build_imps_success_response(imps_request)
            
            return RailExecutionResponse(
                transaction_id=request.transaction_id,
                rail_name="IMPS",
                success=True,
                utr_number=imps_response.IMPSFundsTransferResponseBody.retrivalReferenceNo,
                execution_time_ms=0,  # Will be set by caller
                response_data=imps_response.dict()
            )
        else:
            # Simulate failure
            error_code, error_message = self._get_imps_error()
            return RailExecutionResponse(
                transaction_id=request.transaction_id,
                rail_name="IMPS",
                success=False,
                error_code=error_code,
                error_message=error_message,
                execution_time_ms=0
            )
    
    def _execute_neft(self, request: RailExecutionRequest) -> RailExecutionResponse:
        """Execute NEFT transfer"""
        self.call_counts["NEFT"] += 1
        
        # NEFT has longer processing time (batch processing)
        time.sleep(random.uniform(5.0, 10.0))
        
        success = self._should_succeed("NEFT", request)
        
        if success:
            neft_request = self._build_neft_request(request)
            neft_response = self._build_neft_success_response(neft_request)
            
            return RailExecutionResponse(
                transaction_id=request.transaction_id,
                rail_name="NEFT",
                success=True,
                utr_number=neft_response.NEFTPaymentIntiationResponseBody.utrNumber,
                execution_time_ms=0,
                response_data=neft_response.dict()
            )
        else:
            error_code, error_message = self._get_neft_error()
            return RailExecutionResponse(
                transaction_id=request.transaction_id,
                rail_name="NEFT",
                success=False,
                error_code=error_code,
                error_message=error_message,
                execution_time_ms=0
            )
    
    def _execute_rtgs(self, request: RailExecutionRequest) -> RailExecutionResponse:
        """Execute RTGS transfer"""
        self.call_counts["RTGS"] += 1
        
        # RTGS is fast but has working hours constraints
        time.sleep(random.uniform(0.3, 1.0))
        
        # Check if within RTGS working hours (9 AM - 4:30 PM on weekdays)
        current_time = datetime.now()
        if not self._is_rtgs_working_hours(current_time):
            return RailExecutionResponse(
                transaction_id=request.transaction_id,
                rail_name="RTGS",
                success=False,
                error_code="OUTSIDE_WORKING_HOURS",
                error_message="RTGS is not available outside working hours (9 AM - 4:30 PM, Mon-Fri)",
                execution_time_ms=0
            )
        
        success = self._should_succeed("RTGS", request)
        
        if success:
            rtgs_request = self._build_rtgs_request(request)
            rtgs_response = self._build_rtgs_success_response(rtgs_request)
            
            return RailExecutionResponse(
                transaction_id=request.transaction_id,
                rail_name="RTGS",
                success=True,
                utr_number=rtgs_response.RTGSPaymentIntiationResponseBody.utrNumber,
                execution_time_ms=0,
                response_data=rtgs_response.dict()
            )
        else:
            error_code, error_message = self._get_rtgs_error()
            return RailExecutionResponse(
                transaction_id=request.transaction_id,
                rail_name="RTGS",
                success=False,
                error_code=error_code,
                error_message=error_message,
                execution_time_ms=0
            )
    
    def _execute_ift(self, request: RailExecutionRequest) -> RailExecutionResponse:
        """Execute IFT (Intra-bank Fund Transfer)"""
        self.call_counts["IFT"] += 1
        
        # IFT is very fast (intra-bank)
        time.sleep(random.uniform(0.1, 0.5))
        
        # Check if it's actually intra-bank
        if not self._is_intra_bank(request.intent):
            return RailExecutionResponse(
                transaction_id=request.transaction_id,
                rail_name="IFT",
                success=False,
                error_code="NOT_INTRA_BANK",
                error_message="IFT is only available for intra-bank transfers",
                execution_time_ms=0
            )
        
        success = self._should_succeed("IFT", request)
        
        if success:
            ift_request = self._build_ift_request(request)
            ift_response = self._build_ift_success_response(ift_request)
            
            return RailExecutionResponse(
                transaction_id=request.transaction_id,
                rail_name="IFT",
                success=True,
                utr_number=ift_response.IFTPaymentIntiationResponseBody.utrNumber,
                execution_time_ms=0,
                response_data=ift_response.dict()
            )
        else:
            error_code, error_message = self._get_ift_error()
            return RailExecutionResponse(
                transaction_id=request.transaction_id,
                rail_name="IFT",
                success=False,
                error_code=error_code,
                error_message=error_message,
                execution_time_ms=0
            )
    
    def _execute_upi(self, request: RailExecutionRequest) -> RailExecutionResponse:
        """Execute UPI transfer (mock implementation)"""
        self.call_counts["UPI"] += 1
        
        # UPI is very fast
        time.sleep(random.uniform(0.5, 2.0))
        
        success = self._should_succeed("UPI", request)
        
        if success:
            utr_number = f"UPI{datetime.now().strftime('%y%m%d')}{random.randint(100000, 999999)}"
            
            return RailExecutionResponse(
                transaction_id=request.transaction_id,
                rail_name="UPI",
                success=True,
                utr_number=utr_number,
                execution_time_ms=0,
                response_data={
                    "upi_transaction_id": utr_number,
                    "status": "SUCCESS",
                    "message": "Transaction completed successfully"
                }
            )
        else:
            error_code, error_message = self._get_upi_error()
            return RailExecutionResponse(
                transaction_id=request.transaction_id,
                rail_name="UPI",
                success=False,
                error_code=error_code,
                error_message=error_message,
                execution_time_ms=0
            )
    
    # ========================================
    # Helper Methods
    # ========================================
    
    def _should_succeed(self, rail_name: str, request: RailExecutionRequest) -> bool:
        """Determine if a rail execution should succeed based on various factors"""
        base_success_rate = self.success_rates[rail_name]
        
        # Reduce success rate for retries
        retry_penalty = request.retry_attempt * 0.1
        adjusted_rate = max(0.1, base_success_rate - retry_penalty)
        
        # Add some randomness based on amount (very large amounts might have higher failure rate)
        if request.intent.amount > Decimal('1000000'):  # > 10 Lakh
            adjusted_rate *= 0.9
        
        return random.random() < adjusted_rate
    
    def _is_rtgs_working_hours(self, current_time: datetime) -> bool:
        """Check if current time is within RTGS working hours"""
        weekday = current_time.weekday()  # 0=Monday, 6=Sunday
        if weekday >= 5:  # Saturday or Sunday
            return False
        
        hour = current_time.hour
        minute = current_time.minute
        
        # RTGS: 9:00 AM to 4:30 PM
        start_time = 9 * 60  # 9:00 AM in minutes
        end_time = 16 * 60 + 30  # 4:30 PM in minutes
        current_minutes = hour * 60 + minute
        
        return start_time <= current_minutes <= end_time
    
    def _is_intra_bank(self, intent: Intent) -> bool:
        """Check if transfer is intra-bank"""
        sender_bank_code = intent.sender.ifsc_code[:4]
        receiver_bank_code = intent.receiver.ifsc_code[:4]
        return sender_bank_code == receiver_bank_code
    
    # ========================================
    # Request Builders
    # ========================================
    
    def _build_imps_request(self, request: RailExecutionRequest) -> IMPSFundsTransferRequest:
        """Build IMPS API request"""
        intent = request.intent
        request_uuid = str(uuid.uuid4())
        
        return IMPSFundsTransferRequest(
            IMPSFundsTransferRequestBody=IMPSFundsTransferRequestBody(
                requestId=request.transaction_id,
                remittorMobileNumber="919999999999",  # Mock
                remittorMMId="9211222",  # Mock
                remittorName=intent.sender.name,
                remittorAccountNumber=intent.sender.account_number,
                beneficiaryIFSC=intent.receiver.ifsc_code,
                beneficiaryAccountNo=intent.receiver.account_number,
                amount=str(intent.amount),
                remarks=intent.purpose[:50],  # Truncate if too long
                checksum=str(random.randint(1000000000, 9999999999)),
                beneficiaryName=intent.receiver.name
            ),
            SubHeader=SubHeader(
                requestUUID=request_uuid,
                serviceRequestId="DMZ.IMPSFundTransferAPI.POST.001"
            )
        )
    
    def _build_neft_request(self, request: RailExecutionRequest) -> NEFTPaymentInitiationRequest:
        """Build NEFT API request"""
        intent = request.intent
        request_uuid = str(uuid.uuid4())
        
        return NEFTPaymentInitiationRequest(
            SubHeader=SubHeader(
                requestUUID=request_uuid,
                serviceRequestId="NB.GEN.PDT.ELIG"
            ),
            NEFTPaymentIntiationRequestBody=NEFTPaymentIntiationRequestBody(
                transactionAmount=str(intent.amount),
                sourceReferenceNumber=request.transaction_id,
                DebitAccountDetails=DebitAccountDetails(
                    DebitAccountInformation=DebitAccountInformation(
                        debitAccountNumber=intent.sender.account_number,
                        debitAccountHolderName=intent.sender.name
                    )
                ),
                CreditAccountDetails=CreditAccountDetails(
                    CreditAccountInformation=CreditAccountInformation(
                        bankName=intent.receiver.bank_name,
                        creditAccountNumber=intent.receiver.account_number,
                        creditAccountHolderName=intent.receiver.name,
                        ifscCode=intent.receiver.ifsc_code
                    )
                )
            )
        )
    
    def _build_rtgs_request(self, request: RailExecutionRequest) -> RTGSPaymentInitiationRequest:
        """Build RTGS API request"""
        intent = request.intent
        request_uuid = str(uuid.uuid4())
        
        return RTGSPaymentInitiationRequest(
            SubHeader=SubHeader(
                requestUUID=request_uuid,
                serviceRequestId="NB.GEN.PDT.ELIG"
            ),
            RTGSPaymentIntiationRequestBody=RTGSPaymentIntiationRequestBody(
                transactionAmount=str(intent.amount),
                sourceReferenceNumber=request.transaction_id,
                DebitAccountDetails=DebitAccountDetails(
                    DebitAccountInformation=DebitAccountInformation(
                        debitAccountNumber=intent.sender.account_number,
                        debitAccountHolderName=intent.sender.name
                    )
                ),
                CreditAccountDetails=CreditAccountDetails(
                    CreditAccountInformation=CreditAccountInformation(
                        bankName=intent.receiver.bank_name,
                        creditAccountNumber=intent.receiver.account_number,
                        creditAccountHolderName=intent.receiver.name,
                        ifscCode=intent.receiver.ifsc_code
                    )
                )
            )
        )
    
    def _build_ift_request(self, request: RailExecutionRequest) -> IFTPaymentInitiationRequest:
        """Build IFT API request"""
        intent = request.intent
        request_uuid = str(uuid.uuid4())
        
        return IFTPaymentInitiationRequest(
            SubHeader=SubHeader(
                requestUUID=request_uuid,
                serviceRequestId="NB.GEN.PDT.ELIG"
            ),
            IFTPaymentIntiationRequestBody=IFTPaymentIntiationRequestBody(
                transactionAmount=str(intent.amount),
                sourceReferenceNumber=request.transaction_id,
                remarks=intent.purpose[:100],
                DebitAccountDetails=DebitAccountDetails(
                    DebitAccountInformation=DebitAccountInformation(
                        debitAccountNumber=intent.sender.account_number,
                        debitNarration=f"TRF/{request.transaction_id}/{intent.receiver.name[:20]}"
                    )
                ),
                CreditAccountDetails=CreditAccountDetails(
                    CreditAccountInformation=CreditAccountInformation(
                        bankName=intent.receiver.bank_name,
                        creditAccountNumber=intent.receiver.account_number,
                        creditNarration=f"TRF FROM {intent.sender.name[:20]}",
                        ifscCode=intent.receiver.ifsc_code
                    )
                )
            )
        )
    
    # ========================================
    # Response Builders
    # ========================================
    
    def _build_imps_success_response(self, request: IMPSFundsTransferRequest) -> IMPSFundsTransferResponse:
        """Build successful IMPS response"""
        return IMPSFundsTransferResponse(
            SubHeader=request.SubHeader,
            IMPSFundsTransferResponseBody=IMPSFundsTransferResponseBody(
                responseCode="00",
                isSuccess=True,
                failureReason="Successful Transaction",
                requestId=request.IMPSFundsTransferRequestBody.requestId,
                retrivalReferenceNo=f"{datetime.now().strftime('%y%m%d')}{random.randint(100000, 999999)}",
                transactionDate=datetime.now().strftime("%d%m%Y%H%M%S"),
                beneficiaryName=request.IMPSFundsTransferRequestBody.beneficiaryName,
                checksum=str(random.randint(1000000000, 9999999999))
            )
        )
    
    def _build_neft_success_response(self, request: NEFTPaymentInitiationRequest) -> NEFTPaymentInitiationResponse:
        """Build successful NEFT response"""
        return NEFTPaymentInitiationResponse(
            SubHeader=request.SubHeader,
            NEFTPaymentIntiationResponseBody=NEFTPaymentIntiationResponseBody(
                utrNumber=f"NEFT{datetime.now().strftime('%y%m%d')}{random.randint(100000, 999999)}",
                code="00",
                result="Success"
            )
        )
    
    def _build_rtgs_success_response(self, request: RTGSPaymentInitiationRequest) -> RTGSPaymentInitiationResponse:
        """Build successful RTGS response"""
        return RTGSPaymentInitiationResponse(
            SubHeader=request.SubHeader,
            RTGSPaymentIntiationResponseBody=RTGSPaymentIntiationResponseBody(
                utrNumber=f"RTGS{datetime.now().strftime('%y%m%d')}{random.randint(100000, 999999)}",
                code="00",
                result="Success"
            )
        )
    
    def _build_ift_success_response(self, request: IFTPaymentInitiationRequest) -> IFTPaymentInitiationResponse:
        """Build successful IFT response"""
        return IFTPaymentInitiationResponse(
            SubHeader=request.SubHeader,
            IFTPaymentIntiationResponseBody=IFTPaymentIntiationResponseBody(
                utrNumber=f"IFT{datetime.now().strftime('%y%m%d')}{random.randint(100000, 999999)}",
                code="00",
                result="Success"
            )
        )
    
    # ========================================
    # Error Generators
    # ========================================
    
    def _get_imps_error(self) -> tuple[str, str]:
        """Get random IMPS error"""
        errors = [
            ("91", "Insufficient funds in account"),
            ("92", "Invalid beneficiary account"),
            ("93", "Transaction limit exceeded"),
            ("94", "System temporarily unavailable"),
            ("95", "Invalid IFSC code"),
            ("96", "Account blocked or frozen"),
            ("97", "Network timeout"),
            ("98", "Duplicate transaction"),
            ("99", "General processing error")
        ]
        return random.choice(errors)
    
    def _get_neft_error(self) -> tuple[str, str]:
        """Get random NEFT error"""
        errors = [
            ("N01", "Invalid beneficiary bank"),
            ("N02", "NEFT not supported by beneficiary bank"),
            ("N03", "Amount exceeds transaction limit"),
            ("N04", "Outside NEFT operating hours"),
            ("N05", "Insufficient funds"),
            ("N06", "Account validation failed"),
            ("N07", "System maintenance in progress"),
            ("N08", "Invalid transaction reference")
        ]
        return random.choice(errors)
    
    def _get_rtgs_error(self) -> tuple[str, str]:
        """Get random RTGS error"""
        errors = [
            ("R01", "Amount below RTGS minimum limit"),
            ("R02", "RTGS not operational"),
            ("R03", "Beneficiary bank not reachable"),
            ("R04", "Insufficient funds"),
            ("R05", "Invalid account details"),
            ("R06", "System timeout"),
            ("R07", "Duplicate reference number"),
            ("R08", "Regulatory compliance check failed")
        ]
        return random.choice(errors)
    
    def _get_ift_error(self) -> tuple[str, str]:
        """Get random IFT error"""
        errors = [
            ("I01", "Account not found"),
            ("I02", "Account blocked"),
            ("I03", "Insufficient balance"),
            ("I04", "Invalid transaction amount"),
            ("I05", "System error"),
            ("I06", "Transaction limit exceeded"),
            ("I07", "Account closed"),
            ("I08", "Invalid beneficiary details")
        ]
        return random.choice(errors)
    
    def _get_upi_error(self) -> tuple[str, str]:
        """Get random UPI error"""
        errors = [
            ("U01", "UPI ID not found"),
            ("U02", "Transaction declined by user"),
            ("U03", "Insufficient funds"),
            ("U04", "UPI service unavailable"),
            ("U05", "Invalid VPA"),
            ("U06", "Transaction timeout"),
            ("U07", "Daily limit exceeded"),
            ("U08", "Bank server error")
        ]
        return random.choice(errors)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get API call statistics"""
        return {
            "call_counts": self.call_counts.copy(),
            "success_rates": self.success_rates.copy(),
            "total_calls": sum(self.call_counts.values())
        }