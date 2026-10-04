"""
SIH26146 — Normalized Data Contract & Schema Definitions
Conforming strictly to docs/04-data-contract.md and MASTER_PROJECT_PROMPT.md.
"""

from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    INCOMPLETE = "INCOMPLETE"
    AMBIGUOUS = "AMBIGUOUS"
    QUARANTINED = "QUARANTINED"


class InvestigativePriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFORMATIONAL = "INFORMATIONAL"


class TargetType(str, Enum):
    ENTITY = "entity"
    WALLET = "wallet"
    TRANSACTION = "transaction"
    IP = "ip"


class NormalizedRecord(BaseModel):
    """
    Unified canonical representation for both network observations and blockchain transactions.
    Preserves raw data and provenance.
    """
    # Provenance metadata
    source_file_id: str = Field(..., description="Originating filename or stream identifier")
    source_row_id: str = Field(..., description="Line index or record key in original data")
    schema_version: str = Field("v1.0.0", description="Contract version")
    validation_status: ValidationStatus = Field(ValidationStatus.VALID, description="Data quality classification")
    validation_errors: List[str] = Field(default_factory=list, description="Reason codes/messages if invalid")
    raw_timestamp: Optional[str] = Field(None, description="Original unprocessed timestamp string")
    timestamp_normalization_status: str = Field("NORMALIZED", description="Audit note on date parsing")

    # Core temporal & network fields
    timestamp: datetime = Field(..., description="Canonical UTC ISO timestamp")
    src_ip: str = Field(..., description="Source IPv4 or IPv6 address")
    dst_ip: str = Field(..., description="Destination IPv4 or IPv6 address")
    src_port: int = Field(..., ge=0, le=65535, description="Source port (0-65535)")
    dst_port: int = Field(..., ge=0, le=65535, description="Destination port (0-65535)")

    # Blockchain transaction fields (nullable if record is pure network telemetry)
    txid: Optional[str] = Field(None, description="Bitcoin transaction hash (64 hex characters)")
    input_addresses: List[str] = Field(default_factory=list, description="List of input wallet addresses")
    output_addresses: List[str] = Field(default_factory=list, description="List of output wallet addresses")
    input_amounts: List[float] = Field(default_factory=list, description="Amounts associated with inputs (BTC)")
    output_amounts: List[float] = Field(default_factory=list, description="Amounts associated with outputs (BTC)")

    # Contextual / Geo-IP metadata
    geo_country: Optional[str] = Field(None, description="ISO country code from local offline DB")
    asn: Optional[str] = Field(None, description="Autonomous System Number (e.g., AS15169)")
    fee: Optional[float] = Field(None, description="Transaction fee in BTC")
    script_type: Optional[str] = Field(None, description="Script type (e.g., P2PKH, P2SH, P2WPKH, TAPROOT)")

    def total_output_amount(self) -> float:
        return sum(self.output_amounts) if self.output_amounts else 0.0

    def total_input_amount(self) -> float:
        return sum(self.input_amounts) if self.input_amounts else 0.0


class CorrelationRecord(BaseModel):
    """
    Evidence record detailing explicit linkage between network observations and blockchain transactions.
    """
    correlation_id: str = Field(..., description="Unique correlation identifier")
    network_observation_id: str = Field(..., description="ID/row of network telemetry record")
    txid: str = Field(..., description="Correlated transaction ID")
    wallet_references: List[str] = Field(default_factory=list, description="Wallets linked via this transaction")
    match_methods: List[str] = Field(default_factory=list, description="Match types: EXACT_TXID, TEMPORAL_PROXIMITY, REPEATED_IP")
    matched_fields: List[str] = Field(default_factory=list, description="Fields that matched, e.g. ['txid', 'timestamp']")
    time_delta_seconds: Optional[float] = Field(None, description="Seconds between network observation and transaction timestamp")
    correlation_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in link (0.0=weak, 1.0=exact)")
    confidence_reasons: List[str] = Field(default_factory=list, description="Explainable justifications for confidence")
    source_record_ids: List[str] = Field(default_factory=list, description="Source provenance IDs")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Alert(BaseModel):
    """
    Investigative lead produced by the detection and evidence fusion pipeline.
    Maintains strict separation between anomaly score, correlation confidence, and investigative priority.
    """
    alert_id: str = Field(..., description="Unique alert identifier e.g. ALT-00101")
    target_id: str = Field(..., description="Identifier of flagged entity, wallet, or txid")
    target_type: TargetType = Field(..., description="Type of investigative target")
    
    # Core separate metrics
    investigative_priority: InvestigativePriority = Field(..., description="Actionability tier for analyst")
    priority_score: float = Field(..., ge=0.0, le=1.0, description="Fused investigative priority ranking (0-1)")
    anomaly_score: float = Field(..., ge=0.0, le=1.0, description="Model-derived behavioral anomaly score")
    correlation_confidence: float = Field(..., ge=0.0, le=1.0, description="Strength of network-blockchain linkage")

    # Structured explainability
    primary_reasons: List[str] = Field(default_factory=list, description="Bullet-point plain-language rationale")
    model_evidence: Dict[str, Any] = Field(default_factory=dict, description="Contributing features and importance values")
    graph_evidence: Dict[str, Any] = Field(default_factory=dict, description="Structural indicators: fan-in, fan-out, hops")
    temporal_evidence: Dict[str, Any] = Field(default_factory=dict, description="Burstiness, velocity, timestamps")
    correlation_evidence: Dict[str, Any] = Field(default_factory=dict, description="Associated IPs, match methods, ASNs")

    # Audit & provenance
    source_record_ids: List[str] = Field(default_factory=list, description="Provenance tracing back to raw records")
    explanation_narrative: str = Field(..., description="Synthesized analyst summary report")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Evidence fusion confidence breakdown
    fused_confidence: Optional[float] = Field(None, description="Fused multi-signal confidence score")
    confidence_breakdown: Dict[str, float] = Field(default_factory=dict, description="Component-level confidence breakdown")
    provenance_details: Dict[str, Any] = Field(default_factory=dict, description="Structured audit trail provenance")
    
    # Forensic safety disclaimer
    disclaimer: str = Field(
        default="Investigative lead for human review only. This finding does not establish identity, guilt, or criminality.",
        description="Mandatory forensic boundary disclaimer"
    )


class ValidationSummary(BaseModel):
    """Summary of data ingestion validation results."""
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    incomplete_records: int = 0
    quarantined_records: int = 0
    error_counts_by_type: Dict[str, int] = Field(default_factory=dict)
    source_files: List[str] = Field(default_factory=list)
