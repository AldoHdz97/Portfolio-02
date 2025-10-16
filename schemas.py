from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any
from enum import Enum
import re

######################CAMPUS NORMALIZATION UTILS##########################

CAMPUS_MAPPING = {
    'MTY': 'Monterrey',
    'PUE': 'Puebla',
    'GDL': 'Guadalajara',
    'CDJ': 'Ciudad Juárez',
    'TOL': 'Toluca',
    'CCM': 'Ciudad de México',
    'CEM': 'Estado de México',
    'QRO': 'Querétaro',
    'CHI': 'Chihuahua',
    'SIN': 'Sinaloa',
    'AGS': 'Aguascalientes',
    'COB': 'Ciudad Obregón',
    'LEO': 'León',
    'LAG': 'Laguna',
    'SON': 'Sonora',
    'HGO': 'Hidalgo',
    'SLP': 'San Luis Potosí',
    'CVA': 'Cuernavaca',
    'CSF': 'Santa Fe',
    'SAL': 'Saltillo',
}

class CampusID(str, Enum):
    MTY = "MTY"
    PUE = "PUE"
    GDL = "GDL"
    CDJ = "CDJ"
    TOL = "TOL"
    CCM = "CCM"
    CEM = "CEM"
    QRO = "QRO"
    CHI = "CHI"
    SIN = "SIN"
    AGS = "AGS"
    COB = "COB"
    LEO = "LEO"
    LAG = "LAG"
    SON = "SON"
    HGO = "HGO"
    SLP = "SLP"
    CVA = "CVA"
    CSF = "CSF"
    SAL = "SAL"

# ============================================================================
# PUBLICATIONS DATA STRUCTURE
# ============================================================================

class Publication(BaseModel):

    platform: str = Field(
        ..., 
        description="Social media platform: Instagram or Facebook"
    )
    content: str = Field(
        ..., 
        description="The actual text/description of the post"
    )
    interacciones: int = Field(
        ..., 
        description="Total interactions (likes + comments + shares + reactions) for this post"
    )
    alcance: int = Field(
        ..., 
        description="Total reach - number of unique users who saw this post"
    )
    engagement_score: int = Field(
        ..., 
        description="Calculated engagement metric: (interacciones × 10) + alcance"
    )
    
    class Config:
        extra = 'ignore'

class CampusPublications(BaseModel):
    """Publications for one campus - up to 8 posts (4 Instagram + 4 Facebook)"""
    campus_id: CampusID = Field(
        ..., 
        description="Campus identifier - must be one of the 20 valid campus codes"
    )
    publications: List[Publication] = Field(
        ..., 
        description="List of top publications for this campus (max 8: 4 Instagram + 4 Facebook)"
    )

class PublicationsData(BaseModel):
    """Root structure for publications JSON"""
    campuses: List[CampusPublications] = Field(
        ..., 
        description="List of all campuses with their publications"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata about the dataset"
    )

# ============================================================================
# METRICS DATA STRUCTURE
# ============================================================================

class RegionMetricsCurrent(BaseModel):
    """Current month metrics - no REGION field"""
    POST_COMMENTS__SUM: int
    ALCANCE_TOTAL: float
    VOLUMEN_DE_PUBLICACIONES: int
    INTERACCIONES_TOTALES: int

class RegionMetricsPrevious(BaseModel):
    """Previous year metrics - no REGION field"""
    POST_COMMENTS__SUM: int
    ALCANCE_TOTAL: float
    VOLUMEN_DE_PUBLICACIONES: int
    INTERACCIONES_TOTALES: int

class RegionCombined(BaseModel):
    """Combined metrics for one campus"""
    campus_id: str
    campus_name: str
    current_month: RegionMetricsCurrent
    previous_year_month: RegionMetricsPrevious

class MetricsData(BaseModel):
    """Root structure for metrics JSON"""
    regions: List[RegionCombined]
    metadata: Dict[str, Any] = Field(default_factory=dict)

# ============================================================================
# SCORES DATA STRUCTURE
# ============================================================================

class PlatformScores(BaseModel):
    """Scores for one platform"""
    visibilidad: Optional[int] = None
    visibilidad_categoria: Optional[str] = None
    resonancia: Optional[int] = None
    resonancia_categoria: Optional[str] = None
    permanencia: Optional[int] = None
    permanencia_categoria: Optional[str] = None
    sentimiento: Optional[int] = None
    sentimiento_categoria: Optional[str] = None
    salud_de_marca: Optional[int] = None
    salud_de_marca_categoria: Optional[str] = None

class CampusPerformance(BaseModel):
    """Performance scores for one campus"""
    campus_id: str
    campus_name: str
    facebook: PlatformScores
    twitter: PlatformScores
    instagram: PlatformScores
    totales: PlatformScores

class ScoresData(BaseModel):
    """Root structure for scores JSON"""
    campuses: List[CampusPerformance]
    metadata: Dict[str, Any] = Field(default_factory=dict)

######################AGENT SCHEMAS (For CrewAI Agents)##########################

# ============================================================================
# AGENT 1: VALIDATOR
# ============================================================================

class CampusValidation(BaseModel):
    """Validation status for one campus"""
    campus_id: str
    campus_name: str
    has_publications: bool
    publication_count: int
    has_current_metrics: bool
    has_previous_metrics: bool
    has_platform_scores: bool
    is_complete: bool
    notes: Optional[str] = None

class ValidationReport(BaseModel):
    """Agent 1 output - data validation report"""
    validations: List[CampusValidation]
    total_campuses: int = 0
    complete_campuses: int = 0
    incomplete_campuses: int = 0
    summary: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def calculate_totals(self):
        self.total_campuses = len(self.validations)
        self.complete_campuses = sum(1 for v in self.validations if v.is_complete)
        self.incomplete_campuses = self.total_campuses - self.complete_campuses
        return self

# ============================================================================
# AGENT 2: INSIGHT GENERATOR
# ============================================================================

class CampusInsight(BaseModel):
    """One insight for one campus"""
    campus_id: str
    campus_name: str
    insight_text: str
    month: str = "agosto"
    year: int = 2025

class InsightsReport(BaseModel):
    """Agent 2 output - insights for all campuses"""
    insights: List[CampusInsight]
    total_insights: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def set_total(self):
        self.total_insights = len(self.insights)
        return self

# ============================================================================
# AGENT 3: FACT CHECKER
# ============================================================================

class FactCheckIssue(BaseModel):
    """One fact-checking issue found"""
    campus_id: str
    campus_name: str
    issue_type: str  # "percentage_error", "publication_mismatch", "score_error", "invented_data"
    incorrect_statement: str
    correct_information: str
    severity: str  # "critical", "high", "medium", "low"

class CampusFactCheck(BaseModel):
    """Fact-check result for one campus"""
    campus_id: str
    campus_name: str
    is_accurate: bool
    issues_found: List[FactCheckIssue] = Field(default_factory=list)
    verified_claims: int
    total_claims: int

class FactCheckReport(BaseModel):
    """Agent 3 output - fact-checking report"""
    campus_checks: List[CampusFactCheck]
    total_campuses_checked: int = 0
    accurate_campuses: int = 0
    campuses_with_errors: int = 0
    total_issues_found: int = 0
    overall_accuracy_rate: float = 0.0
    summary: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def calculate_stats(self):
        self.total_campuses_checked = len(self.campus_checks)
        self.accurate_campuses = sum(1 for c in self.campus_checks if c.is_accurate)
        self.campuses_with_errors = self.total_campuses_checked - self.accurate_campuses
        self.total_issues_found = sum(len(c.issues_found) for c in self.campus_checks)
        
        if self.total_campuses_checked > 0:
            self.overall_accuracy_rate = (self.accurate_campuses / self.total_campuses_checked) * 100
        
        return self