#!/usr/bin/env python3
"""
Unit and integration tests for TLS Certificate Monitoring
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import (
    parse_domains,
    check_threshold,
    load_config,
    validate_config,
)


class TestParseDomains(unittest.TestCase):
    """Test domain parsing with optional runbook URLs"""
    
    def test_parse_simple_domains(self):
        """Test parsing domains without runbooks"""
        domains_str = "example.com,test.com"
        result = parse_domains(domains_str)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("example.com", None))
        self.assertEqual(result[1], ("test.com", None))
    
    def test_parse_domains_with_runbooks(self):
        """Test parsing domains with runbook URLs"""
        domains_str = "example.com:https://runbook.com/fix,test.com"
        result = parse_domains(domains_str)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("example.com", "https://runbook.com/fix"))
        self.assertEqual(result[1], ("test.com", None))
    
    def test_parse_mixed_domains(self):
        """Test parsing mixed domains with and without runbooks"""
        domains_str = "example.com:https://wiki.com/ssl,test.com,another.com:https://runbook.io"
        result = parse_domains(domains_str)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("example.com", "https://wiki.com/ssl"))
        self.assertEqual(result[1], ("test.com", None))
        self.assertEqual(result[2], ("another.com", "https://runbook.io"))
    
    def test_parse_empty_string(self):
        """Test parsing empty string"""
        domains_str = ""
        result = parse_domains(domains_str)
        
        self.assertEqual(len(result), 0)
    
    def test_parse_whitespace_handling(self):
        """Test that whitespace is properly trimmed"""
        domains_str = "  example.com  ,  test.com : https://runbook.com  "
        result = parse_domains(domains_str)
        
        self.assertEqual(result[0], ("example.com", None))
        self.assertEqual(result[1], ("test.com", "https://runbook.com"))


class TestCheckThreshold(unittest.TestCase):
    """Test certificate threshold checking logic"""
    
    def test_check_threshold_below_limit(self):
        """Test when days remaining is below threshold"""
        cert_info = {
            "status": "OK",
            "days_remaining": 15,
            "error": None,
        }
        threshold_days = 30
        
        result = check_threshold(cert_info, threshold_days)
        self.assertTrue(result)
    
    def test_check_threshold_above_limit(self):
        """Test when days remaining is above threshold"""
        cert_info = {
            "status": "OK",
            "days_remaining": 60,
            "error": None,
        }
        threshold_days = 30
        
        result = check_threshold(cert_info, threshold_days)
        self.assertFalse(result)
    
    def test_check_threshold_at_limit(self):
        """Test when days remaining equals threshold"""
        cert_info = {
            "status": "OK",
            "days_remaining": 30,
            "error": None,
        }
        threshold_days = 30
        
        result = check_threshold(cert_info, threshold_days)
        self.assertFalse(result)
    
    def test_check_threshold_error_status(self):
        """Test that ERROR status always triggers alert"""
        cert_info = {
            "status": "ERROR",
            "days_remaining": 365,
            "error": "Connection failed",
        }
        threshold_days = 30
        
        result = check_threshold(cert_info, threshold_days)
        self.assertTrue(result)
    
    def test_check_threshold_none_days(self):
        """Test that None days_remaining triggers alert"""
        cert_info = {
            "status": "OK",
            "days_remaining": None,
            "error": None,
        }
        threshold_days = 30
        
        result = check_threshold(cert_info, threshold_days)
        self.assertTrue(result)


class TestLoadConfig(unittest.TestCase):
    """Test configuration loading"""
    
    def test_load_config_with_arguments(self):
        """Test loading config with command-line arguments"""
        config = load_config(
            domains="example.com,test.com",
            threshold=45
        )
        
        self.assertEqual(config["domains_str"], "example.com,test.com")
        self.assertEqual(config["threshold_days"], 45)
    
    def test_load_config_without_arguments(self):
        """Test loading config without arguments falls back to env/defaults"""
        config = load_config(domains=None, threshold=None)
        
        # Should not raise exception
        self.assertIsNotNone(config)
        self.assertIn("domains_str", config)
        self.assertIn("threshold_days", config)
    
    def test_load_config_partial_arguments(self):
        """Test loading config with only some arguments"""
        config = load_config(domains="example.com", threshold=None)
        
        self.assertEqual(config["domains_str"], "example.com")
        self.assertEqual(config["threshold_days"], 30)  # Default


class TestValidateConfig(unittest.TestCase):
    """Test configuration validation"""
    
    def test_validate_config_valid(self):
        """Test that valid config passes validation"""
        config = {
            "domains_str": "example.com,test.com",
            "threshold_days": 30,
        }
        
        # Should not raise exception
        validate_config(config)
    
    def test_validate_config_missing_domains(self):
        """Test that missing domains raises error"""
        config = {
            "domains_str": "",
            "threshold_days": 30,
        }
        
        with self.assertRaises(RuntimeError) as context:
            validate_config(config)
        
        self.assertIn("MONITOR_DOMAINS", str(context.exception))


class TestDomainParsingEdgeCases(unittest.TestCase):
    """Test edge cases in domain parsing"""
    
    def test_parse_domain_with_multiple_colons(self):
        """Test domain parsing with URL containing multiple colons"""
        domains_str = "example.com:https://runbook.com:8080/fix"
        result = parse_domains(domains_str)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "example.com")
        self.assertEqual(result[0][1], "https://runbook.com:8080/fix")
    
    def test_parse_domain_with_query_params(self):
        """Test domain parsing with URL containing query params"""
        domains_str = "example.com:https://wiki.com/fix?env=prod&team=ops"
        result = parse_domains(domains_str)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "https://wiki.com/fix?env=prod&team=ops")
    
    def test_parse_subdomain(self):
        """Test parsing subdomains"""
        domains_str = "api.example.com,www.test.com:https://runbook.com"
        result = parse_domains(domains_str)
        
        self.assertEqual(result[0], ("api.example.com", None))
        self.assertEqual(result[1], ("www.test.com", "https://runbook.com"))


if __name__ == "__main__":
    unittest.main()
