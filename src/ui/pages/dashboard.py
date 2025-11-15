import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from ...core.models import UserAssessment, PersonalityScores
from ...services.database import db_manager
from ...ui.visualizations import PersonalityVisualizer, DashboardComponents
from ...ui.components import MetricsCards, TimelineChart, ComparisonChart

class DashboardPage:
    """Dashboard principal com analytics e insights"""
    
    def __init__(self):
        self.visualizer = PersonalityVisualizer()
        self.components = DashboardComponents()
    
    def render(self) -> None:
        """Renderiza dashboard principal"""
        
        if not st.session_state.get('user_id'):
            self._render_guest_dashboard()
            return
        
        # Carrega dados do usuário
        user_data = self._load_user_data()
        
        if not user_data['assessments']:
            self._render_empty_dashboard()
            return
        
        # Header do dashboard
        self._render_dashboard_header(user_data)
        
        # Conteúdo principal em tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🏠 Visão Geral",
            "📊 Análise Detalhada", 
            "📈 Evolução Temporal",
            "🎯 Benchmarks",
            "🤖 Insights IA"
        ])
        
        with tab1:
            self._render_overview_tab(user_data)
        
        with tab2:
            self._render_detailed_analysis_tab(user_data)
        
        with tab3:
            self._render_evolution_tab(user_data)
        
        with tab4:
            self._render_benchmarks_tab(user_data)
        
        with tab5:
            self._render_ai_insights_tab(user_data)
    
    def _load_user_data(self) -> Dict:
        """Carrega todos os dados necessários do usuário"""
        
        user_id = st.session_state.user_id
        
        # Cache para evitar recarregamentos desnecessários
        cache_key = f"dashboard_data_{user_id}"
        
        if cache_key in st.session_state:
            cache_time = st.session_state.get(f"{cache_key}_time", datetime.min)
            if (datetime.now() - cache_time).seconds < 300:  # Cache por 5 minutos
                return st.session_state[cache_key]
        
        with st.spinner("📊 Carregando seus dados..."):
            try:
                # Carrega avaliações
                assessments = []  # await db_manager.get_user_assessments(user_id, limit=20)
                
                # Carrega analytics
                analytics = {}  # await db_manager.get_assessment_analytics(user_id)
                
                # Carrega benchmarks populacionais
                benchmarks = {}  # await db_manager.get_population_benchmarks()
                
                # Mock data para demonstração
                assessments = self._generate_mock_assessments()
                analytics = self._generate_mock_analytics()
                benchmarks = self._generate_mock_benchmarks()
                
                user_data = {
                    'assessments': assessments,
                    'analytics': analytics,
                    'benchmarks': benchmarks,
                    'latest_assessment': assessments[0] if assessments else None
                }
                
                # Atualiza cache
                st.session_state[cache_key] = user_data
                st.session_state[f"{cache_key}_time"] = datetime.now()
                
                return user_data
                
            except Exception as e:
                st.error(f"Erro ao carregar dados: {e}")
                return {'assessments': [], 'analytics': {}, 'benchmarks': {}, 'latest_assessment': None}
    
    def _render_dashboard_header(self, user_data: Dict) -> None:
        """Renderiza header do dashboard com métricas principais"""
        
        latest = user_data['latest_assessment']
        analytics = user_data['analytics']
        
        st.markdown(f"""
        <div style='background: linear-gradient(90deg, #0b0f17 0%, #1a1f3a 100%); 
                    padding: 2rem; border-radius: 12px; margin-bottom: 2rem;'>
            <h1 style='color: #8ab4f8; margin-bottom: 0.5rem;'>
                🧠 Seu Dashboard NeuroMap
            </h1>
            <p style='color: #a8c7fa; margin-bottom: 1rem;'>
                Acompanhe sua jornada de autoconhecimento e desenvolvimento
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Métricas principais
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_assessments = analytics.get('total_assessments', 0)
            st.metric(
                "📋 Avaliações",
                total_assessments,
                delta=f"+1" if total_assessments > 0 else None
            )
        
        with col2:
            if latest:
                mbti_type = latest.scores.mbti_type
                st.metric("🎭 Tipo Atual", mbti_type)
            else:
                st.metric("🎭 Tipo Atual", "N/A")
        
        with col3:
            frequency = analytics.get('assessment_frequency', 'N/A')
            st.metric("📅 Frequência", frequency)
        
        with col4:
            if latest:
                reliability = latest.reliability_score or 0.85
                st.metric(
                    "🎯 Confiabilidade",
                    f"{reliability:.0%}",
                    delta=f"+{(reliability-0.8)*100:.0f}%" if reliability > 0.8 else None
                )
            else:
                st.metric("🎯 Confiabilidade", "N/A")
        
        with col5:
            streak = analytics.get('assessment_streak', 1)
            st.metric(
                "🔥 Sequência",
                f"{streak} dias",
                delta="+1" if streak > 1 else None
            )
    
    def _render_overview_tab(self, user_data: Dict) -> None:
        """Renderiza tab de visão geral"""
        
        latest = user_data['latest_assessment']
        
        if not latest:
            st.info("📝 Faça sua primeira avaliação para ver os resultados aqui!")
            return
        
        # Resumo da personalidade
        st.markdown("### 🎯 Resumo da Sua Personalidade")
        self.components.personality_summary_card(latest.scores)
        
        st.divider()
        
        # Visualizações principais
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Perfil DISC")
            disc_chart = self.visualizer.create_disc_radar_chart(latest.scores)
            st.plotly_chart(disc_chart, use_container_width=True)
        
        with col2:
            st.markdown("#### 🧠 Big Five")
            b5_chart = self.visualizer.create_big_five_bars(latest.scores)
            st.plotly_chart(b5_chart, use_container_width=True)
        
        # MBTI e Composição
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎭 Preferências MBTI")
            mbti_chart = self.visualizer.create_mbti_preference_chart(latest.scores)
            st.plotly_chart(mbti_chart, use_container_width=True)
        
        with col2:
            st.markdown("#### 🌟 Composição da Personalidade")
            sunburst_chart = self.visualizer.create_personality_blend_sunburst(latest.scores)
            st.plotly_chart(sunburst_chart, use_container_width=True)
        
        # Insights rápidos
        if latest.profile_insights:
            col1, col2 = st.columns(2)
            
            with col1:
                self.components.strengths_insights_card(latest.profile_insights)
            
            with col2:
                self.components.development_recommendations_card(latest.profile_insights)
    
    def _render_detailed_analysis_tab(self, user_data: Dict) -> None:
        """Renderiza análise detalhada"""
        
        latest = user_data['latest_assessment']
        
        if not latest:
            st.info("Dados insuficientes para análise detalhada")
            return
        
        # Seletor de dimensões para análise
        st.markdown("### 🔍 Análise Detalhada por Dimensão")
        
        analysis_type = st.selectbox(
            "Escolha o tipo de análise:",
            ["DISC Completo", "Big Five Detalhado", "MBTI Preferências", "Análise de Confiabilidade"]
        )
        
        if analysis_type == "DISC Completo":
            self._render_disc_detailed_analysis(latest.scores)
        
        elif analysis_type == "Big Five Detalhado":
            self._render_big_five_detailed_analysis(latest.scores)
        
        elif analysis_type == "MBTI Preferências":
            self._render_mbti_detailed_analysis(latest.scores)
        
        elif analysis_type == "Análise de Confiabilidade":
            self._render_reliability_analysis(latest)
    
    def _render_disc_detailed_analysis(self, scores: PersonalityScores) -> None:
        """Análise detalhada do DISC"""
        
        st.markdown("#### 🎯 Análise DISC Detalhada")
        
        # Scores detalhados
        disc_data = []
        for key, value in scores.disc.items():
            dimension = key.replace('DISC_', '')
            disc_data.append({
                'Dimensão': dimension,
                'Score': value,
                'Nível': self._get_disc_level(value),
                'Descrição': self._get_disc_description(dimension, value)
            })
        
        df = pd.DataFrame(disc_data)
        st.dataframe(df, use_container_width=True)
        
        # Combinações especiais
        dominant_disc, strength = scores.get_dominant_disc()
        blend = scores.get_personality_blend()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🏆 Estilo Dominante")
            st.info(f"""
            **{dominant_disc}** ({strength:.1f}%)
            
            {self._get_disc_detailed_description(dominant_disc)}
            """)
        
        with col2:
            st.markdown("##### 🔀 Combinação de Estilos")
            if len(blend) > 1:
                st.success(f"""
                **Estilo Híbrido: {'/'.join(blend)}**
                
                Você apresenta características equilibradas entre diferentes estilos,
                o que indica flexibilidade comportamental.
                """)
            else:
                st.warning(f"""
                **Estilo Puro: {blend[0]}**
                
                Perfil bem definido em uma dimensão. Considere desenvolver
                flexibilidade em outros estilos para situações específicas.
                """)
        
        # Recomendações específicas
        st.markdown("##### 💡 Recomendações Específicas")
        recommendations = self._get_disc_recommendations(scores.disc)
        
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"**{i}.** {rec}")
    
    def _render_big_five_detailed_analysis(self, scores: PersonalityScores) -> None:
        """Análise detalhada do Big Five"""
        
        st.markdown("#### 🧠 Análise Big Five Detalhada")
        
        # Tabela com interpretações
        b5_data = []
        trait_names = {
            'B5_O': 'Abertura à Experiência',
            'B5_C': 'Conscienciosidade',
            'B5_E': 'Extroversão',
            'B5_A': 'Amabilidade',
            'B5_N': 'Neuroticismo'
        }
        
        for key, value in scores.big_five.items():
            trait_name = trait_names.get(key, key)
            b5_data.append({
                'Traço': trait_name,
                'Percentil': f"{value:.0f}%",
                'Nível': self._get_b5_level(value),
                'Interpretação': self._get_b5_interpretation(key, value)
            })
        
        df = pd.DataFrame(b5_data)
        st.dataframe(df, use_container_width=True)
        
        # Análise de padrões
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📈 Pontos Altos (>70%)")
            high_traits = [(k, v) for k, v in scores.big_five.items() if v > 70]
            
            if high_traits:
                for trait, score in high_traits:
                    trait_name = trait_names.get(trait, trait)
                    st.success(f"**{trait_name}**: {score:.0f}% - {self._get_b5_strength(trait)}")
            else:
                st.info("Nenhum traço com score muito alto (perfil equilibrado)")
        
        with col2:
            st.markdown("##### 📉 Áreas de Atenção (<30%)")
            low_traits = [(k, v) for k, v in scores.big_five.items() if v < 30]
            
            if low_traits:
                for trait, score in low_traits:
                    trait_name = trait_names.get(trait, trait)
                    st.warning(f"**{trait_name}**: {score:.0f}% - {self._get_b5_development_area(trait)}")
            else:
                st.info("Nenhum traço com score muito baixo")
        
        # Perfil de personalidade único
        st.markdown("##### 🎨 Seu Perfil Único")
        personality_signature = self._generate_personality_signature(scores.big_five)
        st.info(personality_signature)
    
    def _render_evolution_tab(self, user_data: Dict) -> None:
        """Renderiza evolução temporal"""
        
        assessments = user_data['assessments']
        
        if len(assessments) < 2:
            st.info("""
            📈 **Evolução Temporal**
            
            Faça mais avaliações ao longo do tempo para ver sua evolução pessoal.
            Recomendamos uma avaliação a cada 3-6 meses para acompanhar mudanças significativas.
            """)
            return
        
        st.markdown("### 📈 Sua Jornada de Desenvolvimento")
        
        # Timeline de evolução
        evolution_chart = self.visualizer.create_evolution_timeline(assessments)
        if evolution_chart:
            st.plotly_chart(evolution_chart, use_container_width=True)
        
        # Análise de mudanças
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Mudanças Significativas")
            changes = self._analyze_personality_changes(assessments)
            
            for change in changes:
                if change['magnitude'] > 10:
                    icon = "📈" if change['direction'] == 'increase' else "📉"
                    st.write(f"{icon} **{change['dimension']}**: {change['change']:+.1f}%")
                    st.caption(change['interpretation'])
        
        with col2:
            st.markdown("#### 🎯 Estabilidade do Perfil")
            stability = self._calculate_profile_stability(assessments)
            
            stability_color = "success" if stability > 0.8 else "warning" if stability > 0.6 else "error"
            
            if stability_color == "success":
                st.success(f"**Alta Estabilidade** ({stability:.0%})")
                st.caption("Seu perfil tem se mantido consistente ao longo do tempo")
            elif stability_color == "warning":
                st.warning(f"**Estabilidade Moderada** ({stability:.0%})")
                st.caption("Algumas mudanças graduais foram observadas")
            else:
                st.error(f"**Baixa Estabilidade** ({stability:.0%})")
                st.caption("Mudanças significativas detectadas - pode indicar crescimento pessoal")
        
        # Predições e recomendações
        st.markdown("#### 🔮 Insights de Tendências")
        trends = self._analyze_trends(assessments)
        
        for trend in trends:
            st.info(f"**{trend['dimension']}**: {trend['prediction']}")
    
    def _render_benchmarks_tab(self, user_data: Dict) -> None:
        """Renderiza comparações com benchmarks"""
        
        latest = user_data['latest_assessment']
        benchmarks = user_data['benchmarks']
        
        if not latest or not benchmarks:
            st.info("Dados insuficientes para comparação com benchmarks")
            return
        
        st.markdown("### 🎯 Como Você se Compara")
        
        # Seletor de grupo de comparação
        comparison_group = st.selectbox(
            "Comparar com:",
            ["População Geral", "Sua Área Profissional", "Seu Nível Hierárquico", "Sua Faixa Etária"]
        )
        
        # Comparação DISC
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 DISC vs População")
            disc_comparison = self._create_disc_comparison_chart(latest.scores, benchmarks)
            st.plotly_chart(disc_comparison, use_container_width=True)
        
        with col2:
            st.markdown("#### 🧠 Big Five vs População")
            b5_comparison = self._create_b5_comparison_chart(latest.scores, benchmarks)
            st.plotly_chart(b5_comparison, use_container_width=True)
        
        # Percentis detalhados
        st.markdown("#### 📈 Seus Percentis Detalhados")
        
        percentiles_data = []
        
        # DISC percentis
        for key, value in latest.scores.disc.items():
            dimension = key.replace('DISC_', '')
            benchmark = benchmarks.get('disc_percentiles', {}).get(dimension, {})
            percentile = self._calculate_percentile(value, benchmark)
            
            percentiles_data.append({
                'Categoria': 'DISC',
                'Dimensão': dimension,
                'Seu Score': f"{value:.1f}",
                'Percentil': f"{percentile:.0f}%",
                'Interpretação': self._interpret_percentile(percentile)
            })
        
        # Big Five percentis
        for key, value in latest.scores.big_five.items():
            dimension = key.replace('B5_', '')
            trait_names = {'O': 'Abertura', 'C': 'Conscienciosidade', 'E': 'Extroversão', 'A': 'Amabilidade', 'N': 'Neuroticismo'}
            dimension_name = trait_names.get(dimension, dimension)
            
            percentiles_data.append({
                'Categoria': 'Big Five',
                'Dimensão': dimension_name,
                'Seu Score': f"{value:.1f}%",
                'Percentil': f"{value:.0f}%",  # Big Five já é em percentil
                'Interpretação': self._interpret_percentile(value)
            })
        
        df_percentiles = pd.DataFrame(percentiles_data)
        st.dataframe(df_percentiles, use_container_width=True)
        
        # Insights de posicionamento
        st.markdown("#### 💡 Insights de Posicionamento")
        positioning_insights = self._generate_positioning_insights(latest.scores, benchmarks)
        
        for insight in positioning_insights:
            st.info(f"**{insight['title']}**: {insight['description']}")
    
    def _render_ai_insights_tab(self, user_data: Dict) -> None:
        """Renderiza insights gerados por IA"""
        
        latest = user_data['latest_assessment']
        assessments = user_data['assessments']
        
        if not latest:
            st.info("Faça uma avaliação para receber insights personalizados da IA")
            return
        
        st.markdown("### 🤖 Insights Personalizados com IA")
        
        # Diferentes tipos de insights
        insight_type = st.selectbox(
            "Tipo de insight:",
            [
                "Análise Comportamental Profunda",
                "Recomendações de Carreira",
                "Estratégias de Desenvolvimento",
                "Compatibilidade em Equipes",
                "Gestão de Estresse Personalizada"
            ]
        )
        
        with st.spinner("🧠 Gerando insights personalizados..."):
            
            if insight_type == "Análise Comportamental Profunda":
                insights = self._generate_behavioral_analysis(latest)
                
            elif insight_type == "Recomendações de Carreira":
                insights = self._generate_career_insights(latest)
                
            elif insight_type == "Estratégias de Desenvolvimento":
                insights = self._generate_development_strategies(latest, assessments)
                
            elif insight_type == "Compatibilidade em Equipes":
                insights = self._generate_team_compatibility_insights(latest)
                
            else:  # Gestão de Estresse
                insights = self._generate_stress_management_insights(latest)
        
        # Renderiza insights
        for i, insight in enumerate(insights, 1):
            with st.expander(f"💡 {insight['title']}", expanded=i==1):
                st.markdown(insight['content'])
                
                if 'actions' in insight:
                    st.markdown("**Ações Recomendadas:**")
                    for action in insight['actions']:
                        st.markdown(f"• {action}")
        
        # Feedback sobre insights
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👍 Insights Úteis"):
                st.success("Obrigado pelo feedback!")
        
        with col2:
            if st.button("👎 Não Muito Útil"):
                st.info("Vamos melhorar nossos insights!")
        
        with col3:
            if st.button("💡 Sugerir Melhoria"):
                feedback = st.text_area("Como podemos melhorar?")
                if st.button("Enviar Sugestão"):
                    st.success("Sugestão enviada!")
    
    def _render_guest_dashboard(self) -> None:
        """Renderiza dashboard para usuários não logados"""
        
        st.markdown("""
        <div style='text-align: center; padding: 3rem 0;'>
            <h1 style='color: #8ab4f8;'>🧠 Dashboard NeuroMap</h1>
            <p style='color: #a8c7fa; font-size: 1.2rem; margin-bottom: 2rem;'>
                Faça login para acessar seu dashboard personalizado
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Demo do dashboard
        st.markdown("### 📊 Prévia do Dashboard")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Avaliações", "?", help="Número total de avaliações realizadas")
        
        with col2:
            st.metric("Tipo MBTI", "?", help="Seu tipo de personalidade atual")
        
        with col3:
            st.metric("Evolução", "?", help="Mudanças ao longo do tempo")
        
        # Call to action
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🔑 Fazer Login", use_container_width=True, type="primary"):
                st.switch_page("pages/auth.py")
            
            if st.button("📝 Criar Conta Gratuita", use_container_width=True):
                st.switch_page("pages/auth.py")
    
    def _render_empty_dashboard(self) -> None:
        """Renderiza dashboard quando usuário não tem avaliações"""
        
        st.markdown("""
        <div style='text-align: center; padding: 3rem 0;'>
            <h2 style='color: #8ab4f8;'>🌟 Bem-vindo ao NeuroMap!</h2>
            <p style='color: #a8c7fa; font-size: 1.1rem;'>
                Faça sua primeira avaliação para descobrir insights únicos sobre sua personalidade
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Benefícios da primeira avaliação
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🎯 Descubra
            - Seu perfil DISC
            - Traços Big Five
            - Tipo MBTI
            - Pontos fortes únicos
            """)
        
        with col2:
            st.markdown("""
            ### 📈 Desenvolva
            - Áreas de crescimento
            - Estratégias personalizadas
            - Planos de ação
            - Metas específicas
            """)
        
        with col3:
            st.markdown("""
            ### 💼 Aplique
            - Orientação de carreira
            - Melhoria de relacionamentos
            - Liderança efetiva
            - Comunicação assertiva
            """)
        
        # Call to action
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 Começar Minha Primeira Avaliação", use_container_width=True, type="primary"):
                st.switch_page("pages/assessment.py")
    
    # Métodos auxiliares para análises
    def _generate_mock_assessments(self) -> List[UserAssessment]:
        """Gera dados mock para demonstração"""
        # Implementação simplificada para demo
        return []
    
    def _generate_mock_analytics(self) -> Dict:
        """Gera analytics mock"""
        return {
            'total_assessments': 3,
            'assessment_frequency': 'Mensal',
            'assessment_streak': 5
        }
    
    def _generate_mock_benchmarks(self) -> Dict:
        """Gera benchmarks mock"""
        return {
            'disc_percentiles': {
                'D': {'p50': 25, 'mean': 25, 'std': 15},
                'I': {'p50': 25, 'mean': 25, 'std': 15},
                'S': {'p50': 25, 'mean': 25, 'std': 15},
                'C': {'p50': 25, 'mean': 25, 'std': 15}
            }
        }
    
    def _get_disc_level(self, score: float) -> str:
        """Retorna nível DISC baseado no score"""
        if score >= 70:
            return "Muito Alto"
        elif score >= 50:
            return "Alto"
        elif score >= 30:
            return "Médio"
        else:
            return "Baixo"
    
    def _get_disc_description(self, dimension: str, score: float) -> str:
        """Retorna descrição do score DISC"""
        descriptions = {
            'D': f"Orientação para resultados e liderança direta ({score:.1f}%)",
            'I': f"Habilidade de influência e comunicação ({score:.1f}%)",
            'S': f"Estabilidade e cooperação em equipe ({score:.1f}%)",
            'C': f"Foco em qualidade e conformidade ({score:.1f}%)"
        }
        return descriptions.get(dimension, f"Score: {score:.1f}%")
    
    def _get_b5_level(self, percentile: float) -> str:
        """Retorna nível Big Five baseado no percentil"""
        if percentile >= 80:
            return "Muito Alto"
        elif percentile >= 60:
            return "Alto"
        elif percentile >= 40:
            return "Médio"
        elif percentile >= 20:
            return "Baixo"
        else:
            return "Muito Baixo"
    
    def _generate_behavioral_analysis(self, assessment: UserAssessment) -> List[Dict]:
        """Gera análise comportamental com IA"""
        return [
            {
                'title': 'Padrão de Tomada de Decisão',
                'content': 'Baseado no seu perfil, você tende a tomar decisões de forma analítica...',
                'actions': ['Pratique decisões rápidas em situações de baixo risco', 'Use frameworks de decisão estruturados']
            }
        ]
    
    def _generate_career_insights(self, assessment: UserAssessment) -> List[Dict]:
        """Gera insights de carreira"""
        return [
            {
                'title': 'Funções Ideais para seu Perfil',
                'content': 'Seu perfil indica forte adequação para roles que envolvem...',
                'actions': ['Explore oportunidades em consultoria', 'Desenvolva habilidades de apresentação']
            }
        ]
    
    def _generate_development_strategies(self, latest: UserAssessment, assessments: List[UserAssessment]) -> List[Dict]:
        """Gera estratégias de desenvolvimento"""
        return [
            {
                'title': 'Plano de Desenvolvimento 90 dias',
                'content': 'Com base na sua evolução, recomendamos focar em...',
                'actions': ['Objetivo 1: Melhorar assertividade', 'Objetivo 2: Desenvolver empatia']
            }
        ]
    
    def _generate_team_compatibility_insights(self, assessment: UserAssessment) -> List[Dict]:
        """Gera insights de compatibilidade"""
        return [
            {
                'title': 'Dinâmica em Equipes',
                'content': 'Você funciona melhor em equipes que...',
                'actions': ['Busque roles colaborativos', 'Pratique feedback construtivo']
            }
        ]
    
    def _generate_stress_management_insights(self, assessment: UserAssessment) -> List[Dict]:
        """Gera insights de gestão de estresse"""
        return [
            {
                'title': 'Estratégias de Gestão de Estresse',
                'content': 'Baseado no seu perfil, você pode se beneficiar de...',
                'actions': ['Técnicas de respiração', 'Exercícios de mindfulness']
            }
        ]
