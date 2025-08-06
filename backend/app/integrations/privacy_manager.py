"""
Privacy and data protection manager for GDPR compliance and user data handling.
"""

import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import re

from .integration_config import integration_settings
from .analytics_processor import AnalyticsProcessor

import logging
logger = logging.getLogger(__name__)


class ConsentCategory(str, Enum):
    """Categories of user consent"""
    ESSENTIAL = "essential"
    ANALYTICS = "analytics"
    INTEGRATIONS = "integrations"
    MARKETING = "marketing"
    PREFERENCES = "preferences"


class DataType(str, Enum):
    """Types of data we collect"""
    VISITOR_ID = "visitor_id"
    IP_ADDRESS = "ip_address"
    USER_AGENT = "user_agent"
    INTERACTION_DATA = "interaction_data"
    SESSION_DATA = "session_data"
    PREFERENCE_DATA = "preference_data"
    ANALYTICS_DATA = "analytics_data"


class ProcessingPurpose(str, Enum):
    """Purposes for data processing"""
    ESSENTIAL_FUNCTIONALITY = "essential_functionality"
    ANALYTICS = "analytics"
    PERSONALIZATION = "personalization"
    PERFORMANCE_MONITORING = "performance_monitoring"
    SECURITY = "security"


@dataclass
class ConsentRecord:
    """User consent record"""
    consent_id: str
    visitor_id: str
    categories: Dict[ConsentCategory, bool]
    granted_at: datetime
    expires_at: Optional[datetime]
    ip_address_hash: Optional[str]
    user_agent_hash: Optional[str]
    consent_string: str  # TCF-style consent string
    

@dataclass
class DataSubjectRequest:
    """GDPR data subject request"""
    request_id: str
    request_type: str  # "access", "rectification", "erasure", "portability"
    visitor_id: str
    contact_email: Optional[str]
    requested_at: datetime
    processed_at: Optional[datetime]
    status: str  # "pending", "processing", "completed", "rejected"
    response_data: Optional[Dict[str, Any]]
    

@dataclass
class DataRetentionPolicy:
    """Data retention policy configuration"""
    data_type: DataType
    retention_days: int
    deletion_method: str  # "hard_delete", "anonymize", "pseudonymize"
    legal_basis: str
    

@dataclass
class PrivacyAuditLog:
    """Privacy audit log entry"""
    log_id: str
    timestamp: datetime
    action: str
    data_type: DataType
    purpose: ProcessingPurpose
    visitor_id: Optional[str]
    details: Dict[str, Any]


class PrivacyManager:
    """Privacy and data protection manager"""
    
    def __init__(self):
        self.config = integration_settings.privacy
        
        # Consent management
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.data_subject_requests: Dict[str, DataSubjectRequest] = {}
        
        # Audit logging
        self.audit_logs: List[PrivacyAuditLog] = []
        
        # Data retention policies
        self.retention_policies = self._initialize_retention_policies()
        
        # Privacy settings
        self.anonymization_enabled = self.config.anonymize_visitor_data
        self.consent_required = self.config.require_consent
    
    def _initialize_retention_policies(self) -> Dict[DataType, DataRetentionPolicy]:
        """Initialize default data retention policies"""
        
        retention_days = self.config.data_retention_days
        
        return {
            DataType.VISITOR_ID: DataRetentionPolicy(
                data_type=DataType.VISITOR_ID,
                retention_days=retention_days,
                deletion_method="hard_delete",
                legal_basis="legitimate_interest"
            ),
            DataType.IP_ADDRESS: DataRetentionPolicy(
                data_type=DataType.IP_ADDRESS,
                retention_days=min(retention_days, 30),  # IP addresses shorter retention
                deletion_method="anonymize",
                legal_basis="legitimate_interest"
            ),
            DataType.USER_AGENT: DataRetentionPolicy(
                data_type=DataType.USER_AGENT,
                retention_days=retention_days,
                deletion_method="anonymize",
                legal_basis="legitimate_interest"
            ),
            DataType.INTERACTION_DATA: DataRetentionPolicy(
                data_type=DataType.INTERACTION_DATA,
                retention_days=retention_days,
                deletion_method="anonymize",
                legal_basis="legitimate_interest"
            ),
            DataType.SESSION_DATA: DataRetentionPolicy(
                data_type=DataType.SESSION_DATA,
                retention_days=7,  # Session data shorter retention
                deletion_method="hard_delete",
                legal_basis="legitimate_interest"
            ),
            DataType.ANALYTICS_DATA: DataRetentionPolicy(
                data_type=DataType.ANALYTICS_DATA,
                retention_days=retention_days,
                deletion_method="pseudonymize",
                legal_basis="legitimate_interest"
            )
        }
    
    def anonymize_ip_address(self, ip_address: str) -> str:
        """Anonymize IP address"""
        
        if not self.config.hash_ip_addresses:
            return ip_address
        
        # Hash IP address with salt
        salt = "privacy_salt_2024"  # In production, use secure random salt
        return hashlib.sha256(f"{ip_address}{salt}".encode()).hexdigest()[:16]
    
    def anonymize_user_agent(self, user_agent: str) -> str:
        """Anonymize user agent while preserving useful information"""
        
        if not self.config.hash_user_agents:
            return user_agent
        
        # Extract only essential browser/OS info
        browser_info = self._extract_browser_info(user_agent)
        os_info = self._extract_os_info(user_agent)
        
        return f"{browser_info}/{os_info}"
    
    def _extract_browser_info(self, user_agent: str) -> str:
        """Extract browser information from user agent"""
        
        user_agent_lower = user_agent.lower()
        
        if "chrome" in user_agent_lower:
            return "Chrome"
        elif "firefox" in user_agent_lower:
            return "Firefox"
        elif "safari" in user_agent_lower and "chrome" not in user_agent_lower:
            return "Safari"
        elif "edge" in user_agent_lower:
            return "Edge"
        else:
            return "Other"
    
    def _extract_os_info(self, user_agent: str) -> str:
        """Extract OS information from user agent"""
        
        user_agent_lower = user_agent.lower()
        
        if "windows" in user_agent_lower:
            return "Windows"
        elif "mac" in user_agent_lower:
            return "macOS"
        elif "linux" in user_agent_lower:
            return "Linux"
        elif "android" in user_agent_lower:
            return "Android"
        elif "iphone" in user_agent_lower or "ipad" in user_agent_lower:
            return "iOS"
        else:
            return "Other"
    
    def generate_visitor_id(self, ip_address: str, user_agent: str) -> str:
        """Generate anonymous but consistent visitor ID"""
        
        # Create visitor ID from hashed IP + anonymized user agent
        anonymized_ip = self.anonymize_ip_address(ip_address)
        anonymized_ua = self.anonymize_user_agent(user_agent)
        
        visitor_data = f"{anonymized_ip}:{anonymized_ua}:{datetime.utcnow().date()}"
        return hashlib.sha256(visitor_data.encode()).hexdigest()[:16]
    
    def record_consent(
        self,
        visitor_id: str,
        categories: Dict[ConsentCategory, bool],
        ip_address: str,
        user_agent: str,
        expires_days: Optional[int] = None
    ) -> str:
        """Record user consent"""
        
        consent_id = str(uuid.uuid4())
        
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        elif not expires_days:
            expires_at = datetime.utcnow() + timedelta(days=365)  # Default 1 year
        
        # Generate consent string (simplified)
        consent_string = self._generate_consent_string(categories)
        
        consent_record = ConsentRecord(
            consent_id=consent_id,
            visitor_id=visitor_id,
            categories=categories,
            granted_at=datetime.utcnow(),
            expires_at=expires_at,
            ip_address_hash=self.anonymize_ip_address(ip_address),
            user_agent_hash=hashlib.sha256(user_agent.encode()).hexdigest()[:16],
            consent_string=consent_string
        )
        
        self.consent_records[consent_id] = consent_record
        
        # Log consent
        self._log_privacy_action(
            action="consent_granted",
            data_type=DataType.PREFERENCE_DATA,
            purpose=ProcessingPurpose.ESSENTIAL_FUNCTIONALITY,
            visitor_id=visitor_id,
            details={"categories": list(categories.keys()), "expires_at": expires_at.isoformat() if expires_at else None}
        )
        
        logger.info(f"Recorded consent for visitor {visitor_id}: {consent_string}")
        return consent_id
    
    def get_visitor_consent(self, visitor_id: str) -> Optional[ConsentRecord]:
        """Get current consent for a visitor"""
        
        # Find most recent non-expired consent
        visitor_consents = [
            consent for consent in self.consent_records.values()
            if (consent.visitor_id == visitor_id and 
                (consent.expires_at is None or consent.expires_at > datetime.utcnow()))
        ]
        
        if not visitor_consents:
            return None
        
        # Return most recent
        return max(visitor_consents, key=lambda c: c.granted_at)
    
    def has_consent_for_purpose(
        self,
        visitor_id: str,
        purpose: ProcessingPurpose
    ) -> bool:
        """Check if visitor has given consent for specific purpose"""
        
        if not self.consent_required:
            return True
        
        consent = self.get_visitor_consent(visitor_id)
        if not consent:
            # No consent recorded - only allow essential functionality
            return purpose == ProcessingPurpose.ESSENTIAL_FUNCTIONALITY
        
        # Map purposes to consent categories
        purpose_mapping = {
            ProcessingPurpose.ESSENTIAL_FUNCTIONALITY: ConsentCategory.ESSENTIAL,
            ProcessingPurpose.ANALYTICS: ConsentCategory.ANALYTICS,
            ProcessingPurpose.PERSONALIZATION: ConsentCategory.INTEGRATIONS,
            ProcessingPurpose.PERFORMANCE_MONITORING: ConsentCategory.ANALYTICS,
            ProcessingPurpose.SECURITY: ConsentCategory.ESSENTIAL
        }
        
        required_category = purpose_mapping.get(purpose, ConsentCategory.ESSENTIAL)
        return consent.categories.get(required_category, False)
    
    def _generate_consent_string(self, categories: Dict[ConsentCategory, bool]) -> str:
        """Generate consent string representation"""
        
        # Simple binary string where each position represents a category
        category_order = [
            ConsentCategory.ESSENTIAL,
            ConsentCategory.ANALYTICS, 
            ConsentCategory.INTEGRATIONS,
            ConsentCategory.MARKETING,
            ConsentCategory.PREFERENCES
        ]
        
        consent_bits = []
        for category in category_order:
            consent_bits.append("1" if categories.get(category, False) else "0")
        
        return "".join(consent_bits)
    
    def create_data_subject_request(
        self,
        request_type: str,
        visitor_id: str,
        contact_email: Optional[str] = None
    ) -> str:
        """Create a GDPR data subject request"""
        
        if request_type not in ["access", "rectification", "erasure", "portability"]:
            raise ValueError(f"Invalid request type: {request_type}")
        
        request_id = str(uuid.uuid4())
        
        request = DataSubjectRequest(
            request_id=request_id,
            request_type=request_type,
            visitor_id=visitor_id,
            contact_email=contact_email,
            requested_at=datetime.utcnow(),
            processed_at=None,
            status="pending",
            response_data=None
        )
        
        self.data_subject_requests[request_id] = request
        
        # Log the request
        self._log_privacy_action(
            action=f"data_subject_request_{request_type}",
            data_type=DataType.VISITOR_ID,
            purpose=ProcessingPurpose.ESSENTIAL_FUNCTIONALITY,
            visitor_id=visitor_id,
            details={"request_id": request_id, "contact_email": contact_email}
        )
        
        logger.info(f"Created data subject request: {request_type} for visitor {visitor_id}")
        return request_id
    
    async def process_data_access_request(
        self,
        request_id: str,
        analytics_processor: AnalyticsProcessor
    ) -> Dict[str, Any]:
        """Process a data access request (GDPR Article 15)"""
        
        if request_id not in self.data_subject_requests:
            raise ValueError(f"Request {request_id} not found")
        
        request = self.data_subject_requests[request_id]
        if request.request_type != "access":
            raise ValueError(f"Request {request_id} is not an access request")
        
        request.status = "processing"
        visitor_id = request.visitor_id
        
        # Collect all data for this visitor
        visitor_data = {
            "visitor_id": visitor_id,
            "data_collected": datetime.utcnow().isoformat(),
            "retention_policies": {dt.value: asdict(policy) for dt, policy in self.retention_policies.items()},
            "consent_records": [],
            "visitor_profile": None,
            "interaction_events": [],
            "privacy_logs": []
        }
        
        # Get consent records
        visitor_consents = [
            asdict(consent) for consent in self.consent_records.values()
            if consent.visitor_id == visitor_id
        ]
        visitor_data["consent_records"] = visitor_consents
        
        # Get visitor profile and journey from analytics
        profile = analytics_processor.get_visitor_journey_analysis(visitor_id)
        if profile:
            visitor_data["visitor_profile"] = profile
        
        # Get privacy audit logs for this visitor
        visitor_logs = [
            asdict(log) for log in self.audit_logs
            if log.visitor_id == visitor_id
        ]
        visitor_data["privacy_logs"] = visitor_logs
        
        # Complete the request
        request.status = "completed"
        request.processed_at = datetime.utcnow()
        request.response_data = visitor_data
        
        # Log completion
        self._log_privacy_action(
            action="data_access_request_completed",
            data_type=DataType.VISITOR_ID,
            purpose=ProcessingPurpose.ESSENTIAL_FUNCTIONALITY,
            visitor_id=visitor_id,
            details={"request_id": request_id}
        )
        
        logger.info(f"Completed data access request {request_id} for visitor {visitor_id}")
        return visitor_data
    
    async def process_data_erasure_request(
        self,
        request_id: str,
        analytics_processor: AnalyticsProcessor
    ) -> bool:
        """Process a data erasure request (GDPR Article 17 - Right to be forgotten)"""
        
        if request_id not in self.data_subject_requests:
            raise ValueError(f"Request {request_id} not found")
        
        request = self.data_subject_requests[request_id]
        if request.request_type != "erasure":
            raise ValueError(f"Request {request_id} is not an erasure request")
        
        request.status = "processing"
        visitor_id = request.visitor_id
        
        # Remove visitor profile from analytics
        if visitor_id in analytics_processor.visitor_profiles:
            del analytics_processor.visitor_profiles[visitor_id]
        
        # Remove interaction events
        analytics_processor.interaction_events = [
            event for event in analytics_processor.interaction_events
            if event.visitor_id != visitor_id
        ]
        
        # Remove sessions
        analytics_processor.active_sessions = {
            session_id: session for session_id, session in analytics_processor.active_sessions.items()
            if session.visitor_id != visitor_id
        }
        
        # Remove consent records
        consent_ids_to_remove = [
            consent_id for consent_id, consent in self.consent_records.items()
            if consent.visitor_id == visitor_id
        ]
        for consent_id in consent_ids_to_remove:
            del self.consent_records[consent_id]
        
        # Anonymize privacy logs (don't delete for audit purposes)
        for log in self.audit_logs:
            if log.visitor_id == visitor_id:
                log.visitor_id = "ERASED"
        
        # Complete the request
        request.status = "completed"
        request.processed_at = datetime.utcnow()
        request.response_data = {"erased": True, "visitor_id": visitor_id}
        
        # Log completion
        self._log_privacy_action(
            action="data_erasure_request_completed",
            data_type=DataType.VISITOR_ID,
            purpose=ProcessingPurpose.ESSENTIAL_FUNCTIONALITY,
            visitor_id=None,  # Don't log the erased visitor ID
            details={"request_id": request_id}
        )
        
        logger.info(f"Completed data erasure request {request_id} for visitor {visitor_id}")
        return True
    
    def _log_privacy_action(
        self,
        action: str,
        data_type: DataType,
        purpose: ProcessingPurpose,
        visitor_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log privacy-related action for audit purposes"""
        
        log_entry = PrivacyAuditLog(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            action=action,
            data_type=data_type,
            purpose=purpose,
            visitor_id=visitor_id,
            details=details or {}
        )
        
        self.audit_logs.append(log_entry)
        
        # Limit audit log size (keep last 10000 entries)
        if len(self.audit_logs) > 10000:
            self.audit_logs = self.audit_logs[-10000:]
    
    async def apply_data_retention_policies(
        self,
        analytics_processor: AnalyticsProcessor
    ) -> Dict[str, int]:
        """Apply data retention policies and clean up old data"""
        
        results = {}
        current_time = datetime.utcnow()
        
        for data_type, policy in self.retention_policies.items():
            cutoff_time = current_time - timedelta(days=policy.retention_days)
            removed_count = 0
            
            if data_type == DataType.INTERACTION_DATA:
                # Remove old interaction events
                old_count = len(analytics_processor.interaction_events)
                analytics_processor.interaction_events = [
                    event for event in analytics_processor.interaction_events
                    if event.timestamp >= cutoff_time
                ]
                removed_count = old_count - len(analytics_processor.interaction_events)
            
            elif data_type == DataType.SESSION_DATA:
                # Remove old sessions
                old_count = len(analytics_processor.active_sessions)
                analytics_processor.active_sessions = {
                    session_id: session
                    for session_id, session in analytics_processor.active_sessions.items()
                    if session.start_time >= cutoff_time
                }
                removed_count = old_count - len(analytics_processor.active_sessions)
            
            elif data_type == DataType.VISITOR_ID:
                # Remove old visitor profiles
                old_count = len(analytics_processor.visitor_profiles)
                analytics_processor.visitor_profiles = {
                    visitor_id: profile
                    for visitor_id, profile in analytics_processor.visitor_profiles.items()
                    if profile.last_visit >= cutoff_time
                }
                removed_count = old_count - len(analytics_processor.visitor_profiles)
            
            results[data_type.value] = removed_count
            
            if removed_count > 0:
                self._log_privacy_action(
                    action="data_retention_cleanup",
                    data_type=data_type,
                    purpose=ProcessingPurpose.ESSENTIAL_FUNCTIONALITY,
                    details={"removed_count": removed_count, "retention_days": policy.retention_days}
                )
        
        # Clean up old consent records
        old_consents = [
            consent_id for consent_id, consent in self.consent_records.items()
            if consent.expires_at and consent.expires_at <= current_time
        ]
        
        for consent_id in old_consents:
            del self.consent_records[consent_id]
        
        results["expired_consents"] = len(old_consents)
        
        logger.info(f"Applied data retention policies: {results}")
        return results
    
    def get_privacy_dashboard_data(self) -> Dict[str, Any]:
        """Get data for privacy compliance dashboard"""
        
        current_time = datetime.utcnow()
        
        # Consent statistics
        active_consents = [
            consent for consent in self.consent_records.values()
            if consent.expires_at is None or consent.expires_at > current_time
        ]
        
        consent_by_category = {}
        for category in ConsentCategory:
            consent_by_category[category.value] = sum(
                1 for consent in active_consents
                if consent.categories.get(category, False)
            )
        
        # Request statistics
        request_by_type = {}
        request_by_status = {}
        
        for request in self.data_subject_requests.values():
            request_by_type[request.request_type] = request_by_type.get(request.request_type, 0) + 1
            request_by_status[request.status] = request_by_status.get(request.status, 0) + 1
        
        # Recent activity
        recent_logs = [
            log for log in self.audit_logs
            if (current_time - log.timestamp).days <= 7
        ]
        
        return {
            "consent_summary": {
                "total_active_consents": len(active_consents),
                "consent_by_category": consent_by_category,
                "consent_required": self.consent_required
            },
            "data_subject_requests": {
                "total_requests": len(self.data_subject_requests),
                "by_type": request_by_type,
                "by_status": request_by_status
            },
            "retention_policies": {
                dt.value: {"days": policy.retention_days, "method": policy.deletion_method}
                for dt, policy in self.retention_policies.items()
            },
            "recent_activity": {
                "privacy_actions_7d": len(recent_logs),
                "anonymization_enabled": self.anonymization_enabled
            },
            "compliance_features": {
                "gdpr_compliance": self.config.gdpr_compliance,
                "data_export_enabled": self.config.enable_data_export,
                "data_deletion_enabled": self.config.enable_data_deletion
            }
        }


# Global privacy manager instance  
privacy_manager = PrivacyManager()