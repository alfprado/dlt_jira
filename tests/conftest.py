"""
Configuration and fixtures for tests
"""
import pytest
import sys
from unittest.mock import Mock, patch
from run_pipeline import main

@pytest.fixture
def mock_pipeline():
    """Fixture para mock do JiraDataPipeline"""
    mock_pipeline = Mock()
    mock_pipeline.run_extraction_only.return_value = True
    mock_pipeline.run_dbt_only.return_value = True
    mock_pipeline.run_full_pipeline.return_value = True
    return mock_pipeline

@pytest.fixture
def mock_pipeline_class(mock_pipeline):
    """Fixture para mock da classe JiraDataPipeline"""
    with patch('run_pipeline.JiraDataPipeline') as mock_class:
        mock_class.return_value = mock_pipeline
        yield mock_class

@pytest.fixture
def mock_sys_exit():
    """Fixture para mock do sys.exit"""
    with patch('sys.exit') as mock_exit:
        yield mock_exit
