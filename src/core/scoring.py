import numpy as np
from typing import Dict, List, Tuple
from .models import AssessmentItem, PersonalityScores, ProfileInsights
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class AdvancedScoringEngine:
    """Engine de pontuação com algoritmos estatísticos avançados"""
    
    def __init__(self):
        self.item_reliability_cache = {}
        self.norm_data = self._load_normative_data()
    
    def _load_normative_data(self) -> Dict:
        """Carrega dados normativos para comparação (mock)"""
        return {
            "disc_means": {"D": 50, "I": 50, "S": 50, "C": 50},
            "disc_stds": {"D": 15, "I": 15, "S": 15, "C": 15},
            "b5_means": {"O": 50, "C": 50, "E": 50, "A": 50, "N": 50},
            "b5_stds": {"O": 15, "C": 15, "E": 15, "A": 15, "N": 15}
        }
    
    def calculate_scores_with_confidence(
        self, 
        answers: Dict[int, int], 
        items: List[AssessmentItem]
    ) -> PersonalityScores:
        """Calcula scores com intervalos de confiança"""
        
        raw_scores = self._calculate_raw_scores(answers, items)
        normalized_scores = self._normalize_scores(raw_scores)
        confidence_scores = self._calculate_confidence_intervals(answers, items)
        mbti_type = self._determine_mbti_type(normalized_scores.get("mbti", {}))
        
        return PersonalityScores(
            disc=normalized_scores.get("disc", {}),
            big_five=normalized_scores.get("b5", {}),
            mbti_preferences=normalized_scores.get("mbti", {}),
            mbti_type=mbti_type,
            confidence_scores=confidence_scores
        )
    
    def _calculate_raw_scores(
        self, 
        answers: Dict[int, int], 
        items: List[AssessmentItem]
    ) -> Dict[str, Dict[str, float]]:
        """Calcula scores brutos com pesos adaptativos"""
        
        scores = {
            "disc": {"D": 0, "I": 0, "S": 0, "C": 0},
            "b5": {"O": 0, "C": 0, "E": 0, "A": 0, "N": 0},
            "mbti": {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
        }
        
        for item in items:
            if item.id not in answers:
                continue
                
            response = answers[item.id]
            
            # Aplica reverse scoring se necessário
            if item.reverse_scored:
                response = 6 - response
            
            # Aplica pesos com adaptação baseada na confiabilidade do item
            reliability_factor = self._get_item_reliability(item.id)
            
            for dimension, weight in item.weights.items():
                adjusted_weight = weight * reliability_factor
                
                if dimension.startswith("DISC_"):
                    key = dimension.replace("DISC_", "")
                    scores["disc"][key] += response * adjusted_weight
                elif dimension.startswith("B5_"):
                    key = dimension.replace("B5_", "")
                    scores["b5"][key] += response * adjusted_weight
                elif dimension.startswith("MBTI_"):
                    key = dimension.replace("MBTI_", "")
                    scores["mbti"][key] += response * adjusted_weight
        
        return scores
    
    def _normalize_scores(self, raw_scores: Dict) -> Dict[str, Dict[str, float]]:
        """Normaliza scores usando dados normativos"""
        normalized = {}
        
        for scale, dimensions in raw_scores.items():
            normalized[scale] = {}
            
            if scale == "disc":
                # Normalização ipsativa (soma = 100)
                total = sum(abs(score) for score in dimensions.values())
                if total > 0:
                    for dim, score in dimensions.items():
                        normalized[scale][f"DISC_{dim}"] = round((abs(score) / total) * 100, 1)
                
            elif scale == "b5":
                # Normalização baseada em normas populacionais
                for dim, score in dimensions.items():
                    mean = self.norm_data["b5_means"][dim]
                    std = self.norm_data["b5_stds"][dim]
                    z_score = (score - mean) / std if std > 0 else 0
                    percentile = stats.norm.cdf(z_score) * 100
                    normalized[scale][f"B5_{dim}"] = round(max(0, min(100, percentile)), 1)
            
            elif scale == "mbti":
                # Mantém scores brutos para MBTI (serão usados para determinar preferências)
                normalized[scale] = {f"MBTI_{k}": v for k, v in dimensions.items()}
        
        return normalized
    
    def _calculate_confidence_intervals(
        self, 
        answers: Dict[int, int], 
        items: List[AssessmentItem]
    ) -> Dict[str, float]:
        """Calcula intervalos de confiança para cada dimensão"""
        
        # Análise da consistência das respostas por dimensão
        dimension_responses = {}
        
        for item in items:
            if item.id not in answers:
                continue
                
            response = answers[item.id]
            
            for dimension in item.weights.keys():
                if dimension not in dimension_responses:
                    dimension_responses[dimension] = []
                dimension_responses[dimension].append(response)
        
        confidence_scores = {}
        for dimension, responses in dimension_responses.items():
            if len(responses) < 2:
                confidence_scores[dimension] = 0.5
            else:
                # Calcula consistência interna (Alpha de Cronbach simplificado)
                variance = np.var(responses)
                mean_response = np.mean(responses)
                
                # Score de confiança baseado na variabilidade esperada
                if variance == 0:
                    confidence_scores[dimension] = 0.3  # Muito consistente = suspeito
                else:
                    expected_var = 1.0  # Variância esperada para respostas autênticas
                    confidence = min(1.0, expected_var / (variance + 0.1))
                    confidence_scores[dimension] = round(confidence, 2)
        
        return confidence_scores
    
    def _determine_mbti_type(self, mbti_scores: Dict[str, float]) -> str:
        """Determina tipo MBTI com base nos scores"""
        
        preferences = []
        
        # E vs I
        e_score = mbti_scores.get("MBTI_E", 0)
        i_score = mbti_scores.get("MBTI_I", 0)
        preferences.append("E" if e_score >= i_score else "I")
        
        # S vs N
        s_score = mbti_scores.get("MBTI_S", 0)
        n_score = mbti_scores.get("MBTI_N", 0)
        preferences.append("S" if s_score >= n_score else "N")
        
        # T vs F
        t_score = mbti_scores.get("MBTI_T", 0)
        f_score = mbti_scores.get("MBTI_F", 0)
        preferences.append("T" if t_score >= f_score else "F")
        
        # J vs P
        j_score = mbti_scores.get("MBTI_J", 0)
        p_score = mbti_scores.get("MBTI_P", 0)
        preferences.append("J" if j_score >= p_score else "P")
        
        return "".join(preferences)
    
    def _get_item_reliability(self, item_id: int) -> float:
        """Retorna fator de confiabilidade do item (mock - seria baseado em dados históricos)"""
        if item_id in self.item_reliability_cache:
            return self.item_reliability_cache[item_id]
        
        # Mock: itens com IDs menores são mais confiáveis
        reliability = max(0.7, 1.0 - (item_id * 0.005))
        self.item_reliability_cache[item_id] = reliability
        return reliability

class InsightGenerator:
    """Gerador de insights personalizados usando IA"""
    
    def __init__(self):
        self.personality_templates = self._load_insight_templates()
    
    def generate_comprehensive_insights(
        self, 
        scores: PersonalityScores,
        user_context: Dict = None
    ) -> ProfileInsights:
        """Gera insights abrangentes do perfil"""
        
        dominant_disc, disc_strength = scores.get_dominant_disc()
        personality_blend = scores.get_personality_blend()
        
        # Gera insights contextualizados
        summary = self._generate_summary(scores, personality_blend)
        strengths = self._identify_strengths(scores, dominant_disc)
        development_areas = self._identify_development_areas(scores)
        career_suggestions = self._generate_career_suggestions(scores, user_context)
        
        return ProfileInsights(
            summary=summary,
            strengths=strengths,
            development_areas=development_areas,
            career_suggestions=career_suggestions,
            communication_style=self._determine_communication_style(scores),
            leadership_style=self._determine_leadership_style(scores),
            stress_indicators=self._identify_stress_indicators(scores),
            growth_recommendations=self._generate_growth_recommendations(scores)
        )
    
    def _generate_summary(self, scores: PersonalityScores, blend: List[str]) -> str:
        """Gera resumo personalizado do perfil"""
        
        dominant_disc = blend[0] if blend else "Equilibrado"
        mbti_type = scores.mbti_type
        
        # Template baseado no tipo dominante
        templates = {
            "D": f"Perfil {mbti_type} com orientação para resultados e liderança direta. "
                 f"Combina assertividade ({scores.disc.get('DISC_D', 0):.0f}%) com foco em eficiência.",
            
            "I": f"Perfil {mbti_type} com forte habilidade de comunicação e influência. "
                 f"Destaca-se pela capacidade de inspirar e engajar pessoas ({scores.disc.get('DISC_I', 0):.0f}%).",
            
            "S": f"Perfil {mbti_type} caracterizado pela estabilidade e cooperação. "
                 f"Valoriza harmonia e consistência ({scores.disc.get('DISC_S', 0):.0f}%).",
            
            "C": f"Perfil {mbti_type} com foco em qualidade e precisão. "
                 f"Prioriza análise detalhada e padrões elevados ({scores.disc.get('DISC_C', 0):.0f}%)."
        }
        
        base_summary = templates.get(dominant_disc, f"Perfil {mbti_type} equilibrado entre diferentes dimensões.")
        
        # Adiciona insights do Big Five
        high_traits = [trait.replace("B5_", "") for trait, score in scores.big_five.items() if score > 70]
        if high_traits:
            trait_names = {"O": "Abertura", "C": "Conscienciosidade", "E": "Extroversão", 
                          "A": "Amabilidade", "N": "Neuroticismo"}
            high_trait_names = [trait_names.get(t, t) for t in high_traits]
            base_summary += f" Destaca-se especialmente em: {', '.join(high_trait_names)}."
        
        return base_summary
    
    def _identify_strengths(self, scores: PersonalityScores, dominant_disc: str) -> List[str]:
        """Identifica pontos fortes baseados no perfil"""
        strengths = []
        
        # Strengths baseados em DISC
        disc_strengths = {
            "D": ["Liderança natural", "Tomada de decisão rápida", "Orientação para resultados", 
                  "Capacidade de assumir riscos calculados"],
            "I": ["Comunicação persuasiva", "Networking efetivo", "Motivação de equipes", 
                  "Adaptabilidade social"],
            "S": ["Estabilidade emocional", "Trabalho em equipe", "Confiabilidade", 
                  "Paciência em processos longos"],
            "C": ["Atenção aos detalhes", "Qualidade técnica", "Análise sistemática", 
                  "Conformidade com padrões"]
        }
        
        strengths.extend(disc_strengths.get(dominant_disc, []))
        
        # Strengths baseados em Big Five (scores > 65)
        b5_strengths = {
            "B5_O": "Criatividade e inovação",
            "B5_C": "Disciplina e organização",
            "B5_E": "Energia e sociabilidade",
            "B5_A": "Empatia e cooperação",
        }
        
        for trait, score in scores.big_five.items():
            if score > 65 and trait in b5_strengths:
                strengths.append(b5_strengths[trait])
        
        # Remove duplicatas e limita a 6 strengths principais
        return list(dict.fromkeys(strengths))[:6]
    
    def _identify_development_areas(self, scores: PersonalityScores) -> List[str]:
        """Identifica áreas de desenvolvimento"""
        development_areas = []
        
        # Áreas baseadas em scores baixos do Big Five
        low_score_areas = {
            "B5_O": "Abertura para novas experiências",
            "B5_C": "Organização e disciplina",
            "B5_E": "Assertividade social",
            "B5_A": "Colaboração interpessoal"
        }
        
        for trait, score in scores.big_five.items():
            if score < 35 and trait in low_score_areas:
                development_areas.append(low_score_areas[trait])
        
        # Áreas baseadas em alto neuroticismo
        if scores.big_five.get("B5_N", 0) > 65:
            development_areas.extend([
                "Gestão do estresse",
                "Regulação emocional",
                "Resiliência em adversidades"
            ])
        
        # Balanceamento DISC
        disc_scores = list(scores.disc.values())
        if max(disc_scores) - min(disc_scores) > 40:
            development_areas.append("Flexibilidade comportamental")
        
        return development_areas[:5]
    
    def _generate_career_suggestions(self, scores: PersonalityScores, context: Dict = None) -> List[str]:
        """Gera sugestões de carreira baseadas no perfil"""
        
        dominant_disc, _ = scores.get_dominant_disc()
        mbti = scores.mbti_type
        
        # Sugestões baseadas em combinações DISC + MBTI
        career_matrix = {
            ("D", "NT"): ["Executivo C-Level", "Consultor Estratégico", "Empreendedor Tech"],
            ("D", "ST"): ["Gerente de Operações", "Diretor Financeiro", "Consultor Empresarial"],
            ("I", "NF"): ["Coach Executivo", "Diretor de RH", "Consultor Organizacional"],
            ("I", "SF"): ["Gerente de Vendas", "Relações Públicas", "Treinamento Corporativo"],
            ("S", "SF"): ["Gerente de Pessoas", "Psicólogo Organizacional", "Facilitador"],
            ("S", "ST"): ["Analista de Processos", "Gerente de Qualidade", "Auditor"],
            ("C", "NT"): ["Analista Sênior", "Arquiteto de Sistemas", "Pesquisador"],
            ("C", "ST"): ["Controller", "Analista Financeiro", "Especialista Técnico"]
        }
        
        # Determina temperamento MBTI (NT, NF, ST, SF)
        temperament = mbti[1] + mbti[2]  # Segunda e terceira letras
        
        key = (dominant_disc, temperament)
        suggestions = career_matrix.get(key, ["Líder de Projetos", "Analista de Negócios", "Consultor"])
        
        return suggestions
    
    def _determine_communication_style(self, scores: PersonalityScores) -> str:
        """Determina estilo de comunicação predominante"""
        
        dominant_disc, strength = scores.get_dominant_disc()
        extroversion = scores.big_five.get("B5_E", 50)
        
        styles = {
            "D": "Direto e orientado para resultados" if extroversion > 50 else "Assertivo e conciso",
            "I": "Expressivo e persuasivo" if extroversion > 60 else "Caloroso e influente",
            "S": "Colaborativo e empático" if extroversion > 40 else "Paciente e receptivo",
            "C": "Analítico e preciso" if extroversion > 45 else "Detalhista e sistemático"
        }
        
        return styles.get(dominant_disc, "Equilibrado e adaptável")
    
    def _determine_leadership_style(self, scores: PersonalityScores) -> str:
        """Determina estilo de liderança"""
        
        dominant_disc, _ = scores.get_dominant_disc()
        conscientiousness = scores.big_five.get("B5_C", 50)
        
        if dominant_disc == "D":
            return "Autoritário-Transformacional" if conscientiousness > 60 else "Diretivo-Pragmático"
        elif dominant_disc == "I":
            return "Inspiracional-Carismático" if conscientiousness > 55 else "Motivacional-Flexível"
        elif dominant_disc == "S":
            return "Participativo-Democrático" if conscientiousness > 50 else "Servidor-Facilitador"
        elif dominant_disc == "C":
            return "Técnico-Especialista" if conscientiousness > 65 else "Analítico-Consultivo"
        
        return "Situacional-Adaptativo"
    
    def _identify_stress_indicators(self, scores: PersonalityScores) -> List[str]:
        """Identifica indicadores de estresse baseados no perfil"""
        
        indicators = []
        
        # Baseado em alto neuroticismo
        if scores.big_five.get("B5_N", 0) > 65:
            indicators.extend([
                "Ansiedade em situações de incerteza",
                "Autocrítica excessiva",
                "Dificuldade em lidar com críticas"
            ])
        
        # Baseado em perfil DISC
        dominant_disc, strength = scores.get_dominant_disc()
        
        stress_patterns = {
            "D": ["Impaciência com lentidão", "Frustração com microgerenciamento"],
            "I": ["Isolamento social", "Ambientes muito estruturados"],
            "S": ["Mudanças repentinas", "Conflitos interpessoais"],
            "C": ["Pressão por decisões rápidas", "Ambiguidade nas expectativas"]
        }
        
        indicators.extend(stress_patterns.get(dominant_disc, []))
        
        return indicators[:4]
    
    def _generate_growth_recommendations(self, scores: PersonalityScores) -> List[str]:
        """Gera recomendações específicas de crescimento"""
        
        recommendations = []
        dominant_disc, _ = scores.get_dominant_disc()
        
        # Recomendações baseadas no perfil dominante
        disc_reco = {
            "D": [
                "Pratique escuta ativa em reuniões",
                "Desenvolva paciência com processos colaborativos",
                "Invista em feedback 360° regular"
            ],
            "I": [
                "Estruture melhor suas apresentações",
                "Desenvolva habilidades de follow-up",
                "Pratique análise de dados para suportar argumentos"
            ],
            "S": [
                "Pratique assertividade em situações de conflito",
                "Desenvolva comfort zone com mudanças",
                "Assuma projetos com maior visibilidade"
            ],
            "C": [
                "Pratique comunicação mais sintética",
                "Desenvolva tolerância à ambiguidade",
                "Participe de atividades de team building"
            ]
        }
        
        recommendations.extend(disc_reco.get(dominant_disc, []))
        
        # Recomendações baseadas em Big Five
        if scores.big_five.get("B5_O", 0) < 40:
            recommendations.append("Explore novas abordagens e metodologias")
        
        if scores.big_five.get("B5_E", 0) < 35:
            recommendations.append("Participe de eventos de networking estruturados")
        
        return recommendations[:5]
    
    def _load_insight_templates(self) -> Dict:
        """Carrega templates para geração de insights (mock)"""
        return {
            "career_paths": {},
            "development_plans": {},
            "communication_guides": {}
        }
