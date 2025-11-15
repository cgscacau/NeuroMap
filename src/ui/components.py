import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
import pandas as pd
from ..core.models import PersonalityScores, UserAssessment

class MetricsCards:
    """Componentes de cards de métricas reutilizáveis"""
    
    @staticmethod
    def personality_metric_card(
        title: str,
        value: str,
        delta: Optional[str] = None,
        delta_color: str = "normal",
        help_text: Optional[str] = None,
        icon: str = "📊"
    ) -> None:
        """Card de métrica personalizado para personalidade"""
        
        metric_html = f"""
        <div style='
            background: linear-gradient(135deg, #1e2a44 0%, #2d3748 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid #8ab4f8;
            margin: 0.5rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        '>
            <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                <span style='font-size: 1.5rem; margin-right: 0.5rem;'>{icon}</span>
                <h3 style='color: #a8c7fa; margin: 0; font-size: 0.9rem; text-transform: uppercase;'>
                    {title}
                </h3>
            </div>
            <div style='color: #ffffff; font-size: 2rem; font-weight: bold; margin: 0.5rem 0;'>
                {value}
            </div>
        """
        
        if delta:
            delta_colors = {
                "normal": "#4ade80",
                "inverse": "#f87171", 
                "off": "#94a3b8"
            }
            color = delta_colors.get(delta_color, "#4ade80")
            
            metric_html += f"""
            <div style='color: {color}; font-size: 0.8rem; font-weight: 500;'>
                {delta}
            </div>
            """
        
        if help_text:
            metric_html += f"""
            <div style='color: #94a3b8; font-size: 0.7rem; margin-top: 0.5rem;'>
                {help_text}
            </div>
            """
        
        metric_html += "</div>"
        
        st.markdown(metric_html, unsafe_allow_html=True)
    
    @staticmethod
    def comparison_card(
        title: str,
        user_value: float,
        benchmark_value: float,
        unit: str = "%",
        higher_is_better: bool = True
    ) -> None:
        """Card de comparação com benchmark"""
        
        difference = user_value - benchmark_value
        percentage_diff = (difference / benchmark_value * 100) if benchmark_value != 0 else 0
        
        # Determina cor baseada na comparação
        if higher_is_better:
            color = "#4ade80" if difference >= 0 else "#f87171"
            icon = "📈" if difference >= 0 else "📉"
        else:
            color = "#f87171" if difference >= 0 else "#4ade80"
            icon = "📉" if difference >= 0 else "📈"
        
        comparison_html = f"""
        <div style='
            background: #1a202c;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #2d3748;
            margin: 0.5rem 0;
        '>
            <h4 style='color: #a8c7fa; margin: 0 0 1rem 0; font-size: 0.9rem;'>
                {title}
            </h4>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <div style='color: #ffffff; font-size: 1.5rem; font-weight: bold;'>
                        {user_value:.1f}{unit}
                    </div>
                    <div style='color: #94a3b8; font-size: 0.8rem;'>
                        Benchmark: {benchmark_value:.1f}{unit}
                    </div>
                </div>
                <div style='text-align: right;'>
                    <div style='color: {color}; font-size: 1.2rem;'>
                        {icon}
                    </div>
                    <div style='color: {color}; font-size: 0.8rem; font-weight: bold;'>
                        {percentage_diff:+.1f}%
                    </div>
                </div>
            </div>
        </div>
        """
        
        st.markdown(comparison_html, unsafe_allow_html=True)

class InteractiveCharts:
    """Componentes de gráficos interativos avançados"""
    
    @staticmethod
    def personality_radar_with_controls(
        scores: PersonalityScores,
        comparison_data: Optional[Dict] = None,
        show_controls: bool = True
    ) -> go.Figure:
        """Gráfico radar com controles interativos"""
        
        if show_controls:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                show_comparison = st.checkbox("Mostrar Comparação", value=bool(comparison_data))
            
            with col2:
                chart_style = st.selectbox("Estilo", ["Preenchido", "Apenas Linhas", "Pontos"])
            
            with col3:
                color_scheme = st.selectbox("Cores", ["Padrão", "Vibrante", "Pastel"])
        else:
            show_comparison = bool(comparison_data)
            chart_style = "Preenchido"
            color_scheme = "Padrão"
        
        # Configurações de cor
        color_schemes = {
            "Padrão": {"primary": "#8ab4f8", "secondary": "#a8c7fa"},
            "Vibrante": {"primary": "#ff6b6b", "secondary": "#4ecdc4"},
            "Pastel": {"primary": "#ffd93d", "secondary": "#6c5ce7"}
        }
        
        colors = color_schemes[color_scheme]
        
        # Dados do radar
        dimensions = ['Dominância', 'Influência', 'Estabilidade', 'Conformidade']
        user_values = [
            scores.disc.get('DISC_D', 0),
            scores.disc.get('DISC_I', 0),
            scores.disc.get('DISC_S', 0),
            scores.disc.get('DISC_C', 0)
        ]
        
        fig = go.Figure()
        
        # Configurações baseadas no estilo
        fill_config = 'toself' if chart_style == "Preenchido" else None
        mode_config = 'lines+markers' if chart_style != "Apenas Linhas" else 'lines'
        
        # Linha do usuário
        fig.add_trace(go.Scatterpolar(
            r=user_values + [user_values[0]],
            theta=dimensions + [dimensions[0]],
            fill=fill_config,
            name='Seu Perfil',
            line_color=colors["primary"],
            fillcolor=f"rgba(138, 180, 248, 0.3)" if chart_style == "Preenchido" else None,
            mode=mode_config
        ))
        
        # Linha de comparação
        if show_comparison and comparison_data:
            comparison_values = [
                comparison_data.get('D', 25),
                comparison_data.get('I', 25),
                comparison_data.get('S', 25),
                comparison_data.get('C', 25)
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=comparison_values + [comparison_values[0]],
                theta=dimensions + [dimensions[0]],
                fill=None,
                name='Benchmark',
                line=dict(color=colors["secondary"], dash='dash'),
                mode='lines'
            ))
        
        # Layout personalizado
        fig.update_layout(
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='rgba(255,255,255,0.2)',
                    linecolor='rgba(255,255,255,0.3)',
                    tickfont=dict(color='white', size=10)
                ),
                angularaxis=dict(
                    gridcolor='rgba(255,255,255,0.2)',
                    linecolor='rgba(255,255,255,0.3)',
                    tickfont=dict(color='white', size=12)
                )
            ),
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    @staticmethod
    def evolution_timeline_advanced(
        assessments: List[UserAssessment],
        selected_dimensions: List[str] = None
    ) -> go.Figure:
        """Timeline de evolução com seleção de dimensões"""
        
        if len(assessments) < 2:
            st.info("Dados insuficientes para análise temporal")
            return go.Figure()
        
        # Controles interativos
        col1, col2, col3 = st.columns(3)
        
        with col1:
            available_dimensions = [
                "DISC_D", "DISC_I", "DISC_S", "DISC_C",
                "B5_O", "B5_C", "B5_E", "B5_A", "B5_N"
            ]
            
            if not selected_dimensions:
                selected_dimensions = st.multiselect(
                    "Dimensões para análise:",
                    available_dimensions,
                    default=["DISC_D", "DISC_I", "B5_O", "B5_C"]
                )
        
        with col2:
            time_range = st.selectbox(
                "Período:",
                ["Todos", "Últimos 6 meses", "Último ano", "Últimos 2 anos"]
            )
        
        with col3:
            show_trend_lines = st.checkbox("Linhas de tendência", value=True)
        
        # Filtra dados por período
        if time_range != "Todos":
            cutoff_months = {
                "Últimos 6 meses": 6,
                "Último ano": 12,
                "Últimos 2 anos": 24
            }
            
            cutoff_date = datetime.now() - timedelta(days=cutoff_months[time_range] * 30)
            assessments = [a for a in assessments if a.timestamp >= cutoff_date]
        
        # Ordena por data
        assessments = sorted(assessments, key=lambda x: x.timestamp)
        
        fig = go.Figure()
        
        colors = px.colors.qualitative.Set3
        
        # Adiciona linha para cada dimensão selecionada
        for i, dimension in enumerate(selected_dimensions):
            values = []
            dates = []
            
            for assessment in assessments:
                if dimension.startswith('DISC_'):
                    value = assessment.scores.disc.get(dimension, 0)
                elif dimension.startswith('B5_'):
                    value = assessment.scores.big_five.get(dimension, 0)
                else:
                    continue
                
                values.append(value)
                dates.append(assessment.timestamp)
            
            if values:
                # Linha principal
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=values,
                    mode='lines+markers',
                    name=dimension.replace('DISC_', '').replace('B5_', ''),
                    line=dict(color=colors[i % len(colors)], width=2),
                    marker=dict(size=8)
                ))
                
                # Linha de tendência
                if show_trend_lines and len(values) > 2:
                    # Regressão linear simples
                    x_numeric = [(d - dates[0]).days for d in dates]
                    z = np.polyfit(x_numeric, values, 1)
                    trend_line = np.poly1d(z)
                    
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=[trend_line(x) for x in x_numeric],
                        mode='lines',
                        name=f'Tendência {dimension.replace("DISC_", "").replace("B5_", "")}',
                        line=dict(
                            color=colors[i % len(colors)],
                            width=1,
                            dash='dash'
                        ),
                        opacity=0.6,
                        showlegend=False
                    ))
        
        # Layout
        fig.update_layout(
            title="Evolução Temporal do Perfil",
            xaxis_title="Data",
            yaxis_title="Score",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_xaxes(
            gridcolor='rgba(255,255,255,0.1)',
            linecolor='rgba(255,255,255,0.2)'
        )
        
        fig.update_yaxes(
            gridcolor='rgba(255,255,255,0.1)',
            linecolor='rgba(255,255,255,0.2)'
        )
        
        return fig

class FormComponents:
    """Componentes de formulário avançados"""
    
    @staticmethod
    def likert_scale_question(
        question_id: str,
        question_text: str,
        current_value: int = 3,
        scale_labels: Dict[int, str] = None,
        help_text: str = None,
        required: bool = True
    ) -> int:
        """Componente de escala Likert customizado"""
        
        if not scale_labels:
            scale_labels = {
                1: "Discordo totalmente",
                2: "Discordo parcialmente",
                3: "Neutro",
                4: "Concordo parcialmente", 
                5: "Concordo totalmente"
            }
        
        # Container da questão
        with st.container():
            # Título da questão
            question_html = f"""
            <div style='
                background: #1a202c;
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #8ab4f8;
                margin: 1rem 0;
            '>
                <h4 style='color: #ffffff; margin: 0 0 1rem 0;'>
                    {question_text}
                    {'<span style="color: #f87171;">*</span>' if required else ''}
                </h4>
            """
            
            if help_text:
                question_html += f"""
                <p style='color: #94a3b8; font-size: 0.9rem; margin: 0 0 1rem 0;'>
                    {help_text}
                </p>
                """
            
            question_html += "</div>"
            
            st.markdown(question_html, unsafe_allow_html=True)
            
            # Escala visual
            cols = st.columns(5)
            
            selected_value = current_value
            
            for i, (value, label) in enumerate(scale_labels.items(), 1):
                with cols[i-1]:
                    # Botão visual da escala
                    is_selected = (value == current_value)
                    
                    button_style = f"""
                    <div style='
                        background: {"#8ab4f8" if is_selected else "#2d3748"};
                        color: {"#000000" if is_selected else "#ffffff"};
                        padding: 0.5rem;
                        border-radius: 8px;
                        text-align: center;
                        cursor: pointer;
                        border: 2px solid {"#8ab4f8" if is_selected else "transparent"};
                        margin: 0.2rem 0;
                        font-weight: {"bold" if is_selected else "normal"};
                        transition: all 0.3s ease;
                    '>
                        <div style='font-size: 1.2rem; margin-bottom: 0.2rem;'>
                            {value}
                        </div>
                        <div style='font-size: 0.7rem;'>
                            {label}
                        </div>
                    </div>
                    """
                    
                    if st.button(f"", key=f"{question_id}_{value}", help=label):
                        selected_value = value
                    
                    st.markdown(button_style, unsafe_allow_html=True)
            
            # Slider como alternativa
            st.markdown("**Ou use o controle deslizante:**")
            slider_value = st.slider(
                "Resposta",
                min_value=1,
                max_value=5,
                value=selected_value,
                key=f"{question_id}_slider",
                label_visibility="collapsed"
            )
            
            return slider_value
    
    @staticmethod
    def progress_indicator(
        current_step: int,
        total_steps: int,
        step_names: List[str] = None,
        show_percentage: bool = True
    ) -> None:
        """Indicador de progresso visual"""
        
        progress_percentage = (current_step / total_steps) * 100
        
        # Barra de progresso principal
        st.progress(progress_percentage / 100)
        
        # Informações textuais
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Passo {current_step} de {total_steps}**")
        
        with col2:
            if show_percentage:
                st.write(f"**{progress_percentage:.1f}% concluído**")
        
        # Indicador visual de passos
        if step_names and len(step_names) == total_steps:
            steps_html = "<div style='display: flex; justify-content: space-between; margin: 1rem 0;'>"
            
            for i, step_name in enumerate(step_names, 1):
                is_current = (i == current_step)
                is_completed = (i < current_step)
                
                if is_completed:
                    color = "#4ade80"
                    icon = "✅"
                elif is_current:
                    color = "#8ab4f8"
                    icon = "🔄"
                else:
                    color = "#6b7280"
                    icon = "⭕"
                
                steps_html += f"""
                <div style='
                    text-align: center;
                    color: {color};
                    font-size: 0.8rem;
                    flex: 1;
                '>
                    <div style='font-size: 1.2rem; margin-bottom: 0.2rem;'>
                        {icon}
                    </div>
                    <div style='font-weight: {"bold" if is_current else "normal"};'>
                        {step_name}
                    </div>
                </div>
                """
            
            steps_html += "</div>"
            st.markdown(steps_html, unsafe_allow_html=True)

class NotificationSystem:
    """Sistema de notificações e alertas"""
    
    @staticmethod
    def success_notification(
        title: str,
        message: str,
        action_button: str = None,
        action_callback: Callable = None
    ) -> None:
        """Notificação de sucesso customizada"""
        
        notification_html = f"""
        <div style='
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(16, 185, 129, 0.3);
        '>
            <div style='display: flex; align-items: center;'>
                <span style='font-size: 1.5rem; margin-right: 0.5rem;'>✅</span>
                <div>
                    <h4 style='margin: 0; font-size: 1.1rem;'>{title}</h4>
                    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>{message}</p>
                </div>
            </div>
        </div>
        """
        
        st.markdown(notification_html, unsafe_allow_html=True)
        
        if action_button and action_callback:
            if st.button(action_button, key=f"action_{hash(title)}"):
                action_callback()
    
    @staticmethod
    def warning_notification(
        title: str,
        message: str,
        dismissible: bool = True
    ) -> bool:
        """Notificação de aviso"""
        
        dismiss_key = f"dismiss_{hash(title + message)}"
        
        if dismissible and st.session_state.get(dismiss_key, False):
            return False
        
        notification_html = f"""
        <div style='
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(245, 158, 11, 0.3);
        '>
            <div style='display: flex; align-items: center; justify-content: space-between;'>
                <div style='display: flex; align-items: center;'>
                    <span style='font-size: 1.5rem; margin-right: 0.5rem;'>⚠️</span>
                    <div>
                        <h4 style='margin: 0; font-size: 1.1rem;'>{title}</h4>
                        <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>{message}</p>
                    </div>
                </div>
        """
        
        if dismissible:
            notification_html += """
                <button onclick='this.parentElement.parentElement.style.display="none"'
                        style='
                            background: rgba(255,255,255,0.2);
                            border: none;
                            color: white;
                            padding: 0.5rem;
                            border-radius: 4px;
                            cursor: pointer;
                        '>
                    ✕
                </button>
            """
        
        notification_html += """
            </div>
        </div>
        """
        
        st.markdown(notification_html, unsafe_allow_html=True)
        
        if dismissible:
            col1, col2, col3 = st.columns([4, 1, 1])
            with col3:
                if st.button("Dispensar", key=dismiss_key):
                    st.session_state[dismiss_key] = True
                    st.rerun()
        
        return True
    
    @staticmethod
    def info_tooltip(
        text: str,
        tooltip_content: str,
        position: str = "top"
    ) -> None:
        """Tooltip informativo"""
        
        tooltip_html = f"""
        <div style='display: inline-block; position: relative;'>
            <span style='
                color: #8ab4f8;
                cursor: help;
                border-bottom: 1px dotted #8ab4f8;
            ' title='{tooltip_content}'>
                {text} ℹ️
            </span>
        </div>
        """
        
        st.markdown(tooltip_html, unsafe_allow_html=True)

class DataExportComponents:
    """Componentes para exportação de dados"""
    
    @staticmethod
    def export_button_group(
        data: Any,
        filename_base: str,
        formats: List[str] = None
    ) -> None:
        """Grupo de botões de exportação"""
        
        if not formats:
            formats = ["CSV", "JSON", "Excel"]
        
        st.markdown("### 📤 Exportar Dados")
        
        cols = st.columns(len(formats))
        
        for i, format_type in enumerate(formats):
            with cols[i]:
                if format_type == "CSV" and hasattr(data, 'to_csv'):
                    csv_data = data.to_csv(index=False)
                    st.download_button(
                        f"📄 {format_type}",
                        data=csv_data,
                        file_name=f"{filename_base}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                elif format_type == "JSON":
                    if hasattr(data, 'to_json'):
                        json_data = data.to_json(orient='records', indent=2)
                    else:
                        import json
                        json_data = json.dumps(data, indent=2, default=str)
                    
                    st.download_button(
                        f"📋 {format_type}",
                        data=json_data,
                        file_name=f"{filename_base}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                elif format_type == "Excel" and hasattr(data, 'to_excel'):
                    buffer = io.BytesIO()
                    data.to_excel(buffer, index=False)
                    
                    st.download_button(
                        f"📊 {format_type}",
                        data=buffer.getvalue(),
                        file_name=f"{filename_base}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

# Utilitários de layout
class LayoutUtils:
    """Utilitários para layout e organização"""
    
    @staticmethod
    def centered_container(content_func: Callable, max_width: str = "800px") -> None:
        """Container centralizado com largura máxima"""
        
        st.markdown(f"""
        <div style='
            max-width: {max_width};
            margin: 0 auto;
            padding: 0 1rem;
        '>
        """, unsafe_allow_html=True)
        
        content_func()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    @staticmethod
    def sidebar_with_logo(logo_url: str = None, title: str = "NeuroMap") -> None:
        """Sidebar customizada com logo"""
        
        with st.sidebar:
            if logo_url:
                st.image(logo_url, width=200)
            else:
                st.markdown(f"""
                <div style='text-align: center; padding: 1rem 0;'>
                    <h1 style='color: #8ab4f8; font-size: 2rem;'>
                        🧠 {title}
                    </h1>
                </div>
                """, unsafe_allow_html=True)
    
    @staticmethod
    def floating_action_button(
        icon: str,
        action_callback: Callable,
        position: str = "bottom-right",
        color: str = "#8ab4f8"
    ) -> None:
        """Botão de ação flutuante"""
        
        positions = {
            "bottom-right": "bottom: 20px; right: 20px;",
            "bottom-left": "bottom: 20px; left: 20px;",
            "top-right": "top: 20px; right: 20px;",
            "top-left": "top: 20px; left: 20px;"
        }
        
        position_style = positions.get(position, positions["bottom-right"])
        
        button_html = f"""
        <div style='
            position: fixed;
            {position_style}
            z-index: 1000;
            background: {color};
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            cursor: pointer;
            transition: transform 0.2s ease;
        '
        onmouseover='this.style.transform="scale(1.1)"'
        onmouseout='this.style.transform="scale(1)"'
        onclick='window.streamlitActionButton()'>
            {icon}
        </div>
        
        <script>
        window.streamlitActionButton = function() {{
            // Trigger Streamlit callback
            window.parent.postMessage({{
                type: 'streamlit:actionButton',
                data: 'clicked'
            }}, '*');
        }};
        </script>
        """
        
        st.markdown(button_html, unsafe_allow_html=True)
        
        # Detecta clique (implementação simplificada)
        if st.session_state.get('floating_button_clicked', False):
            action_callback()
            st.session_state.floating_button_clicked = False
