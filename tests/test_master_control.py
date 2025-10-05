"""
Test cases for Master Control Service
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from services.master_control import MasterControl, WorkflowEvent, TaskRequest


class TestMasterControl:
    """Test Master Control service functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.master_control = MasterControl()
        self.sample_event = WorkflowEvent(
            type="workflow_selected",
            batch_id="B-2025-10-04-01",
            line_id="L-1",
            agent_pipeline=["PDR", "CRRAK", "ARL"],
            task_request=TaskRequest(
                task_type="pdr",
                batch_id="B-2025-10-04-01",
                line_id="L-1",
                amount=250000.0
            )
        )
    
    @pytest.mark.asyncio
    async def test_process_workflow_selected(self):
        """Test processing workflow selection event"""
        with patch.object(self.master_control, '_execute_agent') as mock_execute:
            mock_execute.return_value = {
                "status": "SUCCESS",
                "agent": "PDR",
                "result": {"primary_rail": "NEFT"},
                "timestamp": "2025-10-04T13:14:00Z"
            }
            
            result = await self.master_control.process_event(self.sample_event)
            
            assert result["status"] == "SUCCESS"
            assert result["agent"] == "PDR"
            mock_execute.assert_called_once_with("PDR", self.sample_event.task_request)
    
    @pytest.mark.asyncio
    async def test_process_task_completed(self):
        """Test processing task completion event"""
        # First set up a workflow
        workflow_key = "B-2025-10-04-01_L-1"
        self.master_control.workflow_status[workflow_key] = {
            "status": "PROCESSING",
            "pipeline": ["PDR", "CRRAK", "ARL"],
            "current_step": 0,
            "results": {},
            "started_at": "2025-10-04T13:14:00Z"
        }
        
        completion_event = WorkflowEvent(
            type="task_completed",
            batch_id="B-2025-10-04-01",
            line_id="L-1",
            task_request=TaskRequest(
                task_type="crrak",
                batch_id="B-2025-10-04-01",
                line_id="L-1"
            ),
            result={"status": "SUCCESS", "agent": "PDR"}
        )
        
        with patch.object(self.master_control, '_execute_agent') as mock_execute:
            mock_execute.return_value = {
                "status": "SUCCESS",
                "agent": "CRRAK",
                "result": {"compliance_status": "COMPLIANT"},
                "timestamp": "2025-10-04T13:15:00Z"
            }
            
            result = await self.master_control.process_event(completion_event)
            
            assert result["status"] == "SUCCESS"
            assert result["agent"] == "CRRAK"
    
    @pytest.mark.asyncio
    async def test_process_task_failed(self):
        """Test processing task failure event"""
        failure_event = WorkflowEvent(
            type="task_failed",
            batch_id="B-2025-10-04-01",
            line_id="L-1",
            task_request=TaskRequest(
                task_type="pdr",
                batch_id="B-2025-10-04-01",
                line_id="L-1",
                issues=["INVALID_IFSC"]
            ),
            result={"status": "FAILED", "error": "Invalid IFSC code"}
        )
        
        with patch.object(self.master_control, '_execute_agent') as mock_execute:
            mock_execute.return_value = {
                "status": "SUCCESS",
                "agent": "RCA",
                "result": {"root_cause": {"issue": "INVALID_IFSC"}},
                "timestamp": "2025-10-04T13:15:00Z"
            }
            
            result = await self.master_control.process_event(failure_event)
            
            assert result["status"] == "FAILED_WITH_RCA"
            assert "rca_result" in result
    
    @pytest.mark.asyncio
    async def test_execute_agent_pdr(self):
        """Test executing PDR agent"""
        task_request = TaskRequest(
            task_type="pdr",
            batch_id="B-2025-10-04-01",
            line_id="L-1",
            amount=250000.0
        )
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "decisions": [{"primary_rail": "NEFT", "score": 0.95}]
            }
            mock_post.return_value = mock_response
            
            result = await self.master_control._execute_agent("PDR", task_request)
            
            assert result["status"] == "SUCCESS"
            assert result["agent"] == "PDR"
            assert "result" in result
    
    @pytest.mark.asyncio
    async def test_execute_agent_rca(self):
        """Test executing RCA agent"""
        task_request = TaskRequest(
            task_type="rca",
            batch_id="B-2025-10-04-01",
            line_id="L-1",
            status="FAILED",
            issues=["INVALID_IFSC"]
        )
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "task_type": "rca_result",
                "status": "COMPLETED",
                "root_cause": {"issue": "INVALID_IFSC"}
            }
            mock_post.return_value = mock_response
            
            result = await self.master_control._execute_agent("RCA", task_request)
            
            assert result["status"] == "SUCCESS"
            assert result["agent"] == "RCA"
            assert "result" in result
    
    @pytest.mark.asyncio
    async def test_execute_agent_unknown(self):
        """Test executing unknown agent"""
        result = await self.master_control._execute_agent("UNKNOWN", None)
        
        assert result["status"] == "ERROR"
        assert "Unknown agent" in result["error"]
    
    def test_workflow_status_tracking(self):
        """Test workflow status tracking"""
        workflow_key = "B-2025-10-04-01_L-1"
        
        # Initially no workflow
        assert workflow_key not in self.master_control.workflow_status
        
        # Create workflow
        self.master_control.workflow_status[workflow_key] = {
            "status": "PROCESSING",
            "pipeline": ["PDR", "CRRAK"],
            "current_step": 0,
            "results": {},
            "started_at": "2025-10-04T13:14:00Z"
        }
        
        # Check workflow exists
        assert workflow_key in self.master_control.workflow_status
        assert self.master_control.workflow_status[workflow_key]["status"] == "PROCESSING"


if __name__ == "__main__":
    pytest.main([__file__])
