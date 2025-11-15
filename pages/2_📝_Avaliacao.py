import streamlit as st
import json
import time
from datetime import datetime

st.set_page_config(
    page_title="Avaliação - NeuroMap",
    page_icon="📝",
    layout="wide"
)

# Verifica autenticação
if not st.session_state.get('user_authenticated', False):
    st.warning("🔒 Faça login para acessar esta página")
    st.stop()

# Inicializa estado da avaliação
if 'assessment_state' not in st.session_state:
    st.session_state.assessment_state = 'intro'

if 'assessment_answers' not in st.session_state:
    st.session_state.assessment_answers = {}

if 'current_question' not in st.session_state:
    st.session_state.current_question = 1

if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# Questões da avaliação (versão simplificada)
QUESTIONS = [
    {
        "id": 1,
        "text": "Gosto de assumir a responsabilidade quando algo importante precisa ser feito.",
        "category": "DISC_D"
    },
    {
        "id": 2,
        "text": "Tenho facilidade em enxergar soluções lógicas para problemas complexos.",
        "category": "B5_O"
    },
    {
        "id": 3,
        "text": "Gosto de seguir métodos e padrões bem definidos.",
        "category": "DISC_C"
    },
    {
        "id": 4,
        "text": "Prefiro agir rapidamente a ficar analisando demais uma situação.",
        "category": "MBTI_P"
    },
    {
        "id": 5,
        "text": "Tenho prazer em planejar as coisas com antecedência.",
        "category": "MBTI_J"
    },
    {
        "id": 6,
        "text": "Fico desconfortável quando as pessoas são muito emotivas ao meu redor.",
        "category": "MBTI_T"
    },
    {
        "id": 7,
        "text": "Sinto-me motivado quando enfrento grandes desafios.",
        "category": "DISC_D"
    },
    {
        "id": 8,
        "text": "Quando erro, costumo me cobrar mais do que os outros cobrariam.",
        "category": "B5_N"
    },
    {
        "id": 9,
        "text": "Gosto de aprender coisas novas, mesmo que não sejam úteis de imediato.",
        "category": "B5_O"
    },
    {
        "id": 10,
        "text": "Prefiro ter controle total de um projeto a depender de outras pessoas.",
        "category": "DISC_D"
    },
    {
        "id": 11,
        "text": "Tenho facilidade em lidar com situações novas e incertas.",
        "category": "B5_O"
    },
    {
        "id": 12,
        "text": "Quando alguém discorda de mim, busco entender o ponto de vista antes de responder.",
        "category": "B5_A"
    },
    {
        "id": 13,
        "text": "Costumo esconder o que sinto para evitar conflitos.",
        "category": "MBTI_T"
    },
    {
        "id": 14,
        "text": "Tenho facilidade em me colocar no lugar dos outros.",
        "category": "B5_A"
    },
    {
        "id": 15,
        "text": "Fico incomodado quando as pessoas não cumprem o que prometem.",
        "category": "B5_C"
    },
    {
        "id": 16,
        "text": "Gosto de estar rodeado de pessoas e conversar sobre vários assuntos.",
        "category": "MBTI_E"
    },
    {
        "id": 17,
        "text": "Quando estou sob pressão, consigo manter a calma e pensar com clareza.",
        "category": "B5_N"
    },
    {
        "id": 18,
        "text": "Tenho dificuldade em aceitar críticas, mesmo quando são construtivas.",
        "category": "B5_N"
    },
    {
        "id": 19,
        "text": "Gosto de ajudar os outros, mesmo que isso atrase minhas tarefas.",
        "category": "B5_A"
    },
    {
        "id": 20,
        "text": "Em situações tensas, minha primeira reação costuma ser emocional.",
        "category": "MBTI_F"
    }
]

def main():
    if st.session_state.assessment_state == 'intro':
        render_introduction()
    elif st.session_state.assessment_state == 'questions':
        render_questions()
    elif st.session_state.assessment_state == 'processing':
        render_processing()
    elif st.session_state.assessment_state == 'results':
        render_results()

def render_introduction():
    st.title("📝 Avaliação de Personalidade NeuroMap")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🎯 **Sobre esta Avaliação**
        
        Você está prestes a descobrir insights únicos sobre sua personalidade através de uma 
        avaliação científica que combina três dos modelos mais respeitados da psicologia:
        
        - **🎭 DISC**: Seu estilo comportamental no trabalho
        - **🧠 Big Five**: Os cinco grandes traços de personalidade  
        - **💭 MBTI**: Suas preferências cognitivas naturais
        """)
        
        st.markdown("""
        ### ⏱️ **Informações Importantes**
        
        - **Duração**: 15-20 minutos
        - **Questões**: 20 perguntas (versão simplificada)
        - **Formato**: Escala de 1 (Discordo totalmente) a 5 (Concordo totalmente)
        - **Privacidade**: Seus dados são 100% confidenciais
        """)
    
    with col2:
        st.info("""
        ### 📋 **Como Responder**
        
        ✅ **Seja honesto** - não há respostas certas ou erradas
        
        ✅ **Primeira impressão** - responda instintivamente
        
        ✅ **Contexto profissional** - pense em como você age no trabalho
        
        ✅ **Sem pressa** - tome o tempo que precisar
        """)
    
    st.markdown("---")
    
    # Botão para iniciar
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Iniciar Avaliação", type="primary", use_container_width=True):
            st.session_state.assessment_state = 'questions'
            st.session_state.start_time = datetime.now()
            st.rerun()

def render_questions():
    # Progress
    total_questions = len(QUESTIONS)
    answered = len([k for k, v in st.session_state.assessment_answers.items() if v > 0])
    progress = answered / total_questions
    
    st.title("📝 Avaliação em Andamento")
    
    # Barra de progresso
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col1:
        st.metric("Questões", f"{answered}/{total_questions}")
    
    with col2:
        st.progress(progress)
        st.caption(f"Progresso: {progress:.1%}")
    
    with col3:
        if st.session_state.start_time:
            elapsed = (datetime.now() - st.session_state.start_time).seconds // 60
            st.metric("Tempo", f"{elapsed} min")
    
    st.markdown("---")
    
    # Questões (4 por página)
    questions_per_page = 4
    total_pages = (len(QUESTIONS) + questions_per_page - 1) // questions_per_page
    current_page = st.session_state.current_question // questions_per_page
    
    # Navegação
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_page > 0:
            if st.button("⬅️ Anterior"):
                st.session_state.current_question = max(1, st.session_state.current_question - questions_per_page)
                st.rerun()
    
    with col2:
        st.markdown(f"<h3 style='text-align: center;'>Página {current_page + 1} de {total_pages}</h3>", 
                   unsafe_allow_html=True)
    
    with col3:
        if current_page < total_pages - 1:
            if st.button("Próxima ➡️"):
                st.session_state.current_question = min(len(QUESTIONS), st.session_state.current_question + questions_per_page)
                st.rerun()
    
    st.markdown("---")
    
    # Renderiza questões da página atual
    start_idx = current_page * questions_per_page
    end_idx = min(start_idx + questions_per_page, len(QUESTIONS))
    
    for i in range(start_idx, end_idx):
        question = QUESTIONS[i]
        render_single_question(question)
    
    st.markdown("---")
    
    # Ações
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Salvar Progresso"):
            st.success("Progresso salvo!")
    
    with col2:
        if answered >= total_questions:
            if st.button("✨ Finalizar Avaliação", type="primary"):
                st.session_state.assessment_state = 'processing'
                st.rerun()
        else:
            remaining = total_questions - answered
            st.info(f"Faltam {remaining} questões")
    
    with col3:
        if st.button("🔄 Recomeçar"):
            st.session_state.assessment_answers = {}
            st.session_state.current_question = 1
            st.rerun()

def render_single_question(question):
    with st.container():
        st.markdown(f"### {question['id']}. {question['text']}")
        
        # Escala Likert
        current_value = st.session_state.assessment_answers.get(question['id'], 3)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        scale_options = [
            (1, "1️⃣", "Discordo totalmente"),
            (2, "2️⃣", "Discordo parcialmente"),
            (3, "3️⃣", "Neutro"),
            (4, "4️⃣", "Concordo parcialmente"),
            (5, "5️⃣", "Concordo totalmente")
        ]
        
        cols = [col1, col2, col3, col4, col5]
        
        for i, (value, emoji, label) in enumerate(scale_options):
            with cols[i]:
                is_selected = (current_value == value)
                
                button_style = "primary" if is_selected else "secondary"
                
                if st.button(f"{emoji}\n{label}", key=f"q{question['id']}_opt{value}"):
                    st.session_state.assessment_answers[question['id']] = value
                    st.rerun()
        
        # Slider alternativo
        st.markdown("**Ou use o controle deslizante:**")
        slider_value = st.slider(
            "Sua resposta:",
            min_value=1,
            max_value=5,
            value=current_value,
            key=f"q{question['id']}_slider",
            help="1 = Discordo totalmente, 5 = Concordo totalmente"
        )
        
        st.session_state.assessment_answers[question['id']] = slider_value
        
        st.markdown("---")

def render_processing():
    st.title("🔄 Processando sua Avaliação")
    
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <h2>🧠 Analisando suas respostas...</h2>
        <p>Nossos algoritmos estão calculando seu perfil único de personalidade</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Barra de progresso animada
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    steps = [
        "Validando respostas...",
        "Calculando scores DISC...",
        "Analisando Big Five...",
        "Determinando tipo MBTI...",
        "Gerando insights personalizados...",
        "Finalizando relatório..."
    ]
    
    for i, step in enumerate(steps):
        status_text.text(step)
        progress_bar.progress((i + 1) / len(steps))
        time.sleep(1)
    
    # Simula processamento dos resultados
    calculate_results()
    
    status_text.text("✅ Processamento concluído!")
    time.sleep(1)
    
    st.session_state.assessment_state = 'results'
    st.session_state.assessment_completed = True
    st.rerun()

def calculate_results():
    """Calcula resultados baseados nas respostas (versão simplificada)"""
    
    answers = st.session_state.assessment_answers
    
    # Cálculo simplificado dos scores
    disc_scores = {"D": 0, "I": 0, "S": 0, "C": 0}
    b5_scores = {"O": 0, "C": 0, "E": 0, "A": 0, "N": 0}
    mbti_scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    
    # Mapeia respostas para dimensões (simplificado)
    for q_id, answer in answers.items():
        question = next(q for q in QUESTIONS if q['id'] == q_id)
        category = question['category']
        
        if category.startswith('DISC_'):
            dim = category.split('_')[1]
            disc_scores[dim] += answer * 20  # Multiplica para escala 0-100
        elif category.startswith('B5_'):
            dim = category.split('_')[1]
            b5_scores[dim] += answer * 20
        elif category.startswith('MBTI_'):
            dim = category.split('_')[1]
            mbti_scores[dim] += answer
    
    # Normaliza DISC para soma 100%
    disc_total = sum(disc_scores.values())
    if disc_total > 0:
        for key in disc_scores:
            disc_scores[key] = (disc_scores[key] / disc_total) * 100
    
    # Determina tipo MBTI
    mbti_type = ""
    mbti_type += "E" if mbti_scores["E"] >= mbti_scores["I"] else "I"
    mbti_type += "S" if mbti_scores["S"] >= mbti_scores["N"] else "N"
    mbti_type += "T" if mbti_scores["T"] >= mbti_scores["F"] else "F"
    mbti_type += "J" if mbti_scores["J"] >= mbti_scores["P"] else "P"
    
    # Armazena resultados
    st.session_state.results = {
        "disc": disc_scores,
        "big_five": b5_scores,
        "mbti_type": mbti_type,
        "mbti_scores": mbti_scores,
        "completion_time": (datetime.now() - st.session_state.start_time).seconds // 60 if st.session_state.start_time else 0
    }

def render_results():
    st.title("🎉 Seus Resultados Estão Prontos!")
    
    results = st.session_state.get('results', {})
    
    if not results:
        st.error("Erro ao carregar resultados")
        return
    
    # Header dos resultados
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dominant_disc = max(results['disc'], key=results['disc'].get)
        st.metric("Estilo DISC", f"{dominant_disc}", f"{results['disc'][dominant_disc]:.0f}%")
    
    with col2:
        st.metric("Tipo MBTI", results['mbti_type'])
    
    with col3:
        st.metric("Tempo Conclusão", f"{results['completion_time']} min")
    
    st.markdown("---")
    
    # Tabs com resultados
    tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "🎯 Insights", "📄 Relatório"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Perfil DISC")
            
            import plotly.graph_objects as go
            
            fig = go.Figure(go.Bar(
                x=list(results['disc'].keys()),
                y=list(results['disc'].values()),
                marker_color=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
            ))
            
            fig.update_layout(
                title="Seus Scores DISC",
                yaxis_title="Percentual (%)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🧠 Big Five")
            
            traits = ['Abertura', 'Conscienciosidade', 'Extroversão', 'Amabilidade', 'Neuroticismo']
            values = list(results['big_five'].values())
            
            fig = go.Figure(go.Bar(
                y=traits,
                x=values,
                orientation='h',
                marker_color='#8ab4f8'
            ))
            
            fig.update_layout(
                title="Seus Scores Big Five",
                xaxis_title="Score",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 🎯 Seus Insights Personalizados")
        
        # Gera insights baseados no perfil
        dominant_disc = max(results['disc'], key=results['disc'].get)
        mbti_type = results['mbti_type']
        
        insights = generate_insights(dominant_disc, mbti_type, results)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"""
            **🏆 Principais Forças:**
            
            {insights['strengths']}
            """)
        
        with col2:
            st.info(f"""
            **📈 Áreas de Desenvolvimento:**
            
            {insights['development']}
            """)
        
        st.markdown("---")
        
        st.info(f"""
        **💼 Sugestões de Carreira:**
        
        {insights['career']}
        """)
    
    with tab3:
        st.markdown("### 📄 Relatório Completo")
        
        # Opções de relatório
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox(
                "Tipo de relatório:",
                ["Executivo", "Completo", "Para Coaching"]
            )
        
        with col2:
            format_type = st.selectbox(
                "Formato:",
                ["PDF", "HTML"]
            )
        
        if st.button("📄 Gerar Relatório", type="primary", use_container_width=True):
            # Simula geração de relatório
            with st.spinner("Gerando relatório..."):
                time.sleep(2)
                
                # Cria conteúdo do relatório
                report_content = generate_report(results, report_type)
                
                if format_type == "HTML":
                    st.markdown(report_content, unsafe_allow_html=True)
                else:
                    st.success("Relatório PDF gerado! (funcionalidade completa em desenvolvimento)")
    
    # Ações finais
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Ver Dashboard", use_container_width=True):
            st.switch_page("pages/1_📊_Dashboard.py")
    
    with col2:
        if st.button("🔄 Nova Avaliação", use_container_width=True):
            # Reset para nova avaliação
            st.session_state.assessment_answers = {}
            st.session_state.current_question = 1
            st.session_state.assessment_state = 'intro'
            st.rerun()
    
    with col3:
        if st.button("🏠 Página Inicial", use_container_width=True):
            st.switch_page("app.py")

def generate_insights(dominant_disc, mbti_type, results):
    """Gera insights baseados no perfil"""
    
    disc_insights = {
        "D": {
            "strengths": "• Liderança natural\n• Orientação para resultados\n• Tomada de decisão rápida\n• Capacidade de assumir riscos",
            "development": "• Desenvolver paciência\n• Melhorar escuta ativa\n• Praticar colaboração\n• Controlar impulsividade",
            "career": "• Gerente/Diretor\n• Empreendedor\n• Consultor\n• Líder de projetos"
        },
        "I": {
            "strengths": "• Comunicação persuasiva\n• Networking efetivo\n• Motivação de equipes\n• Criatividade social",
            "development": "• Foco em detalhes\n• Follow-up consistente\n• Organização pessoal\n• Análise de dados",
            "career": "• Vendas\n• Marketing\n• Relações Públicas\n• Treinamento"
        },
        "S": {
            "strengths": "• Estabilidade emocional\n• Trabalho em equipe\n• Confiabilidade\n• Paciência",
            "development": "• Assertividade\n• Adaptação a mudanças\n• Tomada de iniciativa\n• Autoconfiança",
            "career": "• Recursos Humanos\n• Suporte ao cliente\n• Administração\n• Educação"
        },
        "C": {
            "strengths": "• Atenção aos detalhes\n• Qualidade técnica\n• Análise sistemática\n• Precisão",
            "development": "• Flexibilidade\n• Comunicação interpessoal\n• Tolerância à ambiguidade\n• Velocidade de decisão",
            "career": "• Analista\n• Contador\n• Engenheiro\n• Pesquisador"
        }
    }
    
    return disc_insights.get(dominant_disc, disc_insights["D"])

def generate_report(results, report_type):
    """Gera conteúdo do relatório"""
    
    dominant_disc = max(results['disc'], key=results['disc'].get)
    
    return f"""
    <div style='background: #1e2a44; padding: 2rem; border-radius: 12px; margin: 1rem 0;'>
        <h2 style='color: #8ab4f8; text-align: center;'>Relatório NeuroMap - {report_type}</h2>
        
        <h3 style='color: #a8c7fa;'>Resumo Executivo</h3>
        <p>Seu perfil apresenta predominância no estilo <strong>{dominant_disc}</strong> 
        ({results['disc'][dominant_disc]:.0f}%), com tipo MBTI <strong>{results['mbti_type']}</strong>.</p>
        
        <h3 style='color: #a8c7fa;'>Scores DISC</h3>
        <ul>
            <li>Dominância: {results['disc']['D']:.0f}%</li>
            <li>Influência: {results['disc']['I']:.0f}%</li>
            <li>Estabilidade: {results['disc']['S']:.0f}%</li>
            <li>Conformidade: {results['disc']['C']:.0f}%</li>
        </ul>
        
        <h3 style='color: #a8c7fa;'>Big Five</h3>
        <ul>
            <li>Abertura: {results['big_five']['O']:.0f}</li>
            <li>Conscienciosidade: {results['big_five']['C']:.0f}</li>
            <li>Extroversão: {results['big_five']['E']:.0f}</li>
            <li>Amabilidade: {results['big_five']['A']:.0f}</li>
            <li>Neuroticismo: {results['big_five']['N']:.0f}</li>
        </ul>
        
        <p style='text-align: center; margin-top: 2rem; color: #94a3b8;'>
            Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}
        </p>
    </div>
    """

if __name__ == "__main__":
    main()
