# Intent Manager - Agentic AI for Payment Classification

A single, comprehensive agentic AI system that processes payment data and classifies intents for the Arealis Gateway system.

## 🤖 What It Does

The Intent Manager is a complete agentic AI solution that:

- **Processes Payment Data**: Handles JSON payment data from S3 or local files
- **Classifies Intents**: Uses rule-based + AI logic to identify payment purposes
- **Calculates Risk Scores**: Assesses risk levels for each payment
- **Routes Workflows**: Directs payments to appropriate processing workflows
- **Generates Agent Pipelines**: Creates step-by-step processing instructions

## 📁 File Structure

```
layers/intent-router/
├── intent_manager.py      # 🤖 Main agentic AI system (SINGLE FILE)
├── sample.json           # 📊 Sample payment data for testing
├── requirements.txt      # 📦 Python dependencies
├── env.example          # 🔧 Environment configuration template
└── README.md            # 📖 This documentation
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Intent Manager

```bash
python intent_manager.py
```

### 3. Expected Output

The system will process your payment data and output:

```json
{
  "batch_id": "B-2025-09-30-01",
  "intents": [
    {
      "line_id": "L-1",
      "intent": "PAYROLL",
      "risk_score": 0.10,
      "confidence": 0.98
    },
    {
      "line_id": "L-2", 
      "intent": "VENDOR_TO_VENDOR",
      "risk_score": 0.25,
      "confidence": 0.95
    }
  ],
  "workflow_ids": ["WF-PAYROLL-DOMESTIC", "WF-VENDOR-TO-VENDOR-DOMESTIC"],
  "agent_pipeline": ["ACC", "PDR", "Execution", "ARL", "CRRAK"],
  "policy_version": "intent-1.0.1"
}
```

## 🎯 Intent Classification

The system classifies payments into these intent types:

- **PAYROLL**: Employee salaries and wages
- **VENDOR_PAYMENT**: Supplier and vendor payments
- **VENDOR_TO_VENDOR**: Vendor-to-vendor transfers
- **LOAN**: Loan disbursements and payments
- **UTILITY**: Utility bill payments
- **TAX**: Tax payments
- **REFUND**: Refund transactions
- **INVESTMENT**: Investment-related payments
- **TRANSFER**: General transfers
- **UNKNOWN**: Unrecognized purposes (requires manual review)

## 📊 Risk Assessment

Risk scores are calculated based on:

- **Amount**: Higher amounts = higher risk
- **Payment Method**: Cash = higher risk
- **Intent Type**: Unknown intents = higher risk
- **Confidence**: Low confidence = higher risk
- **Purpose Patterns**: Unusual patterns = higher risk
- **International**: Cross-border payments = higher risk

Risk Levels:
- **LOW**: 0.0 - 0.3
- **MEDIUM**: 0.3 - 0.5
- **HIGH**: 0.5 - 0.8
- **CRITICAL**: 0.8 - 1.0

## 🔄 Workflow Routing

Based on intent and risk level, payments are routed to:

- **DOMESTIC**: Standard processing workflows
- **ENHANCED**: Enhanced review workflows
- **REVIEW**: Manual review workflows
- **CRITICAL**: Critical review workflows

## 🤖 Agent Pipeline

Each intent type has a specific agent pipeline:

- **ACC**: Account validation
- **PDR**: Payment data review
- **Execution**: Payment execution
- **ARL**: Anti-money laundering
- **CRRAK**: Compliance and risk assessment
- **Manual-Review**: Human review for complex cases

## 📈 Usage Examples

### Process Local File

```python
from intent_manager import IntentManager

# Initialize the agentic AI system
intent_manager = IntentManager()

# Process a JSON file
results = intent_manager.process_file("sample.json", "B-2025-09-30-01")

# Get summary
summary = intent_manager.get_summary(results)
print(f"Total payments: {summary['total_payments']}")
print(f"High risk payments: {summary['manual_review_count']}")
```

### Process Payment Data Directly

```python
# Process payment data directly
payments_data = [
    {
        "payment_type": "payroll",
        "transaction_id": "TXN001",
        "amount": 50000,
        "purpose": "SALARY",
        # ... other fields
    }
]

results = intent_manager.process_payments(payments_data)
```

## 🔧 Configuration

The system is highly configurable through the `IntentManager` class:

- **Intent Mappings**: Add new purpose-to-intent mappings
- **Risk Factors**: Adjust risk scoring parameters
- **Workflow Mappings**: Customize workflow routing
- **Agent Pipelines**: Define processing steps

## 📊 Output Analysis

The system provides comprehensive analysis:

- **Intent Distribution**: Breakdown by intent type
- **Risk Distribution**: Risk level distribution
- **High Risk Alerts**: Payments requiring manual review
- **Workflow Routing**: Assigned workflows and pipelines
- **Processing Statistics**: Performance metrics

## 🎉 Key Features

✅ **Single File Solution**: Everything in one `intent_manager.py` file
✅ **Agentic AI**: Intelligent classification and routing
✅ **Risk Assessment**: Comprehensive risk scoring
✅ **Workflow Routing**: Automatic workflow assignment
✅ **High Performance**: Fast processing of large datasets
✅ **Extensible**: Easy to add new intents and rules
✅ **Production Ready**: Robust error handling and logging

## 🚀 Next Steps

1. **Customize Intent Mappings**: Add your specific purpose codes
2. **Adjust Risk Factors**: Fine-tune risk scoring for your use case
3. **Add New Workflows**: Create custom workflow mappings
4. **Integrate with S3**: Connect to your S3 bucket for data processing
5. **Deploy**: Use in your Arealis Gateway system

---

**🤖 The Intent Manager is your complete agentic AI solution for payment intent classification!**