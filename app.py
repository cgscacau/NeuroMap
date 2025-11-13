# app.py — Sistema de Avaliação de Personalidade (DISC + Big Five + MBTI)
# Requisitos:
#   pip install streamlit supabase "reportlab<4" pydantic
# Execução local:
#   export SUPABASE_URL=...; export SUPABASE_ANON_KEY=...
#   streamlit run app.py
# Observação: este app é single-file e multipáginas via abas. Para produção, recomendo
# separar em módulos, mas aqui mantemos tudo em um arquivo para facilitar o deploy inicial.

import os
import io
import json
import datetime as dt
from dataclasses import dataclass
from typing import Dict, List, Tuple

import streamlit as st
from pydantic import BaseModel, Field
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# =========================
# 🔐 SUPABASE CLIENT (Auth + DB)
# =========================
try:
    from supabase import create_client, Client
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
except Exception as e:
    supabase = None

# =========================
# 🧱 SCHEMA (SQL) — criar no Supabase
# =========================
SCHEMA_SQL = """
-- Tabela de usuários (opcional — pode usar auth.users nativo do Supabase)
-- Neste exemplo usaremos apenas auth.users e gravaremos o user_id nas avaliações.

create table if not exists assessments (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  answers jsonb not null,          -- respostas cruas
  scores jsonb not null,           -- pontuações calculadas
  profile jsonb not null,          -- perfis (DISC/B5/MBTI)
  created_at timestamptz default now()
);

-- Política Row Level Security: apenas o dono lê/escreve
alter table assessments enable row level security;
create policy "insert_own" on assessments for insert with check (auth.uid() = user_id);
create policy "select_own" on assessments for select using (auth.uid() = user_id);
""".strip()

# =========================
# 🧪 Questionário — Banco simplificado (exemplos)
# Para produção, amplie as questões e ajuste pesos. Mantemos 48 itens (12 por bloco) conforme conversa.
# Cada item mapeia para uma dimensão alvo.
# =========================
class Item(BaseModel):
    id: int
    text: str
    scale: str = "1 (Discordo) — 5 (Concordo)"
    weights: Dict[str, float] = Field(default_factory=dict)  # chaves entre {DISC_*, B5_*, MBTI_*}

# Dimensões alvo
DISC_KEYS = ["DISC_D", "DISC_I", "DISC_S", "DISC_C"]
B5_KEYS = ["B5_O", "B5_C", "B5_E", "B5_A", "B5_N"]
MBTI_KEYS = ["MBTI_E", "MBTI_I", "MBTI_S", "MBTI_N", "MBTI_T", "MBTI_F", "MBTI_J", "MBTI_P"]

# Banco de questões (resumo do que construímos — 48 itens)
ITEMS: List[Item] = []
texts_block1 = [
    "Gosto de assumir a responsabilidade quando algo importante precisa ser feito.",
    "Tenho facilidade em enxergar soluções lógicas para problemas complexos.",
    "Gosto de seguir métodos e padrões bem definidos.",
    "Prefiro agir rapidamente a ficar analisando demais uma situação.",
    "Tenho prazer em planejar as coisas com antecedência.",
    "Fico desconfortável quando as pessoas são muito emotivas ao meu redor.",
    "Sinto-me motivado quando enfrento grandes desafios.",
    "Quando erro, costumo me cobrar mais do que os outros cobrariam.",
    "Gosto de aprender coisas novas, mesmo que não sejam úteis de imediato.",
    "Prefiro ter controle total de um projeto a depender de outras pessoas.",
    "Tenho facilidade em lidar com situações novas e incertas.",
    "Quando alguém discorda de mim, busco entender o ponto de vista antes de responder.",
]

texts_block2 = [
    "Costumo esconder o que sinto para evitar conflitos.",
    "Tenho facilidade em me colocar no lugar dos outros.",
    "Fico incomodado quando as pessoas não cumprem o que prometem.",
    "Gosto de estar rodeado de pessoas e conversar sobre vários assuntos.",
    "Quando estou sob pressão, consigo manter a calma e pensar com clareza.",
    "Tenho dificuldade em aceitar críticas, mesmo quando são construtivas.",
    "Gosto de ajudar os outros, mesmo que isso atrase minhas tarefas.",
    "Em situações tensas, minha primeira reação costuma ser emocional.",
    "Prefiro ambientes tranquilos e organizados aos muito agitados.",
    "Tenho facilidade em expressar afeto e demonstrar apreço às pessoas.",
    "Evito discutir quando percebo que o outro está com raiva.",
    "Valorizo mais o respeito e a lealdade do que a popularidade.",
]

texts_block3 = [
    "Tenho prazer em motivar outras pessoas a atingirem resultados.",
    "Prefiro liderar a ser liderado.",
    "Gosto de trabalhar em equipe, mesmo que precise ceder em algumas decisões.",
    "Quando algo dá errado, costumo analisar friamente o que aconteceu.",
    "Evito correr riscos quando não tenho todas as informações.",
    "Sinto-me energizado quando estou aprendendo algo desafiador.",
    "Sou mais produtivo quando tenho liberdade para decidir como fazer meu trabalho.",
    "Prefiro metas claras e mensuráveis a objetivos vagos.",
    "Quando uma ideia é boa, gosto de colocá-la em prática imediatamente.",
    "Costumo assumir o papel de mediador quando há conflito em grupo.",
    "Gosto de inovar, mesmo que isso traga insegurança no início.",
    "Quando lidero, busco mais eficiência do que popularidade.",
]

texts_block4 = [
    "Acredito que tudo deve ter um propósito claro antes de ser iniciado.",
    "Tenho mais interesse em resultados práticos do que em teorias.",
    "Busco equilíbrio entre razão e emoção em minhas decisões.",
    "Valorizo disciplina mais do que inspiração.",
    "Acredito que as pessoas devem ser julgadas pelos resultados que entregam.",
    "Tenho curiosidade sobre temas filosóficos e existenciais.",
    "Gosto de assumir desafios que me tiram da zona de conforto.",
    "Sinto-me realizado quando consigo ensinar ou orientar alguém.",
    "Acredito que o autoconhecimento é essencial para o sucesso.",
    "Prefiro ser respeitado a ser admirado.",
    "Tenho um senso de missão pessoal no que faço.",
    "Busco deixar um legado positivo no ambiente onde atuo.",
]

# Atribuição simplificada de pesos para cada item (pode ser refinado)
# Ideia: cada item pesa em 2-3 dimensões. Escore bruto é soma ponderada.

def w(**kwargs):
    return kwargs

WEIGHTS: List[Dict[str, float]] = [
    # 1-12
    w(DISC_D=1.0, MBTI_J=0.6),
    w(B5_C=0.8, MBTI_T=0.7),
    w(DISC_C=0.9, MBTI_J=0.6),
    w(DISC_D=0.8, MBTI_P=0.4, B5_E=0.3),
    w(B5_C=0.8, MBTI_J=0.7),
    w(B5_N=0.6, MBTI_T=0.5),
    w(DISC_D=0.7, B5_O=0.4),
    w(B5_C=0.8, MBTI_T=0.6),
    w(B5_O=1.0, MBTI_N=0.6),
    w(DISC_D=0.8, MBTI_J=0.5),
    w(B5_E=0.6, MBTI_P=0.5),
    w(B5_A=0.6, MBTI_F=0.6),
    # 13-24
    w(B5_A=0.4, MBTI_T=0.5),
    w(B5_A=0.9, MBTI_F=0.6),
    w(B5_C=0.9, DISC_C=0.4),
    w(B5_E=0.9, MBTI_E=0.6),
    w(DISC_S=0.9, B5_N=-0.2),
    w(B5_N=0.8),
    w(B5_A=0.6, MBTI_F=0.5),
    w(B5_N=0.9),
    w(DISC_S=0.7, MBTI_J=0.5),
    w(B5_A=0.7, MBTI_F=0.6),
    w(B5_A=0.6, MBTI_F=0.5),
    w(DISC_D=0.6, B5_A=-0.2),
    # 25-36
    w(B5_E=0.7, MBTI_E=0.6),
    w(DISC_D=0.9, MBTI_J=0.4),
    w(B5_A=0.6, MBTI_F=0.4),
    w(MBTI_T=0.8, DISC_C=0.5),
    w(B5_C=-0.6, MBTI_P=0.7),
    w(B5_O=0.9, MBTI_N=0.6),
    w(DISC_D=0.7, MBTI_P=0.5),
    w(B5_C=1.0, MBTI_J=0.6),
    w(DISC_D=0.7, MBTI_J=0.5),
    w(B5_A=0.6, DISC_S=0.5),
    w(B5_O=0.8, MBTI_N=0.6),
    w(DISC_D=0.8, B5_C=0.5),
    # 37-48
    w(MBTI_J=0.8, DISC_C=0.4),
    w(B5_C=0.7, MBTI_T=0.4),
    w(B5_N=-0.7, MBTI_T=0.4, MBTI_F=0.4),
    w(B5_C=0.9, MBTI_J=0.6),
    w(DISC_D=0.6, MBTI_T=0.5),
    w(B5_O=0.9, MBTI_N=0.6),
    w(DISC_D=0.6, MBTI_P=0.5),
    w(B5_A=0.8, MBTI_F=0.6),
    w(B5_O=0.6, MBTI_N=0.6),
    w(DISC_D=0.6, MBTI_T=0.4),
    w(MBTI_J=0.6, MBTI_N=0.5),
    w(MBTI_N=0.6, B5_O=0.6),
]

# Monta ITEMS
_id = 1
for txts in [texts_block1, texts_block2, texts_block3, texts_block4]:
    for t in txts:
        ITEMS.append(Item(id=_id, text=t, weights=WEIGHTS[_id-1]))
        _id += 1

# =========================
# 🔢 Scoring
# =========================
@dataclass
class ScorePack:
    disc: Dict[str, float]
    b5: Dict[str, float]
    mbti_axis: Dict[str, float]
    mbti_type: str


def compute_scores(answers: Dict[int, int]) -> ScorePack:
    disc = {k: 0.0 for k in DISC_KEYS}
    b5 = {k: 0.0 for k in B5_KEYS}
    mbti = {k: 0.0 for k in MBTI_KEYS}

    # acumula ponderado
    for item in ITEMS:
        v = float(answers.get(item.id, 0))
        for k, wv in item.weights.items():
            if k.startswith("DISC_"):
                disc[k] += v * wv
            elif k.startswith("B5_"):
                b5[k] += v * wv
            elif k.startswith("MBTI_"):
                mbti[k] += v * wv

    # Normalização simples 0-100 (heurstica)
    def normalize(d: Dict[str, float]) -> Dict[str, float]:
        if not d:
            return {}
        lo = min(d.values())
        hi = max(d.values())
        span = (hi - lo) or 1.0
        return {k: round((v - lo) / span * 100.0, 1) for k, v in d.items()}

    disc_n = normalize(disc)
    b5_n = normalize(b5)

    # MBTI tipo a partir dos eixos
    def axis(a_pos: str, a_neg: str) -> float:
        return mbti.get(a_pos, 0.0) - mbti.get(a_neg, 0.0)

    axes = {
        "EI": axis("MBTI_E", "MBTI_I"),
        "SN": axis("MBTI_S", "MBTI_N"),
        "TF": axis("MBTI_T", "MBTI_F"),
        "JP": axis("MBTI_J", "MBTI_P"),
    }

    def axis_letter(axis_key: str) -> str:
        v = axes[axis_key]
        if axis_key == "EI":
            return "E" if v >= 0 else "I"
        if axis_key == "SN":
            return "S" if v >= 0 else "N"
        if axis_key == "TF":
            return "T" if v >= 0 else "F"
        if axis_key == "JP":
            return "J" if v >= 0 else "P"
        return "?"

    mbti_type = "".join([axis_letter(k) for k in ["EI", "SN", "TF", "JP"]])

    return ScorePack(disc=disc_n, b5=b5_n, mbti_axis=axes, mbti_type=mbti_type)

# =========================
# 🧾 Relatórios (HTML e PDF)
# =========================

def build_html_report(scores: ScorePack, profile: Dict, answers: Dict[int, int]) -> str:
    disc = scores.disc; b5 = scores.b5
    html = f"""
    <html><head><meta charset='utf-8'><title>Relatório de Personalidade</title>
    <style>
      body {{ font-family: Arial, sans-serif; background:#0b0f17; color:#e6edf3; }}
      .card {{ background:#121826; padding:18px; border-radius:12px; margin:12px 0; }}
      h1, h2 {{ color:#8ab4f8; }}
      table {{ width:100%; border-collapse: collapse; }}
      th, td {{ border-bottom: 1px solid #223; padding: 8px; }}
      th {{ text-align:left; color:#a8c7fa; }}
      .pill {{ display:inline-block; padding:4px 10px; border-radius:999px; background:#1e2a44; margin-right:6px; }}
    </style></head><body>
    <h1>Relatório de Personalidade</h1>
    <div class='card'>
      <h2>Resumo</h2>
      <p><span class='pill'>MBTI: <b>{scores.mbti_type}</b></span>
         <span class='pill'>D: {disc.get('DISC_D',0)}%</span>
         <span class='pill'>I: {disc.get('DISC_I',0)}%</span>
         <span class='pill'>S: {disc.get('DISC_S',0)}%</span>
         <span class='pill'>C: {disc.get('DISC_C',0)}%</span></p>
    </div>
    <div class='card'>
      <h2>Big Five</h2>
      <table>
        <tr><th>Abertura (O)</th><td>{b5.get('B5_O',0)}%</td></tr>
        <tr><th>Conscienciosidade (C)</th><td>{b5.get('B5_C',0)}%</td></tr>
        <tr><th>Extroversão (E)</th><td>{b5.get('B5_E',0)}%</td></tr>
        <tr><th>Amabilidade (A)</th><td>{b5.get('B5_A',0)}%</td></tr>
        <tr><th>Estab. Emocional (−N)</th><td>{100 - b5.get('B5_N',0)}%</td></tr>
      </table>
    </div>
    <div class='card'>
      <h2>Interpretação</h2>
      <p>{profile.get('summary','')}</p>
      <ul>
        <li><b>Pontos fortes:</b> {', '.join(profile.get('strengths', []))}</li>
        <li><b>Pontos de atenção:</b> {', '.join(profile.get('risks', []))}</li>
        <li><b>Recomendações:</b> {', '.join(profile.get('reco', []))}</li>
      </ul>
    </div>
    </body></html>
    """
    return html


def build_pdf_report(buf: io.BytesIO, scores: ScorePack, profile: Dict):
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("<b>Relatório de Personalidade</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    disc = scores.disc; b5 = scores.b5

    story.append(Paragraph(f"<b>MBTI:</b> {scores.mbti_type}", styles["Heading2"]))
    story.append(Paragraph(
        f"D: {disc.get('DISC_D',0)}% — I: {disc.get('DISC_I',0)}% — "
        f"S: {disc.get('DISC_S',0)}% — C: {disc.get('DISC_C',0)}%",
        styles["BodyText"]))
    story.append(Spacer(1, 8))

    table_data = [
        ["Dimensão (Big Five)", "%"],
        ["Abertura", b5.get('B5_O',0)],
        ["Conscienciosidade", b5.get('B5_C',0)],
        ["Extroversão", b5.get('B5_E',0)],
        ["Amabilidade", b5.get('B5_A',0)],
        ["Estabilidade Emocional (−N)", 100 - b5.get('B5_N',0)],
    ]
    tbl = Table(table_data, colWidths=[250, 120])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Interpretação</b>", styles["Heading2"]))
    story.append(Paragraph(profile.get('summary',''), styles["BodyText"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Pontos fortes:</b> " + ", ".join(profile.get('strengths', [])), styles["BodyText"]))
    story.append(Paragraph("<b>Pontos de atenção:</b> " + ", ".join(profile.get('risks', [])), styles["BodyText"]))
    story.append(Paragraph("<b>Recomendações:</b> " + ", ".join(profile.get('reco', [])), styles["BodyText"]))

    doc = SimpleDocTemplate(buf, pagesize=A4)
    doc.build(story)

# =========================
# 🧭 Perfis (texto automático baseado em scores)
# =========================

def synthesize_profile(scores: ScorePack) -> Dict:
    D = scores.disc.get("DISC_D", 0)
    S = scores.disc.get("DISC_S", 0)
    I = scores.disc.get("DISC_I", 0)
    C = scores.disc.get("DISC_C", 0)
    b5 = scores.b5

    strengths = []
    risks = []
    reco = []

    if D > 70:
        strengths.append("Liderança e decisão sob pressão")
        risks.append("Impaciência com lentidão/ambiguidade")
        reco.append("Cultivar empatia situacional ao cobrar resultados")
    if S > 65:
        strengths.append("Consistência e autocontrole emocional")
        reco.append("Equilibrar constância com abertura à experimentação")
    if C > 60:
        strengths.append("Qualidade, método e padrão elevado")
        risks.append("Risco de rigidez ou microgestão")
        reco.append("Definir critérios de 'bom o suficiente' para agilizar")
    if I > 55:
        strengths.append("Comunicação e influência objetivas")

    if b5.get("B5_O", 0) > 60:
        strengths.append("Curiosidade intelectual e visão de futuro")
    if b5.get("B5_C", 0) > 70:
        strengths.append("Disciplina e execução confiável")
        risks.append("Autoexigência acima do saudável")
        reco.append("Celebrar marcos e instituir pausas estratégicas")
    if b5.get("B5_N", 0) > 55:
        risks.append("Tensão interna em cenários de alto risco")
        reco.append("Práticas de regulação emocional e delegação")

    summary = (
        f"Perfil MBTI sugerido: {scores.mbti_type}. Combina orientação a resultados (D {int(D)}%) "
        f"com constância (S {int(S)}%) e método (C {int(C)}%), equilibrados por comunicação objetiva (I {int(I)}%). "
        "Nos traços Big Five, destaca-se conscienciosidade/organização e abertura a novas ideias."
    )

    return {
        "summary": summary,
        "strengths": strengths or ["Foco e aprendizado"],
        "risks": risks or ["Manter equilíbrio entre performance e bem-estar"],
        "reco": reco or ["Ciclos de revisão e descanso planejados"],
    }

# =========================
# 🖥️ UI — Streamlit
# =========================
st.set_page_config(page_title="Avaliação de Personalidade", page_icon="🧠", layout="wide")

st.sidebar.title("🧠 Avaliação de Personalidade")
mode = st.sidebar.radio("Navegação", ["Login / Cadastro", "Questionário", "Meu Relatório"], index=0)

# --- Sessão de usuário ---
if "user" not in st.session_state:
    st.session_state.user = None
if "answers" not in st.session_state:
    st.session_state.answers: Dict[int, int] = {}

# --- Funções de Auth ---

def ui_auth():
    st.subheader("Login ou Cadastro")
    if not supabase:
        st.warning("⚠️ Supabase não configurado. Defina SUPABASE_URL e SUPABASE_ANON_KEY.")
    tab_login, tab_signup, tab_sql = st.tabs(["Entrar", "Cadastrar", "SQL (RLS)"])
    with tab_login:
        email = st.text_input("Email")
        pwd = st.text_input("Senha", type="password")
        if st.button("Entrar", use_container_width=True) and supabase:
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pwd})
                st.session_state.user = res.user
                st.success("Bem-vindo!")
            except Exception as e:
                st.error(f"Falha no login: {e}")
    with tab_signup:
        email_s = st.text_input("Email (cadastro)")
        pwd_s = st.text_input("Senha (cadastro)", type="password")
        if st.button("Criar conta", use_container_width=True) and supabase:
            try:
                supabase.auth.sign_up({"email": email_s, "password": pwd_s})
                st.success("Conta criada. Verifique seu email e depois faça login.")
            except Exception as e:
                st.error(f"Falha no cadastro: {e}")
    with tab_sql:
        st.code(SCHEMA_SQL, language="sql")


def ui_questionnaire():
    st.subheader("Questionário (48 itens)")
    if not st.session_state.user:
        st.info("Faça login para salvar suas respostas com segurança.")

    cols = st.columns(2)
    with cols[0]:
        st.write("""**Escala:** 1 Discordo totalmente — 5 Concordo totalmente""")
    with cols[1]:
        if st.button("Zerar respostas", type="secondary"):
            st.session_state.answers = {}

    # Render
    for item in ITEMS:
        st.session_state.answers[item.id] = st.slider(
            f"{item.id}. {item.text}", 1, 5, int(st.session_state.answers.get(item.id, 3))
        )

    if st.button("🔒 Salvar e calcular meu perfil", use_container_width=True):
        scores = compute_scores(st.session_state.answers)
        profile = synthesize_profile(scores)
        st.session_state.scores = scores
        st.session_state.profile = profile

        if supabase and st.session_state.user:
            try:
                payload = {
                    "user_id": st.session_state.user.id,
                    "answers": json.dumps(st.session_state.answers),
                    "scores": json.dumps({
                        "disc": scores.disc,
                        "b5": scores.b5,
                        "mbti_axis": scores.mbti_axis,
                        "mbti_type": scores.mbti_type,
                    }),
                    "profile": json.dumps(profile),
                }
                supabase.table("assessments").insert(payload).execute()
                st.success("Avaliação salva com sucesso.")
            except Exception as e:
                st.error(f"Erro ao salvar na base: {e}")
        else:
            st.warning("Supabase não configurado ou usuário não autenticado. Dados não persistidos.")


def ui_report():
    st.subheader("Meu Relatório")
    if "scores" not in st.session_state:
        # tentar carregar último do banco
        if supabase and st.session_state.user:
            try:
                data = supabase.table("assessments").select("*").eq("user_id", st.session_state.user.id)\
                    .order("created_at", desc=True).limit(1).execute()
                if data.data:
                    row = data.data[0]
                    st.session_state.answers = json.loads(row["answers"]) if isinstance(row["answers"], str) else row["answers"]
                    sc = row["scores"] if isinstance(row["scores"], dict) else json.loads(row["scores"])
                    st.session_state.scores = ScorePack(
                        disc=sc["disc"], b5=sc["b5"], mbti_axis=sc["mbti_axis"], mbti_type=sc["mbti_type"]
                    )
                    st.session_state.profile = row["profile"] if isinstance(row["profile"], dict) else json.loads(row["profile"])
            except Exception as e:
                st.error(f"Erro ao carregar último relatório: {e}")

    if "scores" not in st.session_state:
        st.info("Você ainda não gerou um relatório. Vá até 'Questionário'.")
        return

    scores: ScorePack = st.session_state.scores
    profile: Dict = st.session_state.profile

    c1, c2 = st.columns(2)
    with c1:
        st.metric("MBTI", scores.mbti_type)
        st.progress(int(scores.disc.get("DISC_D",0)), text=f"Dominância: {scores.disc.get('DISC_D',0)}%")
        st.progress(int(scores.disc.get("DISC_I",0)), text=f"Influência: {scores.disc.get('DISC_I',0)}%")
        st.progress(int(scores.disc.get("DISC_S",0)), text=f"Estabilidade: {scores.disc.get('DISC_S',0)}%")
        st.progress(int(scores.disc.get("DISC_C",0)), text=f"Conformidade: {scores.disc.get('DISC_C',0)}%")
    with c2:
        st.write("### Big Five")
        st.progress(int(scores.b5.get("B5_O",0)), text=f"Abertura: {scores.b5.get('B5_O',0)}%")
        st.progress(int(scores.b5.get("B5_C",0)), text=f"Conscienciosidade: {scores.b5.get('B5_C',0)}%")
        st.progress(int(scores.b5.get("B5_E",0)), text=f"Extroversão: {scores.b5.get('B5_E',0)}%")
        st.progress(int(scores.b5.get("B5_A",0)), text=f"Amabilidade: {scores.b5.get('B5_A',0)}%")
        st.progress(int(100 - scores.b5.get("B5_N",0)), text=f"Estabilidade emocional: {100 - scores.b5.get('B5_N',0)}%")

    st.divider()
    st.write("### Interpretação")
    st.write(profile.get("summary", ""))
    st.write("**Pontos fortes**: ", ", ".join(profile.get("strengths", [])))
    st.write("**Pontos de atenção**: ", ", ".join(profile.get("risks", [])))
    st.write("**Recomendações**: ", ", ".join(profile.get("reco", [])))

    # Downloads
    html_str = build_html_report(scores, profile, st.session_state.answers)
    st.download_button("⬇️ Baixar HTML", data=html_str, file_name="relatorio_personalidade.html", mime="text/html")

    buf = io.BytesIO()
    build_pdf_report(buf, scores, profile)
    st.download_button("⬇️ Baixar PDF", data=buf.getvalue(), file_name="relatorio_personalidade.pdf", mime="application/pdf")

# =========================
# 🔁 Roteamento simples
# =========================
if mode == "Login / Cadastro":
    ui_auth()
elif mode == "Questionário":
    ui_questionnaire()
else:
    ui_report()
