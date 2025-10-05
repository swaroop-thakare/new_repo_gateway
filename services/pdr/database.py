"""
PDR Database Integration
Handles PostgreSQL operations for reading intents and writing PDR decisions.
"""

import os
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal
import json

import asyncpg
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import logging

from models import (
    Intent, RailConfig, ACCDecision, PDRDecision, RailPerformance,
    FallbackRail, ScoringWeights, PaymentType, IntentStatus,
    DecisionStatus, ExecutionStatus, RailType, SettlementType,
    Location, GPSCoordinates, Party, AdditionalFields
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database connections and operations for PDR system.
    Supports both sync and async operations.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        # Parse connection details from URL for sync operations
        self._parse_connection_details()
        
        # Connection pools
        self._sync_connection = None
        self._async_pool = None
    
    def _parse_connection_details(self):
        """Parse database URL for sync connection details"""
        # postgresql://user:password@host:port/database
        import urllib.parse
        parsed = urllib.parse.urlparse(self.database_url)
        
        self.connection_params = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:],  # Remove leading '/'
            'user': parsed.username,
            'password': parsed.password
        }
    
    def get_sync_connection(self):
        """Get synchronous database connection"""
        if not self._sync_connection or self._sync_connection.closed:
            self._sync_connection = psycopg2.connect(**self.connection_params)
        return self._sync_connection
    
    async def get_async_pool(self):
        """Get asynchronous connection pool"""
        if not self._async_pool:
            self._async_pool = await asyncpg.create_pool(self.database_url)
        return self._async_pool
    
    def close_connections(self):
        """Close all database connections"""
        if self._sync_connection and not self._sync_connection.closed:
            self._sync_connection.close()
        
        if self._async_pool:
            asyncio.create_task(self._async_pool.close())
    
    # ========================================
    # Intent Operations
    # ========================================
    
    def get_pending_intents(self, limit: int = 100) -> List[Intent]:
        """Get pending intents for processing"""
        conn = self.get_sync_connection()
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM intent 
                WHERE status = %s 
                ORDER BY created_at ASC 
                LIMIT %s
            """, (IntentStatus.PENDING.value, limit))
            
            rows = cursor.fetchall()
            return [self._row_to_intent(row) for row in rows]
    
    def get_intent_by_transaction_id(self, transaction_id: str) -> Optional[Intent]:
        """Get intent by transaction ID"""
        conn = self.get_sync_connection()
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM intent WHERE transaction_id = %s
            """, (transaction_id,))
            
            row = cursor.fetchone()
            return self._row_to_intent(row) if row else None
    
    def update_intent_status(self, transaction_id: str, status: IntentStatus):
        """Update intent status"""
        conn = self.get_sync_connection()
        
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE intent 
                SET status = %s, updated_at = CURRENT_TIMESTAMP 
                WHERE transaction_id = %s
            """, (status.value, transaction_id))
            
        conn.commit()
    
    def _row_to_intent(self, row: Dict[str, Any]) -> Intent:
        """Convert database row to Intent model"""
        additional_fields_data = row.get('additional_fields', {}) or {}
        
        return Intent(
            transaction_id=row['transaction_id'],
            payment_type=PaymentType(row['payment_type']),
            sender=Party(
                name=row['sender_name'],
                account_number=row['sender_account_number'],
                ifsc_code=row['sender_ifsc_code'],
                bank_name=row['sender_bank_name']
            ),
            receiver=Party(
                name=row['receiver_name'],
                account_number=row['receiver_account_number'],
                ifsc_code=row['receiver_ifsc_code'],
                bank_name=row['receiver_bank_name']
            ),
            amount=Decimal(str(row['amount'])),
            currency=row['currency'],
            method=row.get('method'),
            purpose=row['purpose'],
            schedule_datetime=row['schedule_datetime'],
            location=Location(
                city=row['location_city'],
                gps_coordinates=GPSCoordinates(
                    latitude=float(row['location_latitude']),
                    longitude=float(row['location_longitude'])
                ) if row.get('location_latitude') and row.get('location_longitude') else None
            ) if row.get('location_city') else None,
            additional_fields=AdditionalFields(**additional_fields_data),
            status=IntentStatus(row['status']),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    # ========================================
    # Rail Configuration Operations
    # ========================================
    
    def get_active_rails(self) -> List[RailConfig]:
        """Get all active rail configurations"""
        conn = self.get_sync_connection()
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM rail_config 
                WHERE is_active = true 
                ORDER BY rail_name
            """)
            
            rows = cursor.fetchall()
            return [self._row_to_rail_config(row) for row in rows]
    
    def get_rail_config(self, rail_name: str) -> Optional[RailConfig]:
        """Get specific rail configuration"""
        conn = self.get_sync_connection()
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM rail_config WHERE rail_name = %s
            """, (rail_name,))
            
            row = cursor.fetchone()
            return self._row_to_rail_config(row) if row else None
    
    def update_rail_daily_limit_remaining(self, rail_name: str, remaining_amount: Decimal):
        """Update remaining daily limit for a rail"""
        conn = self.get_sync_connection()
        
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE rail_config 
                SET daily_limit_remaining = %s, updated_at = CURRENT_TIMESTAMP 
                WHERE rail_name = %s
            """, (remaining_amount, rail_name))
            
        conn.commit()
    
    def _row_to_rail_config(self, row: Dict[str, Any]) -> RailConfig:
        """Convert database row to RailConfig model"""
        api_headers_data = row.get('api_headers', {}) or {}
        
        return RailConfig(
            rail_name=row['rail_name'],
            rail_type=RailType(row['rail_type']),
            min_amount=Decimal(str(row['min_amount'])),
            max_amount=Decimal(str(row['max_amount'])),
            new_user_limit=Decimal(str(row['new_user_limit'])),
            working_hours_start=row['working_hours_start'],
            working_hours_end=row['working_hours_end'],
            working_days=row['working_days'],
            avg_eta_ms=row['avg_eta_ms'],
            cost_bps=Decimal(str(row['cost_bps'])),
            success_probability=row['success_probability'],
            settlement_type=SettlementType(row['settlement_type']),
            settlement_certainty=row['settlement_certainty'],
            api_endpoint=row.get('api_endpoint'),
            api_method=row['api_method'],
            api_headers=api_headers_data,
            is_active=row['is_active'],
            daily_limit=Decimal(str(row['daily_limit'])),
            daily_limit_remaining=Decimal(str(row['daily_limit_remaining'])) if row.get('daily_limit_remaining') else None,
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    # ========================================
    # ACC Decision Operations
    # ========================================
    
    def get_acc_decision(self, transaction_id: str) -> Optional[ACCDecision]:
        """Get ACC decision for a transaction"""
        conn = self.get_sync_connection()
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM acc_decisions 
                WHERE transaction_id = %s 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (transaction_id,))
            
            row = cursor.fetchone()
            return self._row_to_acc_decision(row) if row else None
    
    def save_acc_decision(self, acc_decision: ACCDecision):
        """Save ACC decision to database"""
        conn = self.get_sync_connection()
        
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO acc_decisions (
                    transaction_id, line_id, decision, policy_version,
                    reasons, evidence_refs, compliance_penalty, risk_score
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                acc_decision.transaction_id,
                acc_decision.line_id,
                acc_decision.decision.value,
                acc_decision.policy_version,
                acc_decision.reasons,
                acc_decision.evidence_refs,
                acc_decision.compliance_penalty,
                acc_decision.risk_score
            ))
            
        conn.commit()
    
    def _row_to_acc_decision(self, row: Dict[str, Any]) -> ACCDecision:
        """Convert database row to ACCDecision model"""
        return ACCDecision(
            transaction_id=row['transaction_id'],
            line_id=row['line_id'],
            decision=DecisionStatus(row['decision']),
            policy_version=row['policy_version'],
            reasons=row.get('reasons', []),
            evidence_refs=row.get('evidence_refs', []),
            compliance_penalty=row.get('compliance_penalty', 0.0),
            risk_score=row.get('risk_score', 0.0),
            created_at=row.get('created_at')
        )
    
    # ========================================
    # PDR Decision Operations
    # ========================================
    
    def save_pdr_decision(self, pdr_decision: PDRDecision):
        """Save PDR decision to database"""
        conn = self.get_sync_connection()
        
        # Convert fallback rails to JSON
        fallback_rails_json = [
            {"rail_name": fb.rail_name, "score": fb.score}
            for fb in pdr_decision.fallback_rails
        ]
        
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO pdr_decisions (
                    transaction_id, primary_rail, primary_rail_score,
                    fallback_rails, scoring_features, scoring_weights,
                    execution_status, current_rail_attempt, attempt_count,
                    final_rail_used, final_utr_number, final_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                pdr_decision.transaction_id,
                pdr_decision.primary_rail,
                pdr_decision.primary_rail_score,
                json.dumps(fallback_rails_json),
                json.dumps(pdr_decision.scoring_features),
                json.dumps(pdr_decision.scoring_weights.dict()),
                pdr_decision.execution_status.value,
                pdr_decision.current_rail_attempt,
                pdr_decision.attempt_count,
                pdr_decision.final_rail_used,
                pdr_decision.final_utr_number,
                pdr_decision.final_status.value if pdr_decision.final_status else None
            ))
            
        conn.commit()
    
    def get_pdr_decision(self, transaction_id: str) -> Optional[PDRDecision]:
        """Get PDR decision for a transaction"""
        conn = self.get_sync_connection()
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM pdr_decisions 
                WHERE transaction_id = %s 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (transaction_id,))
            
            row = cursor.fetchone()
            return self._row_to_pdr_decision(row) if row else None
    
    def update_pdr_execution_status(
        self, 
        transaction_id: str, 
        execution_status: ExecutionStatus,
        current_rail_attempt: Optional[str] = None,
        attempt_count: Optional[int] = None,
        final_rail_used: Optional[str] = None,
        final_utr_number: Optional[str] = None,
        final_status: Optional[ExecutionStatus] = None
    ):
        """Update PDR execution status"""
        conn = self.get_sync_connection()
        
        update_fields = ["execution_status = %s", "updated_at = CURRENT_TIMESTAMP"]
        params = [execution_status.value]
        
        if current_rail_attempt is not None:
            update_fields.append("current_rail_attempt = %s")
            params.append(current_rail_attempt)
            
        if attempt_count is not None:
            update_fields.append("attempt_count = %s")
            params.append(attempt_count)
            
        if final_rail_used is not None:
            update_fields.append("final_rail_used = %s")
            params.append(final_rail_used)
            
        if final_utr_number is not None:
            update_fields.append("final_utr_number = %s")
            params.append(final_utr_number)
            
        if final_status is not None:
            update_fields.append("final_status = %s")
            params.append(final_status.value)
        
        params.append(transaction_id)
        
        with conn.cursor() as cursor:
            cursor.execute(f"""
                UPDATE pdr_decisions 
                SET {', '.join(update_fields)}
                WHERE transaction_id = %s
            """, params)
            
        conn.commit()
    
    def _row_to_pdr_decision(self, row: Dict[str, Any]) -> PDRDecision:
        """Convert database row to PDRDecision model"""
        # Parse fallback rails JSON
        fallback_rails_data = row.get('fallback_rails', []) or []
        fallback_rails = [
            FallbackRail(rail_name=fb['rail_name'], score=fb['score'])
            for fb in fallback_rails_data
        ]
        
        # Parse scoring data
        scoring_features = row.get('scoring_features', {}) or {}
        scoring_weights_data = row.get('scoring_weights', {}) or {}
        scoring_weights = ScoringWeights(**scoring_weights_data) if scoring_weights_data else ScoringWeights()
        
        return PDRDecision(
            transaction_id=row['transaction_id'],
            primary_rail=row['primary_rail'],
            primary_rail_score=row['primary_rail_score'],
            fallback_rails=fallback_rails,
            scoring_features=scoring_features,
            scoring_weights=scoring_weights,
            execution_status=ExecutionStatus(row['execution_status']),
            current_rail_attempt=row.get('current_rail_attempt'),
            attempt_count=row.get('attempt_count', 0),
            final_rail_used=row.get('final_rail_used'),
            final_utr_number=row.get('final_utr_number'),
            final_status=ExecutionStatus(row['final_status']) if row.get('final_status') else None,
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    # ========================================
    # Rail Performance Operations
    # ========================================
    
    def save_rail_performance(self, performance: RailPerformance):
        """Save rail performance data"""
        conn = self.get_sync_connection()
        
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO rail_performance (
                    rail_name, transaction_id, actual_eta_ms, success,
                    error_code, error_message, initiated_at, completed_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                performance.rail_name,
                performance.transaction_id,
                performance.actual_eta_ms,
                performance.success,
                performance.error_code,
                performance.error_message,
                performance.initiated_at,
                performance.completed_at
            ))
            
        conn.commit()
    
    def get_rail_performance_stats(self, rail_name: str, days: int = 30) -> Dict[str, Any]:
        """Get rail performance statistics for the last N days"""
        conn = self.get_sync_connection()
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_transactions,
                    COUNT(*) FILTER (WHERE success = true) as successful_transactions,
                    AVG(actual_eta_ms) FILTER (WHERE success = true) as avg_eta_ms,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY actual_eta_ms) 
                        FILTER (WHERE success = true) as p95_eta_ms
                FROM rail_performance 
                WHERE rail_name = %s 
                    AND created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            """, (rail_name, days))
            
            row = cursor.fetchone()
            
            if row and row['total_transactions'] > 0:
                success_rate = row['successful_transactions'] / row['total_transactions']
                return {
                    'rail_name': rail_name,
                    'total_transactions': row['total_transactions'],
                    'successful_transactions': row['successful_transactions'],
                    'success_rate': success_rate,
                    'avg_eta_ms': row['avg_eta_ms'],
                    'p95_eta_ms': row['p95_eta_ms'],
                    'days': days
                }
            else:
                return {
                    'rail_name': rail_name,
                    'total_transactions': 0,
                    'success_rate': 0.0,
                    'days': days
                }
    
    # ========================================
    # Utility Methods
    # ========================================
    
    def execute_schema_file(self, schema_file_path: str):
        """Execute SQL schema file"""
        conn = self.get_sync_connection()
        
        with open(schema_file_path, 'r') as f:
            schema_sql = f.read()
        
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)
            
        conn.commit()
        logger.info(f"Executed schema file: {schema_file_path}")
    
    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            conn = self.get_sync_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result[0] == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager(
    database_url="postgresql://postgres:NmxNfLIKzWQzxwrmQUiKCouDXhcScjcD@switchyard.proxy.rlwy.net:25675/railway"
)