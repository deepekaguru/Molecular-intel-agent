import re
import hashlib
import json
from typing import Dict, Any
from datetime import datetime
import os

class DataSecurityHandler:
    """Handle PII masking, secrets management, and secure logging"""
    
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'date_of_birth': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'name': r'\b(patient|name|mr|mrs|ms|dr)\.?\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b',
        'mrn': r'\bMRN[\s:]?\d{6,10}\b',
        'zip_code': r'\b\d{5}(-\d{4})?\b',
        'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
    }
    
    @staticmethod
    def mask_pii(text: str) -> Dict[str, Any]:
        """Detect and mask PII in text"""
        masked_text = text
        detected_pii = []
        
        for pii_type, pattern in DataSecurityHandler.PII_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                detected_pii.append(pii_type)
                masked_text = re.sub(pattern, f'[{pii_type.upper()}]', masked_text)
        
        return {
            'masked_text': masked_text,
            'pii_detected': detected_pii,
            'original_length': len(text),
            'masked_length': len(masked_text)
        }
    
    @staticmethod
    def hash_identifier(identifier: str, salt: str = None) -> str:
        """Hash identifiers for pseudonymization"""
        if salt is None:
            salt = os.getenv('HASH_SALT', 'default-salt-change-in-prod')
        
        return hashlib.sha256(f"{identifier}{salt}".encode()).hexdigest()[:16]
    
    @staticmethod
    def anonymize_patient_data(patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize patient data while preserving clinical utility"""
        anonymized = patient_data.copy()
        
        if 'patient_name' in anonymized:
            anonymized['patient_id'] = DataSecurityHandler.hash_identifier(anonymized['patient_name'])
            del anonymized['patient_name']
        
        pii_fields = ['name', 'address', 'phone', 'email', 'ssn']
        for field in pii_fields:
            if field in anonymized:
                del anonymized[field]
        
        if 'age' in anonymized:
            age = anonymized['age']
            if age < 18:
                anonymized['age_group'] = '<18'
            elif age < 40:
                anonymized['age_group'] = '18-39'
            elif age < 65:
                anonymized['age_group'] = '40-64'
            else:
                anonymized['age_group'] = '65+'
        
        return anonymized
    
    @staticmethod
    def secure_log(event: str, data: Dict[str, Any], level: str = 'INFO'):
        """Log events with PII masking — fails silently if file not writable"""
        safe_data = {}
        for key, value in data.items():
            if key in ['patient_id', 'cancer_type', 'mutations']:
                safe_data[key] = value
            elif isinstance(value, str):
                masked_result = DataSecurityHandler.mask_pii(value)
                safe_data[key] = masked_result['masked_text']
            else:
                safe_data[key] = '[REDACTED]'
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'event': event,
            'data': safe_data
        }

        # Try file logging first, fall back to print (Streamlit Cloud safe)
        try:
            log_file = '/tmp/logs/secure.log'
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            print(f"SECURE_LOG | {level} | {event} | {json.dumps(safe_data)}")
    
    @staticmethod
    def load_secrets_from_env() -> Dict[str, str]:
        """Load secrets from environment variables, not code"""
        required_secrets = [
            'NEO4J_URI',
            'NEO4J_USER',
            'NEO4J_PASSWORD',
        ]
        
        secrets = {}
        missing = []
        
        for secret in required_secrets:
            value = os.getenv(secret)
            if not value:
                missing.append(secret)
            else:
                secrets[secret] = value
        
        if missing:
            raise ValueError(f"Missing required secrets: {', '.join(missing)}")
        
        return secrets
