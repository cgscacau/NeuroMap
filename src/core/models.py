from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field, validator
import numpy as np

class AssessmentItem(BaseModel):
    """Item individual do questionário com validações"""
    id: int
    text: str
    category: str = Field(..., description="DISC, B5, ou MBTI")
    reverse_scored: bool = False
    weights: Dict[str, float] = Field(default_factory=dict)
    
    @validator('weights')
    def validate_weights(cls, v):
        """Valida se os pesos estão dentro de limites aceitáveis"""
        for key, weight in v.items():
            if not -2.0 <= weight <= 2.0:
                raise ValueError(f"Peso {weight} para {key} fora do limite [-2.0, 2.0]")
        return v

@dataclass
class PersonalityScores:
    """Scores organizados com métodos de análise"""
    disc: Dict[str, float]
    big_five: Dict[str, float]
    mbti_preferences: Dict[str, float]
    mbti_type: str
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    
    def get_dominant_disc(self) -> Tuple[str, float]:
        """Retorna o fator DISC dominante"""
        if not self.disc:
            return ("", 0.0)
        dominant = max(self.disc.items(), key=lambda x: x[1])
        return dominant[0].replace("DISC_", ""), dominant[1]
    
    def get_personality_blend(self) -> List[str]:
        """Identifica combinação de tipos (ex: DC, SI)"""
        sorted_disc = sorted(self.disc.items(), key=lambda x: x[1], reverse=True)
        top_two = [item[0].replace("DISC_", "") for item in sorted_disc[:2]]
        if sorted_disc[1][1] > 60:  # Segunda dimensão significativa
            return top_two
        return [top_two[0]]

@dataclass
class UserAssessment:
    """Avaliação completa do usuário"""
    user_id: str
    assessment_id: str
    answers: Dict[int, int]
    scores: PersonalityScores
    profile_insights: Dict
    timestamp: datetime
    completion_time_minutes: Optional[int] = None
    reliability_score: Optional[float] = None
    
    def calculate_reliability(self) -> float:
        """Calcula score de confiabilidade baseado em padrões de resposta"""
        if not self.answers:
            return 0.0
        
        responses = list(self.answers.values())
        
        # Verifica variabilidade nas respostas
        variance = np.var(responses)
        if variance < 0.5:  # Muito pouco variável
            return 0.3
        
        # Verifica padrões suspeitos (todas respostas iguais, alternância sistemática)
        unique_responses = len(set(responses))
        if unique_responses == 1:  # Todas iguais
            return 0.1
        
        # Score baseado na distribuição das respostas
        expected_variance = 1.5  # Variância esperada para respostas autênticas
        reliability = min(1.0, variance / expected_variance)
        
        return round(reliability, 2)

class ProfileInsights(BaseModel):
    """Insights estruturados do perfil"""
    summary: str
    strengths: List[str]
    development_areas: List[str]
    career_suggestions: List[str]
    communication_style: str
    leadership_style: str
    stress_indicators: List[str]
    growth_recommendations: List[str]
    compatibility_notes: Dict[str, str] = Field(default_factory=dict)
