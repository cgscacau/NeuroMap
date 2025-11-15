import streamlit as st
import time
from datetime import datetime
from typing import Dict, List, Optional
from ...core.models import AssessmentItem, UserAssessment, PersonalityScores
from ...core.scoring import AdvancedScoringEngine, InsightGenerator
from ...services.database import db_manager
from ...utils.validators import ResponseValidator

class AssessmentPage:
    """Página de avaliação com experiência otimizada"""
    
    def __init__(self):
        self.scoring_engine = AdvancedScoringEngine()
        self.insight_generator = InsightGenerator()
        self.response_validator = ResponseValidator()
        self.items = self._load_assessment_items()
    
    def render(self) -> None:
        """Renderiza a página de avaliação"""
        
        # Inicializa estado da sessão
        self._initialize_session_state()
        
        # Header com progresso
        self._render_header()
        
        # Conteúdo principal baseado no estado
        if st.session_state.assessment_state == 'intro':
            self._render_introduction()
        elif st.session_state.assessment_state == 'questions':
            self._render_questions()
        elif st.session_state.assessment_state == 'processing':
            self._render_processing()
        elif st.session_state.assessment_state == 'results':
            self._render_results()
    
    def _initialize_session_state(self) -> None:
        """Inicializa estado da sessão"""
        
        if 'assessment_state' not in st.session_state:
            st.session_state.assessment_state = 'intro'
        
        if 'assessment_answers' not in st.session_state:
            st.session_state.assessment_answers = {}
        
        if 'assessment_start_time' not in st.session_state:
            st.session_state.assessment_start_time = None
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 0
        
        if 'assessment_results' not in st.session_state:
            st.session_state.assessment_results = None
    
    def _render_header(self) -> None:
        """Renderiza cabeçalho com progresso"""
        
        total_questions = len(self.items)
        answered = len([k for k, v in st.session_state.assessment_answers.items() if v > 0])
        
        # Barra de progresso
        progress = answered / total_questions if total_questions > 0 else 0
        
        col1, col2, col3 = st.columns([2, 3, 2])
        
        with col1:
            st.metric("Questões", f"{answered}/{total_questions}")
        
        with col2:
            st.progress(progress)
            st.caption(f"Progresso: {progress:.1%}")
        
        with col3:
            if st.session_state.assessment_start_time:
                elapsed = (datetime.now() - st.session_state.assessment_start_time).seconds // 60
                st.metric("Tempo", f"{elapsed} min")
    
    def _render_introduction(self) -> None:
        """Renderiza introdução da avaliação"""
        
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='color: #8ab4f8;'>🧠 Avaliação de Personalidade NeuroMap</h1>
            <p style='color: #a8c7fa; font-size: 1.2rem;'>
                Descubra seu perfil único combinando DISC, Big Five e MBTI
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Informações sobre a avaliação
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### ⏱️ **Informações Gerais**
            - **Duração:** 15-20 minutos
            - **Questões:** 48 perguntas
            - **Formato:** Escala Likert (1-5)
            - **Idioma:** Português brasileiro
            """)
        
        with col2:
            st.markdown("""
            ### 📊 **O que você receberá:**
            - Perfil DISC detalhado
            - Scores Big Five com percentis
            - Tipo MBTI com preferências
            - Insights personalizados de carreira
            """)
        
        # Instruções detalhadas
        with st.expander("📋 Instruções Detalhadas", expanded=True):
            st.markdown("""
            **Como responder:**
            
            1. **Seja honesto:** Não há respostas certas ou erradas
            2. **Primeira impressão:** Responda com base na sua reação inicial
            3. **Contexto profissional:** Considere como você age no trabalho/estudos
            4. **Consistência:** Tente ser consistente em suas respostas
            5. **Sem pressa:** Tome o tempo necessário para refletir
            
            **Escala de respostas:**
            - **1 = Discordo totalmente** - Não me identifico nada com a afirmação
            - **2 = Discordo parcialmente** - Me identifico pouco
            - **3 = Neutro** - Às vezes sim, às vezes não
            - **4 = Concordo parcialmente** - Me identifico na maioria das vezes
            - **5 = Concordo totalmente** - Me identifico completamente
            """)
        
        # Avisos importantes
        st.warning("""
        ⚠️ **Importante:**
        - Seus dados são privados e seguros
        - Você pode pausar e retomar a qualquer momento
        - Recomendamos fazer em ambiente tranquilo
        - Evite interrupções durante a avaliação
        """)
        
        # Botão para iniciar
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 Iniciar Avaliação", use_container_width=True, type="primary"):
                st.session_state.assessment_state = 'questions'
                st.session_state.assessment_start_time = datetime.now()
                st.rerun()
    
    def _render_questions(self) -> None:
        """Renderiza questões da avaliação"""
        
        questions_per_page = 8
        total_pages = (len(self.items) + questions_per_page - 1) // questions_per_page
        current_page = st.session_state.current_page
        
        # Navegação entre páginas
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if current_page > 0:
                if st.button("⬅️ Página Anterior"):
                    st.session_state.current_page -= 1
                    st.rerun()
        
        with col2:
            st.markdown(f"<h3 style='text-align: center;'>Página {current_page + 1} de {total_pages}</h3>", 
                       unsafe_allow_html=True)
        
        with col3:
            if current_page < total_pages - 1:
                if st.button("Próxima Página ➡️"):
                    st.session_state.current_page += 1
                    st.rerun()
        
        st.divider()
        
        # Questões da página atual
        start_idx = current_page * questions_per_page
        end_idx = min(start_idx + questions_per_page, len(self.items))
        page_items = self.items[start_idx:end_idx]
        
        for item in page_items:
            self._render_question(item)
        
        st.divider()
        
        # Botões de ação
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("💾 Salvar Progresso"):
                self._save_progress()
        
        with col2:
            if st.button("🔄 Resetar Respostas"):
                if st.session_state.get('confirm_reset', False):
                    st.session_state.assessment_answers = {}
                    st.session_state.confirm_reset = False
                    st.success("Respostas resetadas!")
                    st.rerun()
                else:
                    st.session_state.confirm_reset = True
                    st.warning("Clique novamente para confirmar")
        
        with col3:
            answered_count = len([k for k, v in st.session_state.assessment_answers.items() if v > 0])
            if answered_count >= len(self.items):
                if st.button("✨ Finalizar Avaliação", type="primary"):
                    self._finalize_assessment()
            else:
                remaining = len(self.items) - answered_count
                st.info(f"Faltam {remaining} questões")
    
    def _render_question(self, item: AssessmentItem) -> None:
        """Renderiza uma questão individual"""
        
        # Container da questão
        with st.container():
            st.markdown(f"**{item.id}.** {item.text}")
            
            # Escala de resposta com emojis
            response_options = {
                1: "1️⃣ Discordo totalmente",
                2: "2️⃣ Discordo parcialmente", 
                3: "3️⃣ Neutro",
                4: "4️⃣ Concordo parcialmente",
                5: "5️⃣ Concordo totalmente"
            }
            
            current_value = st.session_state.assessment_answers.get(item.id, 3)
            
            # Radio buttons horizontais
            selected = st.radio(
                "Escolha sua resposta:",
                options=list(response_options.keys()),
                format_func=lambda x: response_options[x],
                key=f"q_{item.id}",
                index=current_value - 1,
                horizontal=True,
                label_visibility="collapsed"
            )
            
            st.session_state.assessment_answers[item.id] = selected
            
            # Indicador visual de resposta
            confidence_colors = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢", 5: "🟢"}
            st.caption(f"Sua resposta: {confidence_colors[selected]} {response_options[selected]}")
            
            st.divider()
    
    def _render_processing(self) -> None:
        """Renderiza tela de processamento"""
        
        st.markdown("""
        <div style='text-align: center; padding: 3rem 0;'>
            <h2 style='color: #8ab4f8;'>🔄 Processando sua avaliação...</h2>
            <p style='color: #a8c7fa;'>Analisando suas respostas com algoritmos avançados</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Barra de progresso animada
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        processing_steps = [
            "Validando respostas...",
            "Calculando scores DISC...",
            "Analisando Big Five...",
            "Determinando tipo MBTI...",
            "Gerando insights personalizados...",
            "Criando relatório final..."
        ]
        
        for i, step in enumerate(processing_steps):
            status_text.text(step)
            progress_bar.progress((i + 1) / len(processing_steps))
            time.sleep(1)  # Simula processamento
        
        # Processa resultados reais
        self._process_results()
        
        status_text.text("✅ Processamento concluído!")
        time.sleep(1)
        
        st.session_state.assessment_state = 'results'
        st.rerun()
    
    def _render_results(self) -> None:
        """Renderiza resultados da avaliação"""
        
        if not st.session_state.assessment_results:
            st.error("Erro: Resultados não encontrados")
            return
        
        results = st.session_state.assessment_results
        scores = results['scores']
        insights = results['insights']
        
        # Header dos resultados
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='color: #8ab4f8;'>🎉 Seus Resultados Estão Prontos!</h1>
            <p style='color: #a8c7fa;'>Descubra insights únicos sobre sua personalidade</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Resumo executivo
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dominant_disc, strength = scores.get_dominant_disc()
            st.metric("Estilo DISC", dominant_disc, f"{strength:.0f}%")
        
        with col2:
            st.metric("Tipo MBTI", scores.mbti_type)
        
        with col3:
            reliability = st.session_state.assessment_results.get('reliability_score', 0.85)
            st.metric("Confiabilidade", f"{reliability:.0%}")
        
        # Tabs com diferentes visualizações
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Visão Geral", 
            "🎯 Insights Pessoais", 
            "💼 Carreira", 
            "📄 Relatório Completo"
        ])
        
        with tab1:
            self._render_overview_tab(scores, insights)
        
        with tab2:
            self._render_insights_tab(insights)
        
        with tab3:
            self._render_career_tab(insights)
        
        with tab4:
            self._render_report_tab(scores, insights)
        
        # Ações finais
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Ver Dashboard Completo", use_container_width=True):
                st.switch_page("pages/dashboard.py")
        
        with col2:
            if st.button("🔄 Nova Avaliação", use_container_width=True):
                self._reset_assessment()
        
        with col3:
            if st.button("📤 Compartilhar Resultados", use_container_width=True):
                self._show_sharing_options()
    
    def _process_results(self) -> None:
        """Processa resultados da avaliação"""
        
        try:
            # Calcula scores
            scores = self.scoring_engine.calculate_scores_with_confidence(
                st.session_state.assessment_answers, 
                self.items
            )
            
            # Gera insights
            user_context = {
                'email': st.session_state.get('user_email'),
                'industry': st.session_state.get('user_industry'),
                'role_level': st.session_state.get('user_role_level')
            }
            
            insights = self.insight_generator.generate_comprehensive_insights(
                scores, user_context
            )
            
            # Calcula confiabilidade
            reliability_score = self._calculate_reliability_score()
            
            # Salva no banco se usuário logado
            if st.session_state.get('user_id'):
                self._save_assessment_to_db(scores, insights, reliability_score)
            
            # Armazena na sessão
            st.session_state.assessment_results = {
                'scores': scores,
                'insights': insights,
                'reliability_score': reliability_score,
                'completion_time': self._calculate_completion_time()
            }
            
        except Exception as e:
            st.error(f"Erro ao processar resultados: {e}")
            st.session_state.assessment_state = 'questions'
    
    def _calculate_reliability_score(self) -> float:
        """Calcula score de confiabilidade das respostas"""
        
        responses = list(st.session_state.assessment_answers.values())
        
        # Verifica variabilidade
        import numpy as np
        variance = np.var(responses)
        
        # Verifica padrões suspeitos
        if len(set(responses)) == 1:  # Todas respostas iguais
            return 0.2
        
        if variance < 0.5:  # Muito pouca variação
            return 0.4
        
        # Score baseado na distribuição esperada
        expected_variance = 1.5
        reliability = min(1.0, variance / expected_variance)
        
        return max(0.3, reliability)  # Mínimo de 30%
    
    def _calculate_completion_time(self) -> int:
        """Calcula tempo de conclusão em minutos"""
        
        if st.session_state.assessment_start_time:
            delta = datetime.now() - st.session_state.assessment_start_time
            return delta.seconds // 60
        return 0
    
    def _load_assessment_items(self) -> List[AssessmentItem]:
        """Carrega itens da avaliação (mock - em produção viria do banco)"""
        # Retorna os mesmos itens do código original, mas estruturados
        # Por brevidade, usando apenas alguns exemplos
        
        items = []
        sample_texts = [
            "Gosto de assumir a responsabilidade quando algo importante precisa ser feito.",
            "Tenho facilidade em enxergar soluções lógicas para problemas complexos.",
            "Gosto de seguir métodos e padrões bem definidos.",
            "Prefiro agir rapidamente a ficar analisando demais uma situação."
        ]
        
        for i, text in enumerate(sample_texts, 1):
            item = AssessmentItem(
                id=i,
                text=text,
                category="DISC" if i <= 2 else "B5",
                weights={"DISC_D": 0.8} if i == 1 else {"B5_O": 0.7}
            )
            items.append(item)
        
        return items
    
    def _finalize_assessment(self) -> None:
        """Finaliza avaliação e vai para processamento"""
        st.session_state.assessment_state = 'processing'
        st.rerun()
    
    def _save_progress(self) -> None:
        """Salva progresso atual"""
        # Em produção, salvaria no banco
        st.success("✅ Progresso salvo!")
    
    def _reset_assessment(self) -> None:
        """Reseta avaliação para começar novamente"""
        keys_to_clear = [
            'assessment_state', 'assessment_answers', 'assessment_start_time',
            'current_page', 'assessment_results', 'confirm_reset'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        st.rerun()
    
    def _save_assessment_to_db(self, scores: PersonalityScores, insights, reliability_score: float) -> None:
        """Salva avaliação no banco de dados"""
        try:
            assessment = UserAssessment(
                user_id=st.session_state.user_id,
                assessment_id=f"assess_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                answers=st.session_state.assessment_answers,
                scores=scores,
                profile_insights=insights,
                timestamp=datetime.now(),
                completion_time_minutes=self._calculate_completion_time(),
                reliability_score=reliability_score
            )
            
            # Salva de forma assíncrona (em produção)
            # await db_manager.save_assessment(st.session_state.user_id, assessment)
            
        except Exception as e:
            st.warning(f"Avaliação processada, mas não foi possível salvar: {e}")
    
    def _render_overview_tab(self, scores, insights) -> None:
        """Renderiza tab de visão geral"""
        st.markdown("### 📊 Resumo do seu Perfil")
        # Implementar visualizações usando PersonalityVisualizer
        pass
    
    def _render_insights_tab(self, insights) -> None:
        """Renderiza tab de insights pessoais"""
        st.markdown("### 🎯 Seus Insights Únicos")
        # Mostrar insights detalhados
        pass
    
    def _render_career_tab(self, insights) -> None:
        """Renderiza tab de carreira"""
        st.markdown("### 💼 Orientações de Carreira")
        # Mostrar sugestões de carreira
        pass
    
    def _render_report_tab(self, scores, insights) -> None:
        """Renderiza tab de relatório"""
        st.markdown("### 📄 Relatório Completo")
        # Opções de download e compartilhamento
        pass
    
    def _show_sharing_options(self) -> None:
        """Mostra opções de compartilhamento"""
        st.info("🔗 Funcionalidade de compartilhamento em desenvolvimento")
