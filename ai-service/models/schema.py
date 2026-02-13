from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON, Enum as SAEnum
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid
import enum

Base = declarative_base()

# SQLite UUID compatibility
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(36), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import UUID
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value

class IdeaStage(enum.Enum):
    GENERATED = "GENERATED"
    VALIDATED = "VALIDATED"
    IN_EXPERIMENT = "IN_EXPERIMENT"
    COMMITTED = "COMMITTED"
    ARCHIVED = "ARCHIVED"

class FounderProfile(Base):
    __tablename__ = "founder_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    # Stored as JSON: {"technical": 0.8, "domain": ["fintech", "edtech"], "leadership": 0.5}
    skills = Column(JSON, default={})
    
    # 1-10 scale
    risk_appetite = Column(Integer, default=5)
    
    # Financial runway in months
    financial_runway = Column(Integer)
    
    # Unfair advantages / Thesis
    # stored as list of strings
    thesis_vector = Column(JSON, default=[])
    
    technical_feasibility_override = Column(Boolean, default=False) # Contrarian override enablement
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ideas = relationship("IdeaDNA", back_populates="founder")

class IdeaDNA(Base):
    __tablename__ = "idea_dna"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    founder_id = Column(GUID(), ForeignKey("founder_profiles.id"))
    
    name = Column(String)
    tagline = Column(String)
    description = Column(String)
    problem_statement = Column(String)
    target_customer = Column(String)
    
    stage = Column(String, default=IdeaStage.GENERATED.value) 
    
    # Current Score (0-100)
    conviction_score = Column(Integer, default=0)
    
    # Origins
    origin_lens = Column(String) # e.g., "GAP_MATRIX", "CONTRARIAN"
    
    # Metrics
    market_size_score = Column(Integer)
    tech_feasibility_score = Column(Integer)
    unit_economics_score = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    founder = relationship("FounderProfile", back_populates="ideas")
    snapshots = relationship("ConvictionSnapshot", back_populates="idea")

class ConvictionSnapshot(Base):
    __tablename__ = "conviction_snapshots"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    idea_id = Column(GUID(), ForeignKey("idea_dna.id"))
    
    total_score = Column(Integer)
    
    # Component scores at this snapshot
    market_score = Column(Integer)
    timing_score = Column(Integer)
    execution_score = Column(Integer)
    
    # Reason for update
    change_reason = Column(String) # "Unit Economics Update", "Market Signal Shift"
    delta = Column(Integer) # +5, -10
    
    recorded_at = Column(DateTime, default=datetime.utcnow)

    idea = relationship("IdeaDNA", back_populates="snapshots")

class MarketSignal(Base):
    __tablename__ = "market_signals"

    # Composite key or hashed ID: sector + region
    id = Column(String, primary_key=True) 
    
    sector = Column(String) # "EdTech"
    region = Column(String) # "US"
    
    # Cached Intelligence
    # { "growth_rate": 0.15, "market_leaders": [...], "cac_benchmark": 150.0 }
    data = Column(JSON)
    
    last_updated = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
