import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from ..core.models import PersonalityScores, UserAssessment

class PersonalityVisualizer:
    """Classe para criar visualizações interativas dos perfis"""
    
    def __init__(self):
        self.color_scheme = {
            'primary': '#8ab4f8',
            'secondary': '#a8c7fa', 
            'background': '#0b0f17',
            'surface': '#121826',
            'disc_colors': {
                'D': '#ff6b6b',  # Vermelho - Dominância
                'I': '#4ecdc4',  # Turquesa - Influência  
                'S': '#45b7d1',  # Azul - Estabilidade
                'C': '#96ceb4'   # Verde - Conformidade
            },
            'b5_colors': {
                'O': '#ff9f43',  # Laranja - Abertura
                'C': '#6c5ce7',  # Roxo - Conscienciosidade
                'E': '#fd79a8',  # Rosa - Extroversão
                'A': '#00b894',  # Verde - Amabilidade
                'N': '#e17055'   # Coral - Neuroticismo
            }
        }
    
    def create_disc_radar_chart(self, scores: PersonalityScores) -> go.Figure:
        """Cria gráfico radar para DISC com comparação normativa"""
        
        dimensions = ['Dominância', 'Influência', 'Estabilidade', 'Conformidade']
        user_values = [
            scores.disc.get('DISC_D', 0),
            scores.disc.get('DISC_I', 0), 
            scores.disc.get('DISC_S', 0),
            scores.disc.get('DISC_C', 0)
        ]
        
        # Dados normativos (população geral)
        norm_values = [25, 25, 25, 25]  # Distribuição equilibrada
        
        fig = go.Figure()
        
        # Linha do usuário
        fig.add_trace(go.Scatterpolar(
            r=user_values + [user_values[0]],  # Fecha o polígono
            theta=dimensions + [dimensions[0]],
            fill='toself',
            name='Seu Perfil',
            line_color=self.color_scheme['primary'],
            fillcolor=f"rgba(138, 180, 248, 0.3)"
        ))
        
        # Linha normativa
        fig.add_trace(go.Scatterpolar(
            r=norm_values + [norm_values[0]],
            theta=dimensions + [dimensions[0]],
            fill=None,
            name='Média Populacional',
            line=dict(color='gray', dash='dash'),
            showlegend=True
        ))
        
        fig.update_layout(
            polar=dict(
                bgcolor=self.color_scheme['surface'],
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='rgba(255,255,255,0.1)',
                    linecolor='rgba(255,255,255,0.2)'
                ),
                angularaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    linecolor='rgba(255,255,255,0.2)'
                )
            ),
            showlegend=True,
            title={
                'text': "Perfil DISC - Radar Comparativo",
                'x': 0.5,
                'font': {'size': 18, 'color': self.color_scheme['primary']}
            },
            paper_bgcolor=self.color_scheme['background'],
            plot_bgcolor=self.color_scheme['background'],
            font=dict(color='white')
        )
        
        return fig
    
    def create_big_five_bars(self, scores: PersonalityScores) -> go.Figure:
        """Cria gráfico de barras para Big Five com percentis"""
        
        traits = ['Abertura', 'Conscienciosidade', 'Extroversão', 'Amabilidade', 'Neuroticismo']
        trait_keys = ['B5_O', 'B5_C', 'B5_E', 'B5_A', 'B5_N']
        values = [scores.big_five.get(key, 0) for key in trait_keys]
        colors = [self.color_scheme['b5_colors'][key.split('_')[1]] for key in trait_keys]
        
        # Interpretação dos percentis
        interpretations = []
        for value in values:
            if value >= 70:
                interpretations.append("Alto")
            elif value >= 30:
                interpretations.append("Médio")
            else:
                interpretations.append("Baixo")
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=traits,
            y=values,
            marker_color=colors,
            text=[f"{v:.0f}%<br>{interp}" for v, interp in zip(values, interpretations)],
            textposition='auto',
            textfont=dict(color='white', size=12),
            hovertemplate='<b>%{x}</b><br>Percentil: %{y:.0f}%<br>Nível: %{text}<extra></extra>'
        ))
        
        # Linha de referência média
        fig.add_hline(
            y=50, 
            line_dash="dash", 
            line_color="gray",
            annotation_text="Média Populacional (50%)",
            annotation_position="top right"
        )
        
        fig.update_layout(
            title={
                'text': "Big Five - Percentis Populacionais",
                'x': 0.5,
                'font': {'size': 18, 'color': self.color_scheme['primary']}
            },
            xaxis=dict(
                title="Traços de Personalidade",
                gridcolor='rgba(255,255,255,0.1)',
                color='white'
            ),
            yaxis=dict(
                title="Percentil (%)",
                range=[0, 100],
                gridcolor='rgba(255,255,255,0.1)',
                color='white'
            ),
            paper_bgcolor=self.color_scheme['background'],
            plot_bgcolor=self.color_scheme['background'],
            font=dict(color='white'),
            showlegend=False
        )
        
        return fig
    
    def create_mbti_preference_chart(self, scores: PersonalityScores) -> go.Figure:
        """Cria visualização das preferências MBTI"""
        
        # Calcula intensidade das preferências
        preferences = {
            'E vs I': scores.mbti_preferences.get('MBTI_E', 0) - scores.mbti_preferences.get('MBTI_I', 0),
            'S vs N': scores.mbti_preferences.get('MBTI_S', 0) - scores.mbti_preferences.get('MBTI_N', 0),
            'T vs F': scores.mbti_preferences.get('MBTI_T', 0) - scores.mbti_preferences.get('MBTI_F', 0),
            'J vs P': scores.mbti_preferences.get('MBTI_J', 0) - scores.mbti_preferences.get('MBTI_P', 0)
        }
        
        # Converte para escala visual (-100 a 100)
        normalized_prefs = {}
        for key, value in preferences.items():
            # Normaliza baseado no range típico dos scores
            normalized = max(-100, min(100, value * 10))  # Ajuste do fator conforme necessário
            normalized_prefs[key] = normalized
        
        fig = go.Figure()
        
        dimensions = list(normalized_prefs.keys())
        values = list(normalized_prefs.values())
        
        # Cores baseadas na direção da preferência
        colors = []
        for val in values:
            if val > 20:
                colors.append('#4ecdc4')  # Turquesa para preferência clara
            elif val < -20:
                colors.append('#ff6b6b')  # Vermelho para preferência oposta clara
            else:
                colors.append('#ffd93d')  # Amarelo para preferência leve
        
        fig.add_trace(go.Bar(
            y=dimensions,
            x=values,
            orientation='h',
            marker_color=colors,
            text=[f"{scores.mbti_type[i]}" for i in range(4)],
            textposition='auto',
            textfont=dict(color='white', size=14, family='Arial Black')
        ))
        
        # Linha central
        fig.add_vline(x=0, line_color="white", line_width=2)
        
        fig.update_layout(
            title={
                'text': f"Preferências MBTI - Tipo {scores.mbti_type}",
                'x': 0.5,
                'font': {'size': 18, 'color': self.color_scheme['primary']}
            },
            xaxis=dict(
                title="Intensidade da Preferência",
                range=[-100, 100],
                gridcolor='rgba(255,255,255,0.1)',
                color='white',
                tickvals=[-75, -50, -25, 0, 25, 50, 75],
                ticktext=['Forte', 'Moderada', 'Leve', 'Neutro', 'Leve', 'Moderada', 'Forte']
            ),
            yaxis=dict(color='white'),
            paper_bgcolor=self.color_scheme['background'],
            plot_bgcolor=self.color_scheme['background'],
            font=dict(color='white'),
            showlegend=False,
            height=400
        )
        
        return fig
    
    def create_personality_blend_sunburst(self, scores: PersonalityScores) -> go.Figure:
        """Cria gráfico sunburst mostrando a combinação de traços"""
        
        # Prepara dados hierárquicos
        labels = ['Personalidade']
        parents = ['']
        values = [100]
        colors = [self.color_scheme['primary']]
        
        # Nível DISC
        disc_total = sum(scores.disc.values())
        for key, value in scores.disc.items():
            label = key.replace('DISC_', '')
            labels.append(f'DISC {label}')
            parents.append('Personalidade')
            values.append(value)
            colors.append(self.color_scheme['disc_colors'][label])
        
        # Nível Big Five (principais traços)
        b5_high = {k: v for k, v in scores.big_five.items() if v > 60}
        for key, value in b5_high.items():
            trait_name = {
                'B5_O': 'Abertura',
                'B5_C': 'Conscienciosidade', 
                'B5_E': 'Extroversão',
                'B5_A': 'Amabilidade',
                'B5_N': 'Neuroticismo'
            }[key]
            
            labels.append(trait_name)
            parents.append('Personalidade')
            values.append(value / 2)  # Reduz para balancear visualmente
            colors.append(self.color_scheme['b5_colors'][key.split('_')[1]])
        
        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(colors=colors),
            hovertemplate='<b>%{label}</b><br>Intensidade: %{value:.0f}%<extra></extra>',
            maxdepth=2
        ))
        
        fig.update_layout(
            title={
                'text': "Composição da Personalidade",
                'x': 0.5,
                'font': {'size': 18, 'color': self.color_scheme['primary']}
            },
            paper_bgcolor=self.color_scheme['background'],
            font=dict(color='white', size=12)
        )
        
        return fig
    
    def create_confidence_indicators(self, scores: PersonalityScores) -> go.Figure:
        """Cria indicadores visuais de confiança dos resultados"""
        
        if not scores.confidence_scores:
            return None
        
        # Agrupa por categoria
        disc_conf = [scores.confidence_scores.get(f'DISC_{d}', 0.5) for d in ['D', 'I', 'S', 'C']]
        b5_conf = [scores.confidence_scores.get(f'B5_{t}', 0.5) for t in ['O', 'C', 'E', 'A', 'N']]
        mbti_conf = [scores.confidence_scores.get(f'MBTI_{p}', 0.5) for p in ['E', 'I', 'S', 'N', 'T', 'F', 'J', 'P']]
        
        categories = ['DISC', 'Big Five', 'MBTI']
        avg_confidences = [
            np.mean(disc_conf),
            np.mean(b5_conf), 
            np.mean(mbti_conf)
        ]
        
        # Cores baseadas no nível de confiança
        colors = []
        for conf in avg_confidences:
            if conf >= 0.8:
                colors.append('#00b894')  # Verde - Alta confiança
            elif conf >= 0.6:
                colors.append('#ffd93d')  # Amarelo - Média confiança
            else:
                colors.append('#ff6b6b')  # Vermelho - Baixa confiança
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=categories,
            y=[c * 100 for c in avg_confidences],
            marker_color=colors,
            text=[f"{c:.0%}" for c in avg_confidences],
            textposition='auto',
            textfont=dict(color='white', size=12)
        ))
        
        # Linha de confiança mínima recomendada
        fig.add_hline(
            y=70,
            line_dash="dash",
            line_color="orange",
            annotation_text="Confiança Mínima Recomendada",
            annotation_position="top right"
        )
        
        fig.update_layout(
            title={
                'text': "Confiabilidade dos Resultados",
                'x': 0.5,
                'font': {'size': 16, 'color': self.color_scheme['primary']}
            },
            xaxis=dict(title="Dimensões", color='white'),
            yaxis=dict(
                title="Confiabilidade (%)",
                range=[0, 100],
                color='white'
            ),
            paper_bgcolor=self.color_scheme['background'],
            plot_bgcolor=self.color_scheme['background'],
            font=dict(color='white'),
            showlegend=False,
            height=300
        )
        
        return fig
    
    def create_evolution_timeline(self, assessments: List[UserAssessment]) -> Optional[go.Figure]:
        """Cria timeline de evolução do perfil ao longo do tempo"""
        
        if len(assessments) < 2:
            return None
        
        # Ordena por timestamp
        sorted_assessments = sorted(assessments, key=lambda x: x.timestamp)
        
        dates = [a.timestamp.strftime('%Y-%m-%d') for a in sorted_assessments]
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('DISC Dominância', 'DISC Influência', 'Big Five Abertura', 'Big Five Conscienciosidade'),
            vertical_spacing=0.1
        )
        
        # DISC D evolution
        disc_d_values = [a.scores.disc.get('DISC_D', 0) for a in sorted_assessments]
        fig.add_trace(
            go.Scatter(x=dates, y=disc_d_values, mode='lines+markers', 
                      name='Dominância', line_color=self.color_scheme['disc_colors']['D']),
            row=1, col=1
        )
        
        # DISC I evolution  
        disc_i_values = [a.scores.disc.get('DISC_I', 0) for a in sorted_assessments]
        fig.add_trace(
            go.Scatter(x=dates, y=disc_i_values, mode='lines+markers',
                      name='Influência', line_color=self.color_scheme['disc_colors']['I']),
            row=1, col=2
        )
        
        # B5 O evolution
        b5_o_values = [a.scores.big_five.get('B5_O', 0) for a in sorted_assessments]
        fig.add_trace(
            go.Scatter(x=dates, y=b5_o_values, mode='lines+markers',
                      name='Abertura', line_color=self.color_scheme['b5_colors']['O']),
            row=2, col=1
        )
        
        # B5 C evolution
        b5_c_values = [a.scores.big_five.get('B5_C', 0) for a in sorted_assessments]
        fig.add_trace(
            go.Scatter(x=dates, y=b5_c_values, mode='lines+markers',
                      name='Conscienciosidade', line_color=self.color_scheme['b5_colors']['C']),
            row=2, col=2
        )
        
        fig.update_layout(
            title={
                'text': "Evolução do Perfil ao Longo do Tempo",
                'x': 0.5,
                'font': {'size': 18, 'color': self.color_scheme['primary']}
            },
            paper_bgcolor=self.color_scheme['background'],
            plot_bgcolor=self.color_scheme['background'],
            font=dict(color='white'),
            showlegend=False,
            height=600
        )
        
        # Update axes
        fig.update_xaxes(color='white', gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(color='white', gridcolor='rgba(255,255,255,0.1)', range=[0, 100])
        
        return fig

class DashboardComponents:
    """Componentes reutilizáveis para dashboard"""
    
    @staticmethod
    def personality_summary_card(scores: PersonalityScores) -> None:
        """Card resumo da personalidade"""
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dominant_disc, strength = scores.get_dominant_disc()
            st.metric(
                label="Estilo Dominante (DISC)",
                value=f"{dominant_disc}",
                delta=f"{strength:.0f}% de intensidade"
            )
        
        with col2:
            st.metric(
                label="Tipo MBTI",
                value=scores.mbti_type,
                delta="Baseado em preferências"
            )
        
        with col3:
            # Calcula "score de complexidade" baseado na variabilidade
            b5_values = list(scores.big_five.values())
            complexity = np.std(b5_values) if b5_values else 0
            complexity_level = "Alta" if complexity > 20 else "Média" if complexity > 10 else "Baixa"
            
            st.metric(
                label="Complexidade do Perfil",
                value=complexity_level,
                delta=f"σ = {complexity:.1f}"
            )
    
    @staticmethod
    def strengths_insights_card(insights: 'ProfileInsights') -> None:
        """Card com insights de pontos fortes"""
        
        st.markdown("### 🎯 Principais Forças")
        
        for i, strength in enumerate(insights.strengths[:4], 1):
            st.markdown(f"**{i}.** {strength}")
        
        if len(insights.strengths) > 4:
            with st.expander("Ver mais forças"):
                for i, strength in enumerate(insights.strengths[4:], 5):
                    st.markdown(f"**{i}.** {strength}")
    
    @staticmethod
    def development_recommendations_card(insights: 'ProfileInsights') -> None:
        """Card com recomendações de desenvolvimento"""
        
        st.markdown("### 📈 Recomendações de Crescimento")
        
        tabs = st.tabs(["🎯 Áreas de Foco", "💡 Ações Práticas", "🚨 Pontos de Atenção"])
        
        with tabs[0]:
            for area in insights.development_areas:
                st.markdown(f"• {area}")
        
        with tabs[1]:
            for rec in insights.growth_recommendations:
                st.markdown(f"✅ {rec}")
        
        with tabs[2]:
            for stress in insights.stress_indicators:
                st.markdown(f"⚠️ {stress}")
    
    @staticmethod
    def career_suggestions_card(insights: 'ProfileInsights') -> None:
        """Card com sugestões de carreira"""
        
        st.markdown("### 💼 Sugestões de Carreira")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Roles Recomendados:**")
            for career in insights.career_suggestions:
                st.markdown(f"• {career}")
        
        with col2:
            st.markdown("**Estilo de Comunicação:**")
            st.info(insights.communication_style)
            
            st.markdown("**Estilo de Liderança:**")
            st.info(insights.leadership_style)
