import io
import json
import base64
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict
import pandas as pd
from fpdf import FPDF
import plotly.graph_objects as go
import plotly.io as pio
from jinja2 import Template
import streamlit as st

from ..core.models import UserAssessment, PersonalityScores, ProfileInsights
from ..ui.visualizations import PersonalityVisualizer

class AdvancedReportGenerator:
    """Gerador avançado de relatórios com múltiplos formatos e personalização"""
    
    def __init__(self):
        self.visualizer = PersonalityVisualizer()
        self.templates = self._load_report_templates()
    
    def generate_comprehensive_report(
        self,
        assessment: UserAssessment,
        report_type: str = "executive",
        format: str = "pdf",
        customizations: Dict = None
    ) -> bytes:
        """Gera relatório abrangente baseado no tipo e formato especificados"""
        
        customizations = customizations or {}
        
        if format == "pdf":
            return self._generate_pdf_report(assessment, report_type, customizations)
        elif format == "html":
            return self._generate_html_report(assessment, report_type, customizations)
        elif format == "excel":
            return self._generate_excel_report(assessment, report_type, customizations)
        elif format == "powerpoint":
            return self._generate_powerpoint_report(assessment, report_type, customizations)
        else:
            raise ValueError(f"Formato não suportado: {format}")
    
    def _generate_pdf_report(
        self,
        assessment: UserAssessment,
        report_type: str,
        customizations: Dict
    ) -> bytes:
        """Gera relatório PDF profissional com gráficos integrados"""
        
        pdf = FPDF('P', 'mm', 'A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Configurações de fonte
        pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        pdf.set_font('DejaVu', '', 12)
        
        # Página de capa
        self._add_cover_page(pdf, assessment, report_type)
        
        # Sumário executivo
        if report_type in ["executive", "complete"]:
            self._add_executive_summary(pdf, assessment)
        
        # Análise DISC
        self._add_disc_analysis(pdf, assessment.scores)
        
        # Análise Big Five
        self._add_big_five_analysis(pdf, assessment.scores)
        
        # Análise MBTI
        self._add_mbti_analysis(pdf, assessment.scores)
        
        # Insights e recomendações
        if assessment.profile_insights:
            self._add_insights_section(pdf, assessment.profile_insights)
        
        # Seções adicionais baseadas no tipo
        if report_type == "complete":
            self._add_detailed_analysis(pdf, assessment)
            self._add_development_plan(pdf, assessment)
        
        elif report_type == "coaching":
            self._add_coaching_insights(pdf, assessment)
            self._add_action_plan(pdf, assessment)
        
        elif report_type == "team":
            self._add_team_dynamics(pdf, assessment)
            self._add_collaboration_tips(pdf, assessment)
        
        # Apêndices
        if customizations.get("include_methodology", True):
            self._add_methodology_appendix(pdf)
        
        # Converte para bytes
        return pdf.output(dest='S').encode('latin1')
    
    def _add_cover_page(self, pdf: FPDF, assessment: UserAssessment, report_type: str) -> None:
        """Adiciona página de capa profissional"""
        
        pdf.add_page()
        
        # Logo/Header (placeholder)
        pdf.set_font('DejaVu', 'B', 24)
        pdf.set_text_color(138, 180, 248)  # Cor azul do tema
        pdf.cell(0, 20, 'NeuroMap', ln=True, align='C')
        
        pdf.set_font('DejaVu', '', 16)
        pdf.set_text_color(168, 199, 250)
        pdf.cell(0, 10, 'Relatório de Personalidade Profissional', ln=True, align='C')
        
        # Espaço
        pdf.ln(30)
        
        # Título do relatório
        pdf.set_font('DejaVu', 'B', 20)
        pdf.set_text_color(0, 0, 0)
        
        report_titles = {
            "executive": "Relatório Executivo de Personalidade",
            "complete": "Análise Completa de Personalidade",
            "coaching": "Relatório para Coaching e Desenvolvimento",
            "team": "Perfil para Dinâmicas de Equipe"
        }
        
        title = report_titles.get(report_type, "Relatório de Personalidade")
        pdf.multi_cell(0, 12, title, align='C')
        
        # Informações do usuário
        pdf.ln(20)
        pdf.set_font('DejaVu', '', 14)
        
        user_info = [
            f"Data da Avaliação: {assessment.timestamp.strftime('%d/%m/%Y')}",
            f"Tipo MBTI: {assessment.scores.mbti_type}",
            f"Confiabilidade: {assessment.reliability_score:.0%}" if assessment.reliability_score else "",
            f"Tempo de Conclusão: {assessment.completion_time_minutes} minutos" if assessment.completion_time_minutes else ""
        ]
        
        for info in user_info:
            if info:  # Só adiciona se não estiver vazio
                pdf.cell(0, 8, info, ln=True, align='C')
        
        # Rodapé da capa
        pdf.set_y(-30)
        pdf.set_font('DejaVu', '', 10)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 5, 'Relatório Confidencial - Uso Pessoal e Profissional', ln=True, align='C')
        pdf.cell(0, 5, f'Gerado em {datetime.now().strftime("%d/%m/%Y às %H:%M")}', ln=True, align='C')
    
    def _add_executive_summary(self, pdf: FPDF, assessment: UserAssessment) -> None:
        """Adiciona sumário executivo"""
        
        pdf.add_page()
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, 'Sumário Executivo', ln=True)
        pdf.ln(5)
        
        # Perfil geral
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 8, 'Perfil Geral:', ln=True)
        
        pdf.set_font('DejaVu', '', 11)
        
        # Resumo do perfil
        dominant_disc, strength = assessment.scores.get_dominant_disc()
        summary_text = f"""
        Seu perfil apresenta predominância no estilo {dominant_disc} ({strength:.0f}%), 
        com tipo MBTI {assessment.scores.mbti_type}. Esta combinação indica uma personalidade 
        orientada para {self._get_style_orientation(dominant_disc, assessment.scores.mbti_type)}.
        """
        
        pdf.multi_cell(0, 6, summary_text.strip())
        pdf.ln(5)
        
        # Pontos fortes principais
        if assessment.profile_insights:
            pdf.set_font('DejaVu', 'B', 12)
            pdf.cell(0, 8, 'Principais Pontos Fortes:', ln=True)
            
            pdf.set_font('DejaVu', '', 11)
            for i, strength in enumerate(assessment.profile_insights.strengths[:3], 1):
                pdf.cell(0, 6, f"{i}. {strength}", ln=True)
            
            pdf.ln(5)
            
            # Áreas de desenvolvimento
            pdf.set_font('DejaVu', 'B', 12)
            pdf.cell(0, 8, 'Áreas de Desenvolvimento:', ln=True)
            
            pdf.set_font('DejaVu', '', 11)
            for i, area in enumerate(assessment.profile_insights.development_areas[:3], 1):
                pdf.cell(0, 6, f"{i}. {area}", ln=True)
    
    def _add_disc_analysis(self, pdf: FPDF, scores: PersonalityScores) -> None:
        """Adiciona análise DISC detalhada"""
        
        pdf.add_page()
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, 'Análise DISC', ln=True)
        pdf.ln(5)
        
        # Gráfico DISC (convertido para imagem)
        disc_chart = self.visualizer.create_disc_radar_chart(scores)
        chart_image = self._plotly_to_image(disc_chart)
        
        if chart_image:
            # Salva imagem temporariamente e adiciona ao PDF
            chart_path = f"/tmp/disc_chart_{datetime.now().timestamp()}.png"
            with open(chart_path, 'wb') as f:
                f.write(chart_image)
            pdf.image(chart_path, x=10, y=None, w=100)
            pdf.ln(80)
        
        # Interpretação dos scores
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 8, 'Interpretação dos Scores:', ln=True)
        pdf.ln(3)
        
        disc_interpretations = {
            'DISC_D': ('Dominância', 'Orientação para resultados, liderança e tomada de decisão rápida'),
            'DISC_I': ('Influência', 'Habilidade de comunicação, persuasão e relacionamento interpessoal'),
            'DISC_S': ('Estabilidade', 'Cooperação, paciência e trabalho em equipe consistente'),
            'DISC_C': ('Conformidade', 'Foco em qualidade, precisão e seguimento de padrões')
        }
        
        pdf.set_font('DejaVu', '', 11)
        for key, value in scores.disc.items():
            name, description = disc_interpretations[key]
            level = self._get_score_level(value)
            pdf.multi_cell(0, 6, f"{name} ({value:.0f}% - {level}): {description}")
            pdf.ln(2)
    
    def _add_big_five_analysis(self, pdf: FPDF, scores: PersonalityScores) -> None:
        """Adiciona análise Big Five"""
        
        pdf.add_page()
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, 'Análise Big Five', ln=True)
        pdf.ln(5)
        
        # Gráfico Big Five
        b5_chart = self.visualizer.create_big_five_bars(scores)
        chart_image = self._plotly_to_image(b5_chart)
        
        if chart_image:
            chart_path = f"/tmp/b5_chart_{datetime.now().timestamp()}.png"
            with open(chart_path, 'wb') as f:
                f.write(chart_image)
            pdf.image(chart_path, x=10, y=None, w=120)
            pdf.ln(90)
        
        # Interpretações detalhadas
        b5_details = {
            'B5_O': ('Abertura à Experiência', 'Criatividade, curiosidade intelectual e abertura para novas ideias'),
            'B5_C': ('Conscienciosidade', 'Organização, disciplina e orientação para objetivos'),
            'B5_E': ('Extroversão', 'Sociabilidade, assertividade e energia em interações sociais'),
            'B5_A': ('Amabilidade', 'Cooperação, empatia e consideração pelos outros'),
            'B5_N': ('Neuroticismo', 'Tendência a experienciar emoções negativas e estresse')
        }
        
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 8, 'Interpretação Detalhada:', ln=True)
        pdf.ln(3)
        
        pdf.set_font('DejaVu', '', 11)
        for key, value in scores.big_five.items():
            name, description = b5_details[key]
            percentile_level = self._get_percentile_interpretation(value)
            
            pdf.multi_cell(0, 6, f"{name} (Percentil {value:.0f}% - {percentile_level}): {description}")
            
            # Adiciona interpretação específica do nível
            interpretation = self._get_b5_level_interpretation(key, value)
            pdf.set_font('DejaVu', '', 10)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 5, f"   → {interpretation}")
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('DejaVu', '', 11)
            pdf.ln(3)
    
    def _add_mbti_analysis(self, pdf: FPDF, scores: PersonalityScores) -> None:
        """Adiciona análise MBTI"""
        
        pdf.add_page()
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, f'Análise MBTI - Tipo {scores.mbti_type}', ln=True)
        pdf.ln(5)
        
        # Descrição do tipo
        type_description = self._get_mbti_type_description(scores.mbti_type)
        pdf.set_font('DejaVu', '', 11)
        pdf.multi_cell(0, 6, type_description)
        pdf.ln(5)
        
        # Preferências detalhadas
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 8, 'Suas Preferências:', ln=True)
        pdf.ln(3)
        
        preferences = [
            ('E/I', 'Extroversão vs Introversão', 'Onde você foca sua energia'),
            ('S/N', 'Sensação vs Intuição', 'Como você processa informações'),
            ('T/F', 'Pensamento vs Sentimento', 'Como você toma decisões'),
            ('J/P', 'Julgamento vs Percepção', 'Como você se organiza')
        ]
        
        pdf.set_font('DejaVu', '', 11)
        for i, (pref_pair, name, description) in enumerate(preferences):
            preference = scores.mbti_type[i]
            pdf.cell(0, 6, f"{name}: {preference}", ln=True)
            pdf.set_font('DejaVu', '', 10)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 5, f"   {description}")
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('DejaVu', '', 11)
            pdf.ln(2)
    
    def _generate_html_report(
        self,
        assessment: UserAssessment,
        report_type: str,
        customizations: Dict
    ) -> bytes:
        """Gera relatório HTML interativo"""
        
        template_name = f"{report_type}_report.html"
        template = self.templates.get(template_name, self.templates['default_report.html'])
        
        # Prepara dados para o template
        context = {
            'assessment': assessment,
            'scores': assessment.scores,
            'insights': assessment.profile_insights,
            'generated_at': datetime.now(),
            'report_type': report_type,
            'customizations': customizations,
            'charts': self._generate_html_charts(assessment.scores)
        }
        
        # Renderiza template
        html_content = template.render(context)
        
        return html_content.encode('utf-8')
    
    def _generate_excel_report(
        self,
        assessment: UserAssessment,
        report_type: str,
        customizations: Dict
    ) -> bytes:
        """Gera relatório Excel com múltiplas abas"""
        
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            
            # Aba: Resumo
            summary_data = self._prepare_summary_data(assessment)
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Resumo', index=False)
            
            # Aba: Scores DISC
            disc_data = [
                {'Dimensão': k.replace('DISC_', ''), 'Score': v, 'Nível': self._get_score_level(v)}
                for k, v in assessment.scores.disc.items()
            ]
            disc_df = pd.DataFrame(disc_data)
            disc_df.to_excel(writer, sheet_name='DISC', index=False)
            
            # Aba: Big Five
            b5_data = [
                {'Traço': k.replace('B5_', ''), 'Percentil': v, 'Nível': self._get_percentile_interpretation(v)}
                for k, v in assessment.scores.big_five.items()
            ]
            b5_df = pd.DataFrame(b5_data)
            b5_df.to_excel(writer, sheet_name='Big Five', index=False)
            
            # Aba: MBTI
            mbti_data = [{
                'Tipo': assessment.scores.mbti_type,
                'Descrição': self._get_mbti_type_description(assessment.scores.mbti_type)
            }]
            mbti_df = pd.DataFrame(mbti_data)
            mbti_df.to_excel(writer, sheet_name='MBTI', index=False)
            
            # Aba: Insights (se disponível)
            if assessment.profile_insights:
                insights_data = {
                    'Pontos Fortes': assessment.profile_insights.strengths,
                    'Áreas de Desenvolvimento': assessment.profile_insights.development_areas,
                    'Sugestões de Carreira': assessment.profile_insights.career_suggestions
                }
                
                max_len = max(len(v) for v in insights_data.values())
                
                # Preenche listas menores com valores vazios
                for key, value_list in insights_data.items():
                    while len(value_list) < max_len:
                        value_list.append('')
                
                insights_df = pd.DataFrame(insights_data)
                insights_df.to_excel(writer, sheet_name='Insights', index=False)
        
        buffer.seek(0)
        return buffer.read()
    
    def _plotly_to_image(self, fig: go.Figure) -> Optional[bytes]:
        """Converte gráfico Plotly para imagem PNG"""
        
        try:
            img_bytes = pio.to_image(fig, format='png', width=800, height=600)
            return img_bytes
        except Exception as e:
            st.warning(f"Erro ao converter gráfico: {e}")
            return None
    
    def _load_report_templates(self) -> Dict[str, Template]:
        """Carrega templates HTML para relatórios"""
        
        # Template básico HTML
        default_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Relatório NeuroMap</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #0b0f17; color: #8ab4f8; padding: 20px; text-align: center; }
                .section { margin: 20px 0; padding: 15px; border-left: 4px solid #8ab4f8; }
                .metric { display: inline-block; margin: 10px; padding: 10px; background: #f0f0f0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🧠 Relatório NeuroMap</h1>
                <p>Gerado em {{ generated_at.strftime('%d/%m/%Y às %H:%M') }}</p>
            </div>
            
            <div class="section">
                <h2>Resumo do Perfil</h2>
                <div class="metric">
                    <strong>Tipo MBTI:</strong> {{ scores.mbti_type }}
                </div>
                <div class="metric">
                    <strong>Estilo DISC Dominante:</strong> {{ scores.get_dominant_disc()[0] }}
                </div>
            </div>
            
            {% if insights %}
            <div class="section">
                <h2>Principais Insights</h2>
                <h3>Pontos Fortes:</h3>
                <ul>
                {% for strength in insights.strengths %}
                    <li>{{ strength }}</li>
                {% endfor %}
                </ul>
                
                <h3>Áreas de Desenvolvimento:</h3>
                <ul>
                {% for area in insights.development_areas %}
                    <li>{{ area }}</li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            <div class="section">
                <h2>Scores Detalhados</h2>
                
                <h3>DISC:</h3>
                {% for key, value in scores.disc.items() %}
                <div class="metric">
                    <strong>{{ key.replace('DISC_', '') }}:</strong> {{ value|round(1) }}%
                </div>
                {% endfor %}
                
                <h3>Big Five:</h3>
                {% for key, value in scores.big_five.items() %}
                <div class="metric">
                    <strong>{{ key.replace('B5_', '') }}:</strong> {{ value|round(1) }}%
                </div>
                {% endfor %}
            </div>
        </body>
        </html>
        """
        
        return {
            'default_report.html': Template(default_template),
            'executive_report.html': Template(default_template),
            'complete_report.html': Template(default_template),
            'coaching_report.html': Template(default_template),
            'team_report.html': Template(default_template)
        }
    
    def _get_style_orientation(self, dominant_disc: str, mbti_type: str) -> str:
        """Retorna orientação do estilo baseado em DISC + MBTI"""
        
        orientations = {
            ('D', 'NT'): 'liderança estratégica e inovação',
            ('D', 'ST'): 'execução eficiente e resultados tangíveis',
            ('I', 'NF'): 'inspiração e desenvolvimento de pessoas',
            ('I', 'SF'): 'relacionamentos e comunicação empática',
            ('S', 'SF'): 'harmonia e suporte em equipe',
            ('S', 'ST'): 'estabilidade e processos consistentes',
            ('C', 'NT'): 'análise sistemática e precisão técnica',
            ('C', 'ST'): 'qualidade e conformidade com padrões'
        }
        
        temperament = mbti_type[1] + mbti_type[2]  # Ex: NT, SF, etc.
        key = (dominant_disc, temperament)
        
        return orientations.get(key, 'equilíbrio entre diferentes aspectos comportamentais')
    
    def _get_score_level(self, score: float) -> str:
        """Retorna nível descritivo do score"""
        if score >= 70:
            return "Muito Alto"
        elif score >= 50:
            return "Alto"
        elif score >= 30:
            return "Moderado"
        else:
            return "Baixo"
    
    def _get_percentile_interpretation(self, percentile: float) -> str:
        """Interpreta percentil do Big Five"""
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
    
    def _get_b5_level_interpretation(self, trait: str, score: float) -> str:
        """Retorna interpretação específica do nível B5"""
        
        interpretations = {
            'B5_O': {
                'high': 'Você é criativo, curioso e aberto a novas experiências',
                'low': 'Você prefere rotinas e abordagens práticas e testadas'
            },
            'B5_C': {
                'high': 'Você é organizado, disciplinado e orientado para objetivos',
                'low': 'Você é mais flexível e espontâneo em sua abordagem'
            },
            'B5_E': {
                'high': 'Você é sociável, assertivo e energizado por interações',
                'low': 'Você prefere ambientes mais tranquilos e reflexão interna'
            },
            'B5_A': {
                'high': 'Você é cooperativo, empático e confiante nos outros',
                'low': 'Você é mais cético e competitivo em suas relações'
            },
            'B5_N': {
                'high': 'Você pode ser mais sensível ao estresse e emoções negativas',
                'low': 'Você mantém estabilidade emocional mesmo sob pressão'
            }
        }
        
        trait_interpretations = interpretations.get(trait, {'high': '', 'low': ''})
        level = 'high' if score > 60 else 'low'
        
        return trait_interpretations[level]
    
    def _get_mbti_type_description(self, mbti_type: str) -> str:
        """Retorna descrição detalhada do tipo MBTI"""
        
        descriptions = {
            'INTJ': 'O Arquiteto - Visionário estratégico com forte senso de independência e determinação para transformar ideias em realidade.',
            'INTP': 'O Pensador - Inovador teórico que busca entender os princípios fundamentais por trás do que veem.',
            'ENTJ': 'O Comandante - Líder natural, ousado e com forte vontade, sempre encontrando ou criando soluções.',
            'ENTP': 'O Debatedor - Pensador rápido e original que consegue inspirar outros com suas ideias inovadoras.',
            'INFJ': 'O Advogado - Criativo e perspicaz, inspirado e determinado, com forte senso de integridade pessoal.',
            'INFP': 'O Mediador - Poeta por natureza, gentil e altruísta, sempre em busca de harmonia e potencial humano.',
            'ENFJ': 'O Protagonista - Líder carismático e inspirador, capaz de fascinar seus ouvintes.',
            'ENFP': 'O Ativista - Entusiasta criativo e sociável, sempre vendo a vida cheia de possibilidades.',
            'ISTJ': 'O Logístico - Prático e focado em fatos, confiável e responsável em suas ações.',
            'ISFJ': 'O Protetor - Protetor caloroso e dedicado, sempre pronto para defender seus entes queridos.',
            'ESTJ': 'O Executivo - Excelente administrador, com talento natural para gerenciar pessoas e processos.',
            'ESFJ': 'O Cônsul - Extraordinariamente atencioso, sociável e popular, sempre ansioso para ajudar.',
            'ISTP': 'O Virtuoso - Experimentador ousado e prático, mestre de todos os tipos de ferramentas.',
            'ISFP': 'O Aventureiro - Artista flexível e charmoso, sempre pronto para explorar novas possibilidades.',
            'ESTP': 'O Empreendedor - Inteligente, perceptivo e verdadeiramente espontâneo, excelente em situações de crise.',
            'ESFP': 'O Animador - Espontâneo, energético e entusiasta, a vida nunca é chata ao seu redor.'
        }
        
        return descriptions.get(mbti_type, f'Tipo {mbti_type} - Combinação única de preferências cognitivas.')
    
    def _prepare_summary_data(self, assessment: UserAssessment) -> List[Dict]:
        """Prepara dados de resumo para Excel"""
        
        dominant_disc, strength = assessment.scores.get_dominant_disc()
        
        return [
            {'Métrica': 'Tipo MBTI', 'Valor': assessment.scores.mbti_type},
            {'Métrica': 'Estilo DISC Dominante', 'Valor': f'{dominant_disc} ({strength:.1f}%)'},
            {'Métrica': 'Data da Avaliação', 'Valor': assessment.timestamp.strftime('%d/%m/%Y')},
            {'Métrica': 'Confiabilidade', 'Valor': f'{assessment.reliability_score:.0%}' if assessment.reliability_score else 'N/A'},
            {'Métrica': 'Tempo de Conclusão', 'Valor': f'{assessment.completion_time_minutes} min' if assessment.completion_time_minutes else 'N/A'}
        ]
    
    def _generate_html_charts(self, scores: PersonalityScores) -> Dict[str, str]:
        """Gera gráficos em HTML para inclusão no relatório"""
        
        charts = {}
        
        # Gráfico DISC
        disc_chart = self.visualizer.create_disc_radar_chart(scores)
        charts['disc'] = pio.to_html(disc_chart, include_plotlyjs='cdn', div_id='disc-chart')
        
        # Gráfico Big Five
        b5_chart = self.visualizer.create_big_five_bars(scores)
        charts['big_five'] = pio.to_html(b5_chart, include_plotlyjs=False, div_id='b5-chart')
        
        # Gráfico MBTI
        mbti_chart = self.visualizer.create_mbti_preference_chart(scores)
        charts['mbti'] = pio.to_html(mbti_chart, include_plotlyjs=False, div_id='mbti-chart')
        
        return charts

# Interface Streamlit para geração de relatórios
class ReportInterface:
    """Interface Streamlit para geração e customização de relatórios"""
    
    def __init__(self):
        self.report_generator = AdvancedReportGenerator()
    
    def render_report_generator(self, assessment: UserAssessment) -> None:
        """Renderiza interface de geração de relatórios"""
        
        st.markdown("### 📄 Gerador de Relatórios Personalizados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox(
                "Tipo de Relatório:",
                [
                    ("executive", "📊 Executivo - Resumo para liderança"),
                    ("complete", "📚 Completo - Análise detalhada"),
                    ("coaching", "🎯 Coaching - Para desenvolvimento"),
                    ("team", "👥 Equipe - Dinâmicas de grupo")
                ],
                format_func=lambda x: x[1]
            )[0]
        
        with col2:
            format_type = st.selectbox(
                "Formato:",
                [
                    ("pdf", "📄 PDF - Para impressão"),
                    ("html", "🌐 HTML - Interativo"),
                    ("excel", "📊 Excel - Dados tabulares")
                ],
                format_func=lambda x: x[1]
            )[0]
        
        # Customizações
        with st.expander("🎨 Customizações Avançadas"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                include_charts = st.checkbox("Incluir gráficos", value=True)
                include_methodology = st.checkbox("Incluir metodologia", value=True)
                include_recommendations = st.checkbox("Incluir recomendações", value=True)
            
            with col2:
                color_scheme = st.selectbox(
                    "Esquema de cores:",
                    ["Padrão", "Profissional", "Moderno", "Clássico"]
                )
                
                language = st.selectbox(
                    "Idioma:",
                    ["Português", "English", "Español"]
                )
        
        customizations = {
            "include_charts": include_charts,
            "include_methodology": include_methodology,
            "include_recommendations": include_recommendations,
            "color_scheme": color_scheme,
            "language": language
        }
        
        # Botão de geração
        if st.button("🚀 Gerar Relatório", type="primary", use_container_width=True):
            
            with st.spinner(f"Gerando relatório {format_type.upper()}..."):
                try:
                    report_data = self.report_generator.generate_comprehensive_report(
                        assessment, report_type, format_type, customizations
                    )
                    
                    # Determina MIME type
                    mime_types = {
                        'pdf': 'application/pdf',
                        'html': 'text/html',
                        'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    }
                    
                    # Nome do arquivo
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"neuromap_relatorio_{report_type}_{timestamp}.{format_type if format_type != 'excel' else 'xlsx'}"
                    
                    # Botão de download
                    st.download_button(
                        label=f"⬇️ Baixar Relatório {format_type.upper()}",
                        data=report_data,
                        file_name=filename,
                        mime=mime_types[format_type],
                        use_container_width=True
                    )
                    
                    st.success("✅ Relatório gerado com sucesso!")
                    
                except Exception as e:
                    st.error(f"❌ Erro ao gerar relatório: {e}")
        
        # Preview do relatório
        if format_type == "html" and st.checkbox("🔍 Preview do Relatório"):
            with st.spinner("Gerando preview..."):
                try:
                    preview_data = self.report_generator.generate_comprehensive_report(
                        assessment, report_type, "html", customizations
                    )
                    
                    st.markdown("#### Preview:")
                    st.components.v1.html(preview_data.decode('utf-8'), height=600, scrolling=True)
                    
                except Exception as e:
                    st.error(f"Erro no preview: {e}")
