import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Dashboard - NeuroMap",
    page_icon="📊",
    layout="wide"
)

# Verifica autenticação
if not st.session_state.get('user_authenticated', False):
    st.warning("🔒 Faça login para acessar esta página")
    st.stop()

st.title("📊 Dashboard Completo")

# Tabs principais
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Visão Geral",
    "📈 Análise Detalhada", 
    "⏰ Evolução Temporal",
    "🎯 Benchmarks"
])

with tab1:
    st.markdown("### 🎯 Resumo da Sua Personalidade")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Tipo MBTI", "INTJ", help="Seu tipo de personalidade")
    
    with col2:
        st.metric("DISC Dominante", "D (75%)", delta="+5%")
    
    with col3:
        st.metric("Confiabilidade", "87%", delta="+2%")
    
    with col4:
        st.metric("Última Avaliação", "Hoje")
    
    st.markdown("---")
    
    # Gráficos principais
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Perfil DISC Radar")
        
        # Gráfico radar DISC
        categories = ['Dominância', 'Influência', 'Estabilidade', 'Conformidade']
        values = [75, 45, 30, 60]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='Seu Perfil',
            line_color='#8ab4f8',
            fillcolor='rgba(138, 180, 248, 0.3)'
        ))
        
        # Linha de comparação
        benchmark = [25, 25, 25, 25]
        fig.add_trace(go.Scatterpolar(
            r=benchmark + [benchmark[0]],
            theta=categories + [categories[0]],
            fill=None,
            name='Média Populacional',
            line=dict(color='gray', dash='dash')
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🧠 Big Five Percentis")
        
        traits = ['Abertura', 'Conscienciosidade', 'Extroversão', 'Amabilidade', 'Neuroticismo']
        percentiles = [85, 90, 35, 75, 20]
        colors = ['#ff9f43', '#6c5ce7', '#fd79a8', '#00b894', '#e17055']
        
        fig = go.Figure(go.Bar(
            y=traits,
            x=percentiles,
            orientation='h',
            marker_color=colors,
            text=[f'{p}%' for p in percentiles],
            textposition='auto'
        ))
        
        fig.add_vline(x=50, line_dash="dash", line_color="gray", 
                     annotation_text="Média (50%)")
        
        fig.update_layout(
            title="Seus Percentis Populacionais",
            xaxis_title="Percentil (%)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### 🔍 Análise Detalhada")
    
    analysis_type = st.selectbox(
        "Escolha o tipo de análise:",
        ["DISC Completo", "Big Five Detalhado", "MBTI Preferências", "Análise de Confiabilidade"]
    )
    
    if analysis_type == "DISC Completo":
        st.markdown("#### 🎯 Análise DISC Detalhada")
        
        # Tabela de scores
        disc_data = {
            'Dimensão': ['Dominância', 'Influência', 'Estabilidade', 'Conformidade'],
            'Score': [75, 45, 30, 60],
            'Nível': ['Muito Alto', 'Médio', 'Baixo', 'Alto'],
            'Descrição': [
                'Orientação forte para resultados e liderança',
                'Habilidade moderada de comunicação e persuasão',
                'Preferência por mudanças e variedade',
                'Foco significativo em qualidade e precisão'
            ]
        }
        
        df = pd.DataFrame(disc_data)
        st.dataframe(df, use_container_width=True)
        
        # Insights específicos
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("""
            **🏆 Estilo Dominante: D (75%)**
            
            Você demonstra forte orientação para resultados, gosta de assumir liderança
            e toma decisões rapidamente. Prefere ambientes desafiadores onde pode
            exercer controle e influência.
            """)
        
        with col2:
            st.info("""
            **💡 Recomendações:**
            
            • Pratique escuta ativa em reuniões
            • Desenvolva paciência com processos colaborativos  
            • Invista em feedback 360° regular
            • Balance assertividade com empatia
            """)

with tab3:
    st.markdown("### 📈 Evolução Temporal")
    
    # Simula dados históricos
    dates = pd.date_range(start='2024-01-01', end='2024-11-15', freq='M')
    
    # Dados simulados de evolução
    disc_d_evolution = [70, 72, 71, 74, 75, 73, 75, 74, 76, 75, 75][:len(dates)]
    disc_i_evolution = [40, 42, 45, 44, 45, 46, 45, 44, 45, 45, 45][:len(dates)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=disc_d_evolution,
        mode='lines+markers',
        name='Dominância',
        line=dict(color='#ff6b6b', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=disc_i_evolution,
        mode='lines+markers',
        name='Influência',
        line=dict(color='#4ecdc4', width=3)
    ))
    
    fig.update_layout(
        title="Evolução do Perfil DISC ao Longo do Tempo",
        xaxis_title="Data",
        yaxis_title="Score DISC",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Análise de mudanças
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Mudanças Significativas")
        st.write("📈 **Dominância**: +5% nos últimos 6 meses")
        st.write("📊 **Influência**: Estável (variação < 3%)")
        st.write("📉 **Estabilidade**: -2% (mais flexível)")
    
    with col2:
        st.markdown("#### 🎯 Estabilidade do Perfil")
        st.success("**Alta Estabilidade (92%)**")
        st.write("Seu perfil tem se mantido consistente, indicando maturidade e autoconhecimento.")

with tab4:
    st.markdown("### 🎯 Benchmarks Populacionais")
    
    comparison_group = st.selectbox(
        "Comparar com:",
        ["População Geral", "Profissionais de Tecnologia", "Líderes Executivos", "Sua Faixa Etária"]
    )
    
    # Dados de comparação simulados
    your_scores = [75, 45, 30, 60]  # DISC
    if comparison_group == "População Geral":
        benchmark_scores = [25, 25, 25, 25]
    elif comparison_group == "Profissionais de Tecnologia":
        benchmark_scores = [35, 20, 20, 45]
    elif comparison_group == "Líderes Executivos":
        benchmark_scores = [65, 40, 15, 35]
    else:  # Faixa Etária
        benchmark_scores = [30, 30, 25, 35]
    
    # Gráfico de comparação
    categories = ['Dominância', 'Influência', 'Estabilidade', 'Conformidade']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Você',
        x=categories,
        y=your_scores,
        marker_color='#8ab4f8'
    ))
    
    fig.add_trace(go.Bar(
        name=comparison_group,
        x=categories,
        y=benchmark_scores,
        marker_color='rgba(168, 199, 250, 0.6)'
    ))
    
    fig.update_layout(
        title=f"Comparação: Você vs {comparison_group}",
        yaxis_title="Score DISC",
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights de posicionamento
    st.markdown("#### 💡 Insights de Posicionamento")
    
    if comparison_group == "Líderes Executivos":
        st.info("""
        🎯 **Compatibilidade com Liderança Executiva: 85%**
        
        Seu perfil está muito alinhado com líderes executivos, especialmente em:
        • Dominância (similar aos top performers)
        • Orientação para resultados
        • Capacidade de tomar decisões difíceis
        """)
    else:
        st.info(f"""
        📊 **Posicionamento vs {comparison_group}**
        
        Você se destaca em Dominância e Conformidade, indicando um perfil de:
        • Liderança natural
        • Foco em qualidade
        • Orientação para resultados
        """)

# Sidebar com ações
with st.sidebar:
    st.markdown("### 🛠️ Ações")
    
    if st.button("📄 Gerar Relatório PDF", use_container_width=True):
        st.success("Relatório gerado! (funcionalidade em desenvolvimento)")
    
    if st.button("📊 Exportar Dados", use_container_width=True):
        # Simula exportação
        data = {
            'Dimensão': ['DISC_D', 'DISC_I', 'DISC_S', 'DISC_C'],
            'Score': [75, 45, 30, 60],
            'Data': ['2024-11-15'] * 4
        }
        df = pd.DataFrame(data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name="neuromap_dados.csv",
            mime="text/csv"
        )
    
    if st.button("🔄 Nova Avaliação", use_container_width=True):
        st.switch_page("pages/2_📝_Avaliacao.py")
    
    st.markdown("---")
    st.markdown("### 📈 Estatísticas")
    st.metric("Avaliações Feitas", "3")
    st.metric("Dias Consecutivos", "5")
    st.metric("Melhoria Geral", "+12%")
