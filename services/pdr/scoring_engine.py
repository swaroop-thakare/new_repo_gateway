"""
PDR Rail Scoring Engine
Implements the sophisticated rail selection algorithm with normalization and weighted scoring.
"""

import math
from datetime import datetime, time
from typing import List, Dict, Tuple, Optional, Any
from decimal import Decimal

from models import (
    Intent, RailConfig, ACCDecision, RailFeatures, NormalizedFeatures, 
    ScoringWeights, RailScore, SettlementType, RailType
)


class RailScoringEngine:
    """
    Implements the sophisticated rail scoring algorithm with:
    1. Hard constraint filtering
    2. Feature normalization 
    3. Weighted linear scoring
    4. Fallback ordering
    """
    
    def __init__(self, scoring_weights: Optional[ScoringWeights] = None):
        self.weights = scoring_weights or ScoringWeights()
    
    def select_rails(
        self, 
        intent: Intent, 
        available_rails: List[RailConfig],
        acc_decision: ACCDecision,
        current_time: Optional[datetime] = None
    ) -> Tuple[List[RailScore], List[str]]:
        """
        Main rail selection pipeline:
        1. Filter by hard constraints
        2. Compute raw features
        3. Normalize features
        4. Score and rank
        
        Returns:
            Tuple of (scored_rails, filtered_reasons)
        """
        if current_time is None:
            current_time = datetime.now()
            
        # Step 1: Hard constraint filtering
        eligible_rails, filter_reasons = self._filter_by_hard_constraints(
            intent, available_rails, acc_decision, current_time
        )
        
        if not eligible_rails:
            return [], filter_reasons
            
        # Step 2: Compute raw features for each eligible rail
        raw_features = []
        for rail in eligible_rails:
            features = self._compute_raw_features(intent, rail, acc_decision, current_time)
            raw_features.append(features)
            
        # Step 3: Normalize features across all rails
        normalized_features = self._normalize_features(raw_features)
        
        # Step 4: Score each rail
        scored_rails = []
        for i, rail in enumerate(eligible_rails):
            score = self._compute_score(normalized_features[i])
            rail_score = RailScore(
                rail_name=rail.rail_name,
                score=score,
                normalized_features=normalized_features[i],
                raw_features=raw_features[i]
            )
            scored_rails.append(rail_score)
            
        # Step 5: Sort by score (descending)
        scored_rails.sort(key=lambda x: x.score, reverse=True)
        
        return scored_rails, filter_reasons
    
    def _filter_by_hard_constraints(
        self, 
        intent: Intent, 
        rails: List[RailConfig],
        acc_decision: ACCDecision,
        current_time: datetime
    ) -> Tuple[List[RailConfig], List[str]]:
        """
        Apply hard constraints to filter eligible rails.
        Returns (eligible_rails, rejection_reasons)
        """
        eligible_rails = []
        rejection_reasons = []
        
        for rail in rails:
            # Skip if rail is inactive
            if not rail.is_active:
                rejection_reasons.append(f"{rail.rail_name}: Rail is inactive")
                continue
                
            # Amount constraints
            if intent.amount < rail.min_amount:
                rejection_reasons.append(
                    f"{rail.rail_name}: Amount {intent.amount} < min_amount {rail.min_amount}"
                )
                continue
                
            if intent.amount > rail.max_amount:
                rejection_reasons.append(
                    f"{rail.rail_name}: Amount {intent.amount} > max_amount {rail.max_amount}"
                )
                continue
                
            # Daily limit check (if available)
            if rail.daily_limit_remaining is not None and intent.amount > rail.daily_limit_remaining:
                rejection_reasons.append(
                    f"{rail.rail_name}: Amount {intent.amount} > daily_limit_remaining {rail.daily_limit_remaining}"
                )
                continue
                
            # New user limits (simplified - assume user_age < 30 days is new user)
            # In production, this would come from user profile
            is_new_user = self._is_new_user(intent)  # Mock implementation
            if is_new_user and intent.amount > rail.new_user_limit:
                rejection_reasons.append(
                    f"{rail.rail_name}: New user amount {intent.amount} > new_user_limit {rail.new_user_limit}"
                )
                continue
                
            # Working hours check
            if not self._is_within_working_hours(rail, current_time):
                rejection_reasons.append(
                    f"{rail.rail_name}: Outside working hours"
                )
                continue
                
            # ACC compliance check - if ACC failed, block the rail
            if acc_decision.decision == "FAIL":
                rejection_reasons.append(
                    f"{rail.rail_name}: ACC compliance failed: {', '.join(acc_decision.reasons)}"
                )
                continue
                
            # Intra-bank check (simplified)
            if rail.rail_name == "IFT" and not self._is_same_bank(intent):
                rejection_reasons.append(
                    f"{rail.rail_name}: Intra-bank transfer requires same bank"
                )
                continue
                
            # If we reach here, rail passes all hard constraints
            eligible_rails.append(rail)
            
        return eligible_rails, rejection_reasons
    
    def _compute_raw_features(
        self, 
        intent: Intent, 
        rail: RailConfig,
        acc_decision: ACCDecision,
        current_time: datetime
    ) -> RailFeatures:
        """Compute raw features for a rail"""
        
        # Basic features from rail config
        eta_ms = rail.avg_eta_ms
        cost_bps = float(rail.cost_bps)
        success_prob = rail.success_probability
        
        # Compliance and risk from ACC
        compliance_penalty = acc_decision.compliance_penalty
        risk_score = acc_decision.risk_score
        
        # Critic penalty decay (mock implementation)
        critic_penalty_decay = self._compute_critic_penalty(rail, current_time)
        
        # Window bonus (load balancing)
        window_bonus = self._compute_window_bonus(rail, current_time)
        
        # Amount match bonus
        amount_match_bonus = self._compute_amount_match_bonus(rail, intent.amount)
        
        # Working hours penalty
        working_hours_penalty = self._compute_working_hours_penalty(rail, current_time)
        
        # Settlement certainty
        settlement_certainty = rail.settlement_certainty
        
        return RailFeatures(
            rail_name=rail.rail_name,
            eta_ms=eta_ms,
            cost_bps=cost_bps,
            success_prob=success_prob,
            compliance_penalty=compliance_penalty,
            risk_score=risk_score,
            critic_penalty_decay=critic_penalty_decay,
            window_bonus=window_bonus,
            amount_match_bonus=amount_match_bonus,
            working_hours_penalty=working_hours_penalty,
            settlement_certainty=settlement_certainty
        )
    
    def _normalize_features(self, raw_features_list: List[RailFeatures]) -> List[NormalizedFeatures]:
        """
        Normalize features across all rails using min-max normalization.
        Higher normalized value = better for scoring.
        """
        if not raw_features_list:
            return []
            
        # Extract feature arrays
        eta_values = [f.eta_ms for f in raw_features_list]
        cost_values = [f.cost_bps for f in raw_features_list]
        succ_values = [f.success_prob for f in raw_features_list]
        comp_values = [f.compliance_penalty for f in raw_features_list]
        risk_values = [f.risk_score for f in raw_features_list]
        crit_values = [f.critic_penalty_decay for f in raw_features_list]
        win_values = [f.window_bonus for f in raw_features_list]
        amt_values = [f.amount_match_bonus for f in raw_features_list]
        wh_values = [f.working_hours_penalty for f in raw_features_list]
        setl_values = [f.settlement_certainty for f in raw_features_list]
        
        # Normalize each feature
        normalized_list = []
        for i, raw_features in enumerate(raw_features_list):
            # For features where LOWER is BETTER (invert normalization)
            eta_n = self._normalize_lower_better(eta_values[i], eta_values)
            cost_n = self._normalize_lower_better(cost_values[i], cost_values)
            comp_n = self._normalize_lower_better(comp_values[i], comp_values)
            risk_n = self._normalize_lower_better(risk_values[i], risk_values)
            crit_n = self._normalize_lower_better(crit_values[i], crit_values)
            wh_n = self._normalize_lower_better(wh_values[i], wh_values)
            
            # For features where HIGHER is BETTER (normal normalization)
            succ_n = self._normalize_higher_better(succ_values[i], succ_values)
            win_n = self._normalize_higher_better(win_values[i], win_values)
            amt_n = self._normalize_higher_better(amt_values[i], amt_values)
            setl_n = self._normalize_higher_better(setl_values[i], setl_values)
            
            normalized = NormalizedFeatures(
                rail_name=raw_features.rail_name,
                eta_n=eta_n,
                cost_n=cost_n,
                succ_n=succ_n,
                comp_n=comp_n,
                risk_n=risk_n,
                crit_n=crit_n,
                win_n=win_n,
                amt_n=amt_n,
                wh_n=wh_n,
                setl_n=setl_n
            )
            normalized_list.append(normalized)
            
        return normalized_list
    
    def _normalize_higher_better(self, value: float, all_values: List[float]) -> float:
        """Normalize where higher values are better"""
        min_val = min(all_values)
        max_val = max(all_values)
        
        if max_val == min_val:
            return 0.5  # Neutral if all values are equal
            
        return (value - min_val) / (max_val - min_val)
    
    def _normalize_lower_better(self, value: float, all_values: List[float]) -> float:
        """Normalize where lower values are better (invert the scale)"""
        min_val = min(all_values)
        max_val = max(all_values)
        
        if max_val == min_val:
            return 0.5  # Neutral if all values are equal
            
        return (max_val - value) / (max_val - min_val)
    
    def _compute_score(self, normalized: NormalizedFeatures) -> float:
        """
        Compute final weighted score using normalized features.
        Higher score = better rail.
        """
        score = (
            self.weights.w_eta * normalized.eta_n +
            self.weights.w_cost * normalized.cost_n +
            self.weights.w_succ * normalized.succ_n +
            self.weights.w_comp * normalized.comp_n +
            self.weights.w_risk * normalized.risk_n +
            self.weights.w_crit * normalized.crit_n +
            self.weights.w_win * normalized.win_n +
            self.weights.w_amt * normalized.amt_n +
            self.weights.w_wh * normalized.wh_n +
            self.weights.w_setl * normalized.setl_n
        )
        
        # Ensure score is in [0, 1] range
        return max(0.0, min(1.0, score))
    
    # ========================================
    # Helper Methods
    # ========================================
    
    def _is_new_user(self, intent: Intent) -> bool:
        """
        Mock implementation to determine if user is new.
        In production, this would check user profile/history.
        """
        # For demo purposes, assume users with employee_id starting with 'NEW' are new
        if intent.additional_fields and intent.additional_fields.employee_id:
            return intent.additional_fields.employee_id.startswith('NEW')
        return False
    
    def _is_within_working_hours(self, rail: RailConfig, current_time: datetime) -> bool:
        """Check if current time is within rail's working hours"""
        current_weekday = current_time.weekday() + 1  # Monday = 1
        current_time_only = current_time.time()
        
        # Check if current day is a working day
        if current_weekday not in rail.working_days:
            return False
            
        # Check if current time is within working hours
        if rail.working_hours_start <= rail.working_hours_end:
            # Normal case: start < end (e.g., 9:00 - 17:00)
            return rail.working_hours_start <= current_time_only <= rail.working_hours_end
        else:
            # Overnight case: start > end (e.g., 22:00 - 06:00)
            return current_time_only >= rail.working_hours_start or current_time_only <= rail.working_hours_end
    
    def _is_same_bank(self, intent: Intent) -> bool:
        """Check if sender and receiver are from the same bank"""
        sender_bank_code = intent.sender.ifsc_code[:4]
        receiver_bank_code = intent.receiver.ifsc_code[:4]
        return sender_bank_code == receiver_bank_code
    
    def _compute_critic_penalty(self, rail: RailConfig, current_time: datetime) -> float:
        """
        Compute critic penalty based on recent failures.
        In production, this would query rail_performance table.
        """
        # Mock implementation - return small penalty for NEFT during off-hours
        if rail.rail_name == "NEFT" and not self._is_within_working_hours(rail, current_time):
            return 0.2
        return 0.0
    
    def _compute_window_bonus(self, rail: RailConfig, current_time: datetime) -> float:
        """
        Compute window bonus for load balancing.
        In production, this would consider current rail usage.
        """
        # Mock implementation - give bonus to underused rails
        if rail.rail_name == "IFT":  # Assume IFT is underused
            return 0.3
        elif rail.rail_name == "RTGS" and current_time.hour >= 14:  # Afternoon RTGS bonus
            return 0.2
        return 0.0
    
    def _compute_amount_match_bonus(self, rail: RailConfig, amount: Decimal) -> float:
        """
        Compute how well the rail matches the transaction amount.
        """
        amount_float = float(amount)
        
        if rail.rail_name == "UPI":
            # UPI is great for small amounts
            if amount_float <= 25000:
                return 1.0
            elif amount_float <= 100000:
                return 0.7
            else:
                return 0.3
                
        elif rail.rail_name == "IMPS":
            # IMPS is good for medium amounts
            if 1000 <= amount_float <= 200000:
                return 1.0
            elif amount_float <= 500000:
                return 0.8
            else:
                return 0.4
                
        elif rail.rail_name == "NEFT":
            # NEFT is good for larger amounts
            if amount_float >= 50000:
                return 1.0
            elif amount_float >= 10000:
                return 0.8
            else:
                return 0.5
                
        elif rail.rail_name == "RTGS":
            # RTGS is best for very large amounts
            if amount_float >= 500000:
                return 1.0
            elif amount_float >= 200000:
                return 0.8
            else:
                return 0.3  # Below minimum, but might be allowed
                
        elif rail.rail_name == "IFT":
            # IFT is good for intra-bank transfers of any size
            return 0.9
            
        return 0.5  # Default neutral score
    
    def _compute_working_hours_penalty(self, rail: RailConfig, current_time: datetime) -> float:
        """
        Compute penalty for rails that would require waiting.
        """
        if not self._is_within_working_hours(rail, current_time):
            if rail.rail_type == RailType.BATCH:
                # NEFT outside working hours has high penalty
                return 0.8
            elif rail.rail_type == RailType.REALTIME:
                # RTGS outside working hours has very high penalty
                return 0.9
            else:
                # Instant rails (UPI, IMPS) have no penalty
                return 0.0
        return 0.0
    
    def get_explainability_report(self, scored_rails: List[RailScore]) -> Dict[str, Any]:
        """
        Generate an explainability report for the scoring decision.
        """
        if not scored_rails:
            return {"error": "No rails scored"}
            
        primary_rail = scored_rails[0]
        
        # Find top contributing features
        features = primary_rail.normalized_features
        contributions = {
            "ETA": self.weights.w_eta * features.eta_n,
            "Cost": self.weights.w_cost * features.cost_n,
            "Success Probability": self.weights.w_succ * features.succ_n,
            "Compliance": self.weights.w_comp * features.comp_n,
            "Risk": self.weights.w_risk * features.risk_n,
            "Recent Failures": self.weights.w_crit * features.crit_n,
            "Load Balancing": self.weights.w_win * features.win_n,
            "Amount Match": self.weights.w_amt * features.amt_n,
            "Working Hours": self.weights.w_wh * features.wh_n,
            "Settlement Certainty": self.weights.w_setl * features.setl_n,
        }
        
        # Sort by contribution
        sorted_contributions = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "primary_rail": primary_rail.rail_name,
            "primary_score": primary_rail.score,
            "top_contributing_factors": sorted_contributions[:3],
            "all_contributions": sorted_contributions,
            "total_rails_evaluated": len(scored_rails),
            "scoring_weights": self.weights.dict()
        }