# tests/conftest.py
import pytest
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch

# Adiciona src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from src.core.models import PersonalityScores, UserAssessment, ProfileInsights, AssessmentItem

@pytest.fixture
def sample_scores():
    """Fixture com scores de exemplo"""
    return PersonalityScores(
        disc={
            'DISC_D': 75.0,
            'DISC_I': 45.0,
            'DISC_S': 30.0,
            'DISC_C': 60.0
        },
        big_five={
            'B5_O': 80.0,
            'B5_C': 85.0,
            'B5_E': 40.0,
            'B5_A': 70.0,
            'B5_N': 25.0
        },
        mbti_preferences={
            'MBTI_E': 30.0,
            'MBTI_I': 70.0,
            'MBTI_S': 20.0,
            'MBTI_N': 80.0,
            'MBTI_T': 75.0,
            'MBTI_F': 25.0,
            'MBTI_J': 85.0,
            'MBTI_P': 15.0
        },
        mbti_type='INTJ',
        confidence_scores={
            'DISC_D': 0.9,
            'DISC_I': 0.8,
            'B5_O': 0.95,
            'B5_C': 0.92
        }
    )

@pytest.fixture
def sample_insights():
    """Fixture com insights de exemplo"""
    return ProfileInsights(
        summary="Perfil INTJ com forte orientação para resultados e inovação.",
        strengths=["Pensamento estratégico", "Independência", "Visão de longo prazo"],
        development_areas=["Comunicação interpessoal", "Flexibilidade", "Trabalho em equipe"],
        career_suggestions=["Arquiteto de Software", "Consultor Estratégico", "Pesquisador"],
        communication_style="Direto e analítico",
        leadership_style="Visionário-Técnico",
        stress_indicators=["Microgerenciamento", "Mudanças constantes"],
        growth_recommendations=["Desenvolver empatia", "Praticar comunicação clara"]
    )

@pytest.fixture
def sample_assessment(sample_scores, sample_insights):
    """Fixture com assessment completo"""
    return UserAssessment(
        user_id="test_user_123",
        assessment_id="assess_20241115_001",
        answers={1: 5, 2: 4, 3: 3, 4: 2, 5: 1},
        scores=sample_scores,
        profile_insights=sample_insights,
        timestamp=datetime(2024, 11, 15, 10, 30, 0),
        completion_time_minutes=18,
        reliability_score=0.87
    )

@pytest.fixture
def sample_items():
    """Fixture com itens de avaliação"""
    return [
        AssessmentItem(
            id=1,
            text="Gosto de assumir liderança em projetos importantes",
            category="DISC",
            weights={"DISC_D": 0.8, "MBTI_J": 0.4}
        ),
        AssessmentItem(
            id=2,
            text="Prefiro trabalhar com ideias abstratas e conceitos",
            category="B5",
            weights={"B5_O": 0.9, "MBTI_N": 0.7}
        ),
        AssessmentItem(
            id=3,
            text="Sou muito organizado em meu trabalho",
            category="B5",
            reverse_scored=False,
            weights={"B5_C": 0.85, "MBTI_J": 0.6}
        )
    ]

@pytest.fixture
def mock_firestore():
    """Mock do Firestore para testes"""
    with patch('src.services.database.firestore.Client') as mock_client:
        mock_db = Mock()
        mock_client.return_value = mock_db
        
        # Mock collection/document chain
        mock_collection = Mock()
        mock_document = Mock()
        mock_subcollection = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        mock_document.collection.return_value = mock_subcollection
        
        yield mock_db

# tests/test_scoring.py
import pytest
import numpy as np
from src.core.scoring import AdvancedScoringEngine, InsightGenerator
from src.core.models import AssessmentItem

class TestAdvancedScoringEngine:
    """Testes para o engine de pontuação"""
    
    def test_calculate_scores_basic(self, sample_items):
        """Testa cálculo básico de scores"""
        engine = AdvancedScoringEngine()
        answers = {1: 5, 2: 4, 3: 3}
        
        scores = engine.calculate_scores_with_confidence(answers, sample_items)
        
        assert scores is not None
        assert scores.mbti_type is not None
        assert len(scores.mbti_type) == 4
        assert all(isinstance(v, float) for v in scores.disc.values())
        assert all(isinstance(v, float) for v in scores.big_five.values())
    
    def test_disc_normalization(self, sample_items):
        """Testa normalização ipsativa do DISC"""
        engine = AdvancedScoringEngine()
        answers = {1: 5, 2: 3, 3: 2}
        
        scores = engine.calculate_scores_with_confidence(answers, sample_items)
        
        # DISC deve somar aproximadamente 100% (normalização ipsativa)
        disc_total = sum(scores.disc.values())
        assert abs(disc_total - 100.0) < 1.0  # Tolerância para arredondamento
    
    def test_confidence_calculation(self, sample_items):
        """Testa cálculo de intervalos de confiança"""
        engine = AdvancedScoringEngine()
        
        # Respostas muito consistentes (baixa confiança)
        consistent_answers = {1: 3, 2: 3, 3: 3}
        scores_consistent = engine.calculate_scores_with_confidence(consistent_answers, sample_items)
        
        # Respostas variadas (alta confiança)
        varied_answers = {1: 1, 2: 3, 3: 5}
        scores_varied = engine.calculate_scores_with_confidence(varied_answers, sample_items)
        
        # Respostas variadas devem ter maior confiança média
        avg_conf_consistent = np.mean(list(scores_consistent.confidence_scores.values()))
        avg_conf_varied = np.mean(list(scores_varied.confidence_scores.values()))
        
        assert avg_conf_varied > avg_conf_consistent
    
    def test_mbti_determination(self, sample_items):
        """Testa determinação do tipo MBTI"""
        engine = AdvancedScoringEngine()
        
        # Cria itens que favorecem INTJ
        intj_items = [
            AssessmentItem(
                id=1,
                text="Test item 1",
                weights={"MBTI_I": 1.0, "MBTI_N": 1.0, "MBTI_T": 1.0, "MBTI_J": 1.0}
            )
        ]
        
        answers = {1: 5}  # Resposta alta
        scores = engine.calculate_scores_with_confidence(answers, intj_items)
        
        # Deve tender para INTJ
        assert 'I' in scores.mbti_type
        assert 'N' in scores.mbti_type
        assert 'T' in scores.mbti_type
        assert 'J' in scores.mbti_type

class TestInsightGenerator:
    """Testes para o gerador de insights"""
    
    def test_generate_insights_basic(self, sample_scores):
        """Testa geração básica de insights"""
        generator = InsightGenerator()
        
        insights = generator.generate_comprehensive_insights(sample_scores)
        
        assert insights is not None
        assert len(insights.summary) > 0
        assert len(insights.strengths) > 0
        assert len(insights.development_areas) >= 0
        assert len(insights.career_suggestions) > 0
    
    def test_disc_dominant_identification(self, sample_scores):
        """Testa identificação do DISC dominante"""
        generator = InsightGenerator()
        
        insights = generator.generate_comprehensive_insights(sample_scores)
        
        # Com DISC_D = 75%, deve identificar Dominância como principal
        assert "D" in insights.summary or "Dominância" in insights.summary
    
    def test_career_suggestions_relevance(self, sample_scores):
        """Testa relevância das sugestões de carreira"""
        generator = InsightGenerator()
        
        insights = generator.generate_comprehensive_insights(sample_scores)
        
        # Para perfil INTJ com alta Dominância, deve sugerir roles de liderança/estratégia
        career_text = " ".join(insights.career_suggestions).lower()
        
        leadership_keywords = ["estratég", "arquitet", "consultor", "líder", "diretor"]
        assert any(keyword in career_text for keyword in leadership_keywords)
    
    def test_stress_indicators_accuracy(self, sample_scores):
        """Testa precisão dos indicadores de estresse"""
        generator = InsightGenerator()
        
        insights = generator.generate_comprehensive_insights(sample_scores)
        
        # Para perfil com baixo Neuroticismo (25%), não deve ter muitos indicadores de estresse
        assert len(insights.stress_indicators) <= 3

# tests/test_models.py
import pytest
from datetime import datetime
from src.core.models import PersonalityScores, UserAssessment, AssessmentItem

class TestPersonalityScores:
    """Testes para o modelo PersonalityScores"""
    
    def test_get_dominant_disc(self, sample_scores):
        """Testa identificação do DISC dominante"""
        dominant, strength = sample_scores.get_dominant_disc()
        
        assert dominant == "D"  # DISC_D tem 75%
        assert strength == 75.0
    
    def test_get_personality_blend(self, sample_scores):
        """Testa identificação da combinação de estilos"""
        blend = sample_scores.get_personality_blend()
        
        assert "D" in blend  # Dominante
        # Se C (60%) for significativo, deve aparecer também
        if sample_scores.disc.get('DISC_C', 0) > 60:
            assert "C" in blend
    
    def test_empty_scores_handling(self):
        """Testa comportamento com scores vazios"""
        empty_scores = PersonalityScores(
            disc={},
            big_five={},
            mbti_preferences={},
            mbti_type="",
            confidence_scores={}
        )
        
        dominant, strength = empty_scores.get_dominant_disc()
        assert dominant == ""
        assert strength == 0.0

class TestUserAssessment:
    """Testes para o modelo UserAssessment"""
    
    def test_calculate_reliability(self, sample_assessment):
        """Testa cálculo de confiabilidade"""
        # Modifica respostas para teste
        sample_assessment.answers = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}  # Boa variabilidade
        
        reliability = sample_assessment.calculate_reliability()
        
        assert 0.0 <= reliability <= 1.0
        assert reliability > 0.5  # Boa variabilidade deve ter alta confiabilidade
    
    def test_reliability_all_same_answers(self, sample_assessment):
        """Testa confiabilidade com todas respostas iguais"""
        sample_assessment.answers = {1: 3, 2: 3, 3: 3, 4: 3, 5: 3}
        
        reliability = sample_assessment.calculate_reliability()
        
        assert reliability <= 0.2  # Baixa confiabilidade para respostas idênticas
    
    def test_reliability_no_answers(self, sample_assessment):
        """Testa comportamento sem respostas"""
        sample_assessment.answers = {}
        
        reliability = sample_assessment.calculate_reliability()
        
        assert reliability == 0.0

class TestAssessmentItem:
    """Testes para o modelo AssessmentItem"""
    
    def test_weight_validation(self):
        """Testa validação de pesos"""
        # Peso válido
        valid_item = AssessmentItem(
            id=1,
            text="Test item",
            weights={"DISC_D": 0.8}
        )
        assert valid_item.weights["DISC_D"] == 0.8
        
        # Peso inválido deve gerar erro
        with pytest.raises(ValueError):
            AssessmentItem(
                id=2,
                text="Test item",
                weights={"DISC_D": 3.0}  # Fora do limite [-2.0, 2.0]
            )

# tests/test_database.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.database import FirestoreManager

class TestFirestoreManager:
    """Testes para o gerenciador Firestore"""
    
    @pytest.mark.asyncio
    async def test_save_assessment(self, mock_firestore, sample_assessment):
        """Testa salvamento de avaliação"""
        manager = FirestoreManager()
        manager.db = mock_firestore
        
        # Mock da transação
        mock_transaction = Mock()
        mock_firestore.transaction.return_value = mock_transaction
        
        # Mock das referências de documento
        mock_doc_ref = Mock()
        mock_doc_ref.id = "test_doc_id"
        
        mock_firestore.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_doc_ref
        
        result = await manager.save_assessment("test_user", sample_assessment)
        
        # Verifica se a transação foi usada
        mock_firestore.transaction.assert_called_once()
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_get_user_assessments(self, mock_firestore):
        """Testa recuperação de avaliações do usuário"""
        manager = FirestoreManager()
        manager.db = mock_firestore
        
        # Mock dos dados retornados
        mock_doc = Mock()
        mock_doc.to_dict.return_value = {
            'user_id': 'test_user',
            'assessment_id': 'test_assessment',
            'answers': {1: 5, 2: 4},
            'scores': {
                'disc': {'DISC_D': 75.0},
                'big_five': {'B5_O': 80.0},
                'mbti_preferences': {'MBTI_E': 30.0},
                'mbti_type': 'INTJ',
                'confidence_scores': {'DISC_D': 0.9}
            },
            'timestamp': datetime(2024, 11, 15),
            'reliability_score': 0.87
        }
        
        mock_query = Mock()
        mock_query.stream.return_value = [mock_doc]
        
        mock_firestore.collection.return_value.document.return_value.collection.return_value.order_by.return_value.limit.return_value = mock_query
        
        assessments = await manager.get_user_assessments("test_user", limit=5)
        
        assert len(assessments) >= 0
        # Verifica se a query foi construída corretamente
        mock_firestore.collection.assert_called()
    
    def test_cache_functionality(self, mock_firestore):
        """Testa funcionalidade de cache"""
        manager = FirestoreManager()
        
        # Testa set e get do cache
        test_key = "test_key"
        test_data = {"test": "data"}
        
        manager._set_cache(test_key, test_data)
        cached_data = manager._get_cache(test_key)
        
        assert cached_data == test_data
        
        # Testa cache inválido (não deve retornar nada)
        invalid_cached = manager._get_cache("nonexistent_key")
        assert invalid_cached is None

# tests/test_visualizations.py
import pytest
import plotly.graph_objects as go
from src.ui.visualizations import PersonalityVisualizer

class TestPersonalityVisualizer:
    """Testes para o visualizador de personalidade"""
    
    def test_create_disc_radar_chart(self, sample_scores):
        """Testa criação do gráfico radar DISC"""
        visualizer = PersonalityVisualizer()
        
        fig = visualizer.create_disc_radar_chart(sample_scores)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0  # Deve ter pelo menos um trace
        
        # Verifica se tem os dados corretos
        trace_data = fig.data[0]
        assert len(trace_data.r) == 5  # 4 dimensões + fechamento do polígono
        assert len(trace_data.theta) == 5
    
    def test_create_big_five_bars(self, sample_scores):
        """Testa criação do gráfico de barras Big Five"""
        visualizer = PersonalityVisualizer()
        
        fig = visualizer.create_big_five_bars(sample_scores)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        
        # Verifica se tem 5 barras (uma para cada traço)
        trace_data = fig.data[0]
        assert len(trace_data.x) == 5
        assert len(trace_data.y) == 5
    
    def test_create_mbti_preference_chart(self, sample_scores):
        """Testa criação do gráfico de preferências MBTI"""
        visualizer = PersonalityVisualizer()
        
        fig = visualizer.create_mbti_preference_chart(sample_scores)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        
        # Verifica se tem 4 barras (uma para cada dimensão MBTI)
        trace_data = fig.data[0]
        assert len(trace_data.y) == 4  # 4 dimensões MBTI
    
    def test_confidence_indicators(self, sample_scores):
        """Testa criação dos indicadores de confiança"""
        visualizer = PersonalityVisualizer()
        
        fig = visualizer.create_confidence_indicators(sample_scores)
        
        if fig:  # Só testa se há confidence_scores
            assert isinstance(fig, go.Figure)
            assert len(fig.data) > 0

# tests/test_reports.py
import pytest
from src.utils.reports import AdvancedReportGenerator

class TestAdvancedReportGenerator:
    """Testes para o gerador de relatórios"""
    
    def test_generate_pdf_report(self, sample_assessment):
        """Testa geração de relatório PDF"""
        generator = AdvancedReportGenerator()
        
        pdf_data = generator.generate_comprehensive_report(
            sample_assessment,
            report_type="executive",
            format="pdf"
        )
        
        assert isinstance(pdf_data, bytes)
        assert len(pdf_data) > 0
        # Verifica se é um PDF válido (começa com %PDF)
        assert pdf_data.startswith(b'%PDF')
    
    def test_generate_html_report(self, sample_assessment):
        """Testa geração de relatório HTML"""
        generator = AdvancedReportGenerator()
        
        html_data = generator.generate_comprehensive_report(
            sample_assessment,
            report_type="complete",
            format="html"
        )
        
        assert isinstance(html_data, bytes)
        html_content = html_data.decode('utf-8')
        assert '<html>' in html_content
        assert 'NeuroMap' in html_content
        assert sample_assessment.scores.mbti_type in html_content
    
    def test_generate_excel_report(self, sample_assessment):
        """Testa geração de relatório Excel"""
        generator = AdvancedReportGenerator()
        
        excel_data = generator.generate_comprehensive_report(
            sample_assessment,
            report_type="coaching",
            format="excel"
        )
        
        assert isinstance(excel_data, bytes)
        assert len(excel_data) > 0
    
    def test_mbti_type_description(self, sample_assessment):
        """Testa descrições dos tipos MBTI"""
        generator = AdvancedReportGenerator()
        
        description = generator._get_mbti_type_description("INTJ")
        
        assert isinstance(description, str)
        assert len(description) > 0
        assert "Arquiteto" in description or "INTJ" in description

# tests/test_integration.py
import pytest
from src.core.scoring import AdvancedScoringEngine, InsightGenerator
from src.utils.reports import AdvancedReportGenerator

class TestIntegration:
    """Testes de integração entre componentes"""
    
    def test_complete_assessment_flow(self, sample_items):
        """Testa fluxo completo de avaliação"""
        # 1. Scoring
        engine = AdvancedScoringEngine()
        answers = {1: 5, 2: 4, 3: 3}
        
        scores = engine.calculate_scores_with_confidence(answers, sample_items)
        assert scores is not None
        
        # 2. Insights
        insight_generator = InsightGenerator()
        insights = insight_generator.generate_comprehensive_insights(scores)
        assert insights is not None
        
        # 3. Relatório
        from src.core.models import UserAssessment
        assessment = UserAssessment(
            user_id="integration_test",
            assessment_id="test_001",
            answers=answers,
            scores=scores,
            profile_insights=insights,
            timestamp=datetime.now(),
            reliability_score=0.8
        )
        
        report_generator = AdvancedReportGenerator()
        pdf_report = report_generator.generate_comprehensive_report(
            assessment, "executive", "pdf"
        )
        
        assert isinstance(pdf_report, bytes)
        assert len(pdf_report) > 0
    
    def test_data_consistency(self, sample_items):
        """Testa consistência de dados entre componentes"""
        engine = AdvancedScoringEngine()
        answers = {1: 5, 2: 4, 3: 3}
        
        scores = engine.calculate_scores_with_confidence(answers, sample_items)
        
        # Verifica consistência DISC (deve somar ~100%)
        disc_total = sum(scores.disc.values())
        assert abs(disc_total - 100.0) < 5.0
        
        # Verifica consistência MBTI (tipo deve ter 4 caracteres)
        assert len(scores.mbti_type) == 4
        assert all(c in 'EISTFJPN' for c in scores.mbti_type)
        
        # Verifica Big Five (deve estar entre 0-100)
        for value in scores.big_five.values():
            assert 0 <= value <= 100
