# app.py — NeuroMap (Firebase Edition, usando fpdf2 para PDF)
# ===========================================================
# Stack: Python + Streamlit + Firebase Auth + Firestore (REST)
# Recursos: Login/Signup, questionário (48 itens), cálculo de scores,
# relatório HTML e PDF, persistência por usuário via Firestore.

import os
import io
import json
import datetime as dt
from dataclasses import dataclass
from typing import Dict, List

import requests
import streamlit as st
from pydantic import BaseModel, Field
from fpdf import FPDF  # PDF com fpdf2

# =========================
# 🔧 Config & Secrets
# =========================
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY") or st.secrets.get("FIREBASE_API_KEY", "")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID") or st.secrets.get("FIREBASE_PROJECT_ID", "")

if not FIREBASE_API_KEY or not FIREBASE_PROJECT_ID:
    st.warning("⚠️ Configure FIREBASE_API_KEY e FIREBASE_PROJECT_ID nos secrets/env para salvar no Firestore.")

# =========================
# 🔐 Firebase Auth (REST)
# =========================
AUTH_SIGNUP_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={key}"
AUTH_SIGNIN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={key}"


def fb_signup(email: str, password: str) -> Dict:
    url = AUTH_SIGNUP_URL.format(key=FIREBASE_API_KEY)
    r = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True})
    r.raise_for_status()
    return r.json()  # idToken, refreshToken, localId (uid)


def fb_signin(email: str, password: str) -> Dict:
    url = AUTH_SIGNIN_URL.format(key=FIREBASE_API_KEY)
    r = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True})
    r.raise_for_status()
    return r.json()


# =========================
# 📦 Firestore (REST) — users/{uid}/assessments/{doc}
# =========================
FS_BASE = (
    f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}"
    "/databases/(default)/documents"
)


def _fs_headers(id_token: str) -> Dict[str, str]:
    return {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": f"Bearer {id_token}",
    }


def fs_create_assessment(id_token: str, uid: str, answers: dict, scores: dict, profile: dict) -> Dict:
    url = f"{FS_BASE}/users/{uid}/assessments"
    body = {
        "fields": {
            "answers": {"stringValue": json.dumps(answers, ensure_ascii=False)},
            "scores": {"stringValue": json.dumps(scores, ensure_ascii=False)},
            "profile": {"stringValue": json.dumps(profile, ensure_ascii=False)},
            "owner_uid": {"stringValue": uid},
            "ts": {"timestampValue": dt.datetime.utcnow().isoformat() + "Z"},
        }
    }
    r = requests.post(url, headers=_fs_headers(id_token), json=body)
    if not r.ok:
        raise Exception(f"Firestore create error {r.status_code}: {r.text}")
    return r.json()


def fs_get_latest_assessment(id_token: str, uid: str):
    url = f"{FS_BASE}/users/{uid}/assessments?pageSize=1&orderBy=createTime desc"
    r = requests.get(url, headers=_fs_headers(id_token))
    if not r.ok:
        raise Exception(f"Firestore get error {r.status_code}: {r.text}")
    docs = r.json().get("documents", [])
    if not docs:
        return None
    fields = docs[0]["fields"]
    return {
        "answers": json.loads(fields["answers"]["stringValue"]),
        "scores": json.loads(fields["scores"]["stringValue"]),
        "profile": json.loads(fields["profile"]["stringValue"]),
    }


# =========================
# 🧪 Questionário — 48 itens
# =========================
class Item(BaseModel):
    id: int
    text: str
    scale: str = "1 (Discordo) — 5 (Concordo)"
    weights: Dict[str, float] = Field(default_factory=dict)


DISC_KEYS = ["DISC_D", "DISC_I", "DISC_S", "DISC_C"]
B5_KEYS = ["B5_O", "B5_C", "B5_E", "B5_A", "B5_N"]
MBTI_KEYS = ["MBTI_E", "MBTI_I", "MBTI_S", "MBTI_N", "MBTI_T", "MBTI_F", "MBTI_J", "MBTI_P"]

ITEMS: List[Item] = []

texts_block1 = [
    "Gosto de assumir a responsabilidade quando algo importante precisa ser feito.",
    "Tenho facilidade em enxergar solucoes logicas para problemas complexos.",
    "Gosto de seguir metodos e padroes bem definidos.",
    "Prefiro agir rapidamente a ficar analisando demais uma situacao.",
    "Tenho prazer em planejar as coisas com antecedencia.",
    "Fico desconfortavel quando as pessoas sao muito emotivas ao meu redor.",
    "Sinto-me motivado quando enfrento grandes desafios.",
    "Quando erro, costumo me cobrar mais do que os outros cobrariam.",
    "Gosto de aprender coisas novas, mesmo que nao sejam uteis de imediato.",
    "Prefiro ter controle total de um projeto a depender de outras pessoas.",
    "Tenho facilidade em lidar com situacoes novas e incertas.",
    "Quando alguem discorda de mim, busco entender o ponto de vista antes de responder.",
]

texts_block2 = [
    "Costumo esconder o que sinto para evitar conflitos.",
    "Tenho facilidade em me colocar no lugar dos outros.",
    "Fico incomodado quando as pessoas nao cumprem o que prometem.",
    "Gosto de estar rodeado de pessoas e conversar sobre varios assuntos.",
    "Quando estou sob pressao, consigo manter a calma e pensar com clareza.",
    "Tenho dificuldade em aceitar criticas, mesmo quando sao construtivas.",
    "Gosto de ajudar os outros, mesmo que isso atrase minhas tarefas.",
    "Em situacoes tensas, minha primeira reacao costuma ser emocional.",
    "Prefiro ambientes tranquilos e organizados aos muito agitados.",
    "Tenho facilidade em expressar afeto e demonstrar apreco as pessoas.",
    "Evito discutir quando percebo que o outro esta com raiva.",
    "Valorizo mais o respeito e a lealdade do que a popularidade.",
]

texts_block3 = [
    "Tenho prazer em motivar outras pessoas a atingirem resultados.",
    "Prefiro liderar a ser liderado.",
    "Gosto de trabalhar em equipe, mesmo que precise ceder em algumas decisoes.",
    "Quando algo da errado, costumo analisar friamente o que aconteceu.",
    "Evito correr riscos quando nao tenho todas as informacoes.",
    "Sinto-me energizado quando estou aprendendo algo desafiador.",
    "Sou mais produtivo quando tenho liberdade para decidir como fazer meu trabalho.",
    "Prefiro metas claras e mensuraveis a objetivos vagos.",
    "Quando uma ideia e boa, gosto de coloca-la em pratica imediatamente.",
    "Costumo assumir o papel de mediador quando ha conflito em grupo.",
    "Gosto de inovar, mesmo que isso traga inseguranca no inicio.",
    "Quando lidero, busco mais eficiencia do que popularidade.",
]

texts_block4 = [
    "Acredito que tudo deve ter um proposito claro antes de ser iniciado.",
    "Tenho mais interesse em resultados praticos do que em teorias.",
    "Busco equilibrio entre razao e emocao em minhas decisoes.",
    "Valorizo disciplina mais do que inspiracao.",
    "Acredito que as pessoas devem ser julgadas pelos resultados que entregam.",
    "Tenho curiosidade sobre temas filosoficos e existenciais.",
    "Gosto de assumir desafios que me tiram da zona de conforto.",
    "Sinto-me realizado quando consigo ensinar ou orientar alguem.",
    "Acredito que o autoconhecimento e essencial para o sucesso.",
    "Prefiro ser respeitado a ser admirado.",
    "Tenho um senso de missao pessoal no que faco.",
    "Busco deixar um legado positivo no ambiente onde atuo.",
]


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

ITEMS.clear()
_id = 1
for block in [texts_block1, texts_block2, texts_block3, texts_block4]:
    for t in block:
        ITEMS.append(Item(id=_id, text=t, weights=WEIGHTS[_id - 1]))
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

    for item in ITEMS:
        v = float(answers.get(item.id, 0))
        for k, wv in item.weights.items():
            if k.startswith("DISC_"):
                disc[k] += v * wv
            elif k.startswith("B5_"):
                b5[k] += v * wv
            elif k.startswith("MBTI_"):
                mbti[k] += v * wv

    def normalize(d: Dict[str, float]) -> Dict[str, float]:
        if not d:
            return {}
        lo = min(d.values())
        hi = max(d.values())
        span = (hi - lo) or 1.0
        return {k: round((v - lo) / span * 100.0, 1) for k, v in d.items()}

    disc_n = normalize(disc)
    b5_n = normalize(b5)

    def axis(a_pos: str, a_neg: str) -> float:
        return mbti.get(a_pos, 0.0) - mbti.get(a_neg, 0.0)

    axes = {
        "EI": axis("MBTI_E", "MBTI_I"),
        "SN": axis("MBTI_S", "MBTI_N"),
        "TF": axis("MBTI_T", "MBTI_F"),
        "JP": axis("MBTI_J", "MBTI_P"),
    }

    def letter(axis_key: str) -> str:
        v = axes[axis_key]
        return {
            "EI": "E" if v >= 0 else "I",
            "SN": "S" if v >= 0 else "N",
            "TF": "T" if v >= 0 else "F",
            "JP": "J" if v >= 0 else "P",
        }[axis_key]

    mbti_type = "".join([letter(k) for k in ["EI", "SN", "TF", "JP"]])
    return ScorePack(disc=disc_n, b5=b5_n, mbti_axis=axes, mbti_type=mbti_type)


# =========================
# 🧾 Relatórios (HTML / PDF)
# =========================

def build_html_report(scores: ScorePack, profile: Dict, answers: Dict[int, int]) -> str:
    disc = scores.disc
    b5 = scores.b5
    return f"""
    <html><head><meta charset='utf-8'><title>Relatorio NeuroMap</title>
    <style>
      body {{ font-family: Arial, sans-serif; background:#0b0f17; color:#e6edf3; }}
      .card {{ background:#121826; padding:18px; border-radius:12px; margin:12px 0; }}
      h1, h2 {{ color:#8ab4f8; }}
      table {{ width:100%; border-collapse: collapse; }}
      th, td {{ border-bottom: 1px solid #223; padding: 8px; }}
      th {{ text-align:left; color:#a8c7fa; }}
      .pill {{ display:inline-block; padding:4px 10px; border-radius:999px; background:#1e2a44; margin-right:6px; }}
    </style></head><body>
      <h1>Relatorio de Personalidade - NeuroMap</h1>
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
          <tr><th>Extroversao (E)</th><td>{b5.get('B5_E',0)}%</td></tr>
          <tr><th>Amabilidade (A)</th><td>{b5.get('B5_A',0)}%</td></tr>
          <tr><th>Estabilidade Emocional (-N)</th><td>{100 - b5.get('B5_N',0)}%</td></tr>
        </table>
      </div>
      <div class='card'>
        <h2>Interpretacao</h2>
        <p>{profile.get('summary','')}</p>
        <ul>
          <li><b>Pontos fortes:</b> {', '.join(profile.get('strengths', []))}</li>
          <li><b>Pontos de atencao:</b> {', '.join(profile.get('risks', []))}</li>
          <li><b>Recomendacoes:</b> {', '.join(profile.get('reco', []))}</li>
        </ul>
      </div>
    </body></html>
    """


# helper para garantir que o texto esta em latin-1
def pdf_safe(text: str) -> str:
    return text.encode("latin-1", "replace").decode("latin-1")


def build_pdf_report(buf: io.BytesIO, scores: ScorePack, profile: Dict):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    disc = scores.disc
    b5 = scores.b5

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, pdf_safe("Relatorio de Personalidade - NeuroMap"), ln=1)

    pdf.set_font("Arial", "", 12)
    pdf.ln(4)
    pdf.cell(0, 8, pdf_safe(f"MBTI: {scores.mbti_type}"), ln=1)
    pdf.cell(
        0,
        8,
        pdf_safe(
            f"D: {disc.get('DISC_D',0)}%  I: {disc.get('DISC_I',0)}%  "
            f"S: {disc.get('DISC_S',0)}%  C: {disc.get('DISC_C',0)}%"
        ),
        ln=1,
    )

    pdf.ln(4)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, pdf_safe("Big Five"), ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 6, pdf_safe(f"Abertura (O): {b5.get('B5_O',0)}%"), ln=1)
    pdf.cell(0, 6, pdf_safe(f"Conscienciosidade (C): {b5.get('B5_C',0)}%"), ln=1)
    pdf.cell(0, 6, pdf_safe(f"Extroversao (E): {b5.get('B5_E',0)}%"), ln=1)
    pdf.cell(0, 6, pdf_safe(f"Amabilidade (A): {b5.get('B5_A',0)}%"), ln=1)
    pdf.cell(0, 6, pdf_safe(f"Estabilidade Emocional (-N): {100 - b5.get('B5_N',0)}%"), ln=1)

    pdf.ln(4)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, pdf_safe("Interpretacao"), ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 6, pdf_safe(profile.get("summary", "")))

    strengths = ", ".join(profile.get("strengths", []))
    risks = ", ".join(profile.get("risks", []))
    reco = ", ".join(profile.get("reco", []))

    pdf.ln(2)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, pdf_safe("Pontos fortes:"), ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 6, pdf_safe(strengths or "-"))

    pdf.ln(2)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, pdf_safe("Pontos de atencao:"), ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 6, pdf_safe(risks or "-"))

    pdf.ln(2)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, pdf_safe("Recomendacoes:"), ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 6, pdf_safe(reco or "-"))

    # Gera o PDF em memória (fpdf2 pode retornar str ou bytes)
    pdf_bytes = pdf.output(dest="S")
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode("latin-1")  # compatibilidade
    buf.write(pdf_bytes)



# =========================
# 🧭 Perfil textual
# =========================
def synthesize_profile(scores: ScorePack) -> Dict:
    D = scores.disc.get("DISC_D", 0)
    S = scores.disc.get("DISC_S", 0)
    I = scores.disc.get("DISC_I", 0)
    C = scores.disc.get("DISC_C", 0)
    b5 = scores.b5

    strengths, risks, reco = [], [], []

    if D > 70:
        strengths.append("Lideranca e decisao sob pressao")
        risks.append("Impaciencia com lentidao/ambiguidade")
        reco.append("Praticar empatia situacional ao cobrar resultados")
    if S > 65:
        strengths.append("Consistencia e autocontrole emocional")
        reco.append("Equilibrar constancia com experimentacao")
    if C > 60:
        strengths.append("Qualidade, metodo e padrao elevado")
        risks.append("Possivel rigidez ou microgestao")
        reco.append("Definir criterios de 'bom o suficiente'")
    if I > 55:
        strengths.append("Comunicacao e influencia objetivas")
    if b5.get("B5_O", 0) > 60:
        strengths.append("Curiosidade intelectual e visao de futuro")
    if b5.get("B5_C", 0) > 70:
        strengths.append("Disciplina e execucao confiavel")
        risks.append("Autoexigencia acima do saudavel")
        reco.append("Celebrar marcos e instituir pausas estrategicas")
    if b5.get("B5_N", 0) > 55:
        risks.append("Tensao interna em cenarios de alto risco")
        reco.append("Praticas de regulacao emocional e delegacao")

    summary = (
        f"MBTI sugerido: {scores.mbti_type}. Combina orientacao a resultados (D {int(D)}%) "
        f"com constancia (S {int(S)}%) e metodo (C {int(C)}%), "
        f"equilibrados por comunicacao objetiva (I {int(I)}%). "
        "Big Five indica alta conscienciosidade e foco em performance."
    )

    return {
        "summary": summary,
        "strengths": strengths or ["Foco e aprendizado"],
        "risks": risks or ["Equilibrio entre performance e bem-estar"],
        "reco": reco or ["Ciclos de revisao e descanso planejados"],
    }


# =========================
# 🖥️ UI – Streamlit
# =========================
st.set_page_config(page_title="NeuroMap – Avaliacao", page_icon="🧠", layout="wide")

st.sidebar.title("🧠 NeuroMap")
mode = st.sidebar.radio("Navegacao", ["Login / Cadastro", "Questionario", "Meu Relatorio"], index=0)

if "uid" not in st.session_state:
    st.session_state.uid = None
if "idToken" not in st.session_state:
    st.session_state.idToken = None
if "answers" not in st.session_state:
    st.session_state.answers = {}


def ui_auth():
    st.subheader("Login ou Cadastro (Firebase)")
    tab_l, tab_s, tab_info = st.tabs(["Entrar", "Cadastrar", "Regras Firestore"])

    with tab_l:
        email = st.text_input("Email")
        pwd = st.text_input("Senha", type="password")
        if st.button("Entrar", use_container_width=True):
            try:
                data = fb_signin(email, pwd)
                st.session_state.uid = data["localId"]
                st.session_state.idToken = data["idToken"]
                st.success("Bem-vindo ao NeuroMap!")
            except Exception as e:
                st.error(f"Falha no login: {e}")

    with tab_s:
        email = st.text_input("Email (cadastro)")
        pwd = st.text_input("Senha (cadastro)", type="password")
        if st.button("Criar conta", use_container_width=True):
            try:
                fb_signup(email, pwd)
                st.success("Conta criada. Verifique seu email e faca login.")
            except Exception as e:
                st.error(f"Erro no cadastro: {e}")

    with tab_info:
        st.code(
            """rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/assessments/{docId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}""",
            language="firebase",
        )


def ui_questionnaire():
    st.subheader("Questionario (48 itens)")
    if not st.session_state.uid:
        st.info("Faca login para vincular e salvar sua avaliacao com seguranca.")

    c_top = st.columns(2)
    with c_top[0]:
        st.write("**Escala:** 1 Discordo totalmente — 5 Concordo totalmente")
    with c_top[1]:
        if st.button("Zerar respostas"):
            st.session_state.answers = {}

    for item in ITEMS:
        st.session_state.answers[item.id] = st.slider(
            f"{item.id}. {item.text}", 1, 5, int(st.session_state.answers.get(item.id, 3))
        )

    if st.button("🔒 Salvar e calcular meu perfil", use_container_width=True):
        scores = compute_scores(st.session_state.answers)
        profile = synthesize_profile(scores)
        st.session_state.scores = scores
        st.session_state.profile = profile

        if st.session_state.uid and st.session_state.idToken:
            try:
                fs_create_assessment(
                    st.session_state.idToken,
                    st.session_state.uid,
                    st.session_state.answers,
                    {
                        "disc": scores.disc,
                        "b5": scores.b5,
                        "mbti_axis": scores.mbti_axis,
                        "mbti_type": scores.mbti_type,
                    },
                    profile,
                )
                st.success("Avaliacao salva no Firestore.")
            except Exception as e:
                st.error(f"Erro ao salvar no Firestore: {e}")
        else:
            st.warning("Faca login para persistir sua avaliacao.")


def ui_report():
    st.subheader("Meu Relatorio")

    if "scores" not in st.session_state and st.session_state.uid and st.session_state.idToken:
        try:
            last = fs_get_latest_assessment(st.session_state.idToken, st.session_state.uid)
            if last:
                st.session_state.answers = last["answers"]
                sc = last["scores"]
                st.session_state.scores = ScorePack(
                    disc=sc["disc"], b5=sc["b5"], mbti_axis=sc["mbti_axis"], mbti_type=sc["mbti_type"]
                )
                st.session_state.profile = last["profile"]
        except Exception as e:
            st.error(f"Erro ao carregar relatorio: {e}")

    if "scores" not in st.session_state:
        st.info("Voce ainda nao gerou um relatorio. Va em 'Questionario'.")
        return

    scores: ScorePack = st.session_state.scores
    profile: Dict = st.session_state.profile

    c1, c2 = st.columns(2)
    with c1:
        st.metric("MBTI", scores.mbti_type)
        st.progress(int(scores.disc.get("DISC_D", 0)), text=f"Dominancia: {scores.disc.get('DISC_D',0)}%")
        st.progress(int(scores.disc.get("DISC_I", 0)), text=f"Influencia: {scores.disc.get('DISC_I',0)}%")
        st.progress(int(scores.disc.get("DISC_S", 0)), text=f"Estabilidade: {scores.disc.get('DISC_S',0)}%")
        st.progress(int(scores.disc.get("DISC_C", 0)), text=f"Conformidade: {scores.disc.get('DISC_C',0)}%")
    with c2:
        st.write("### Big Five")
        st.progress(int(scores.b5.get("B5_O", 0)), text=f"Abertura: {scores.b5.get('B5_O',0)}%")
        st.progress(int(scores.b5.get("B5_C", 0)), text=f"Conscienciosidade: {scores.b5.get('B5_C',0)}%")
        st.progress(int(scores.b5.get("B5_E", 0)), text=f"Extroversao: {scores.b5.get('B5_E',0)}%")
        st.progress(int(scores.b5.get("B5_A", 0)), text=f"Amabilidade: {scores.b5.get('B5_A',0)}%")
        st.progress(
            int(100 - scores.b5.get("B5_N", 0)),
            text=f"Estabilidade emocional: {100 - scores.b5.get('B5_N',0)}%",
        )

    st.divider()
    st.write("### Interpretacao")
    st.write(profile.get("summary", ""))
    st.write("**Pontos fortes**: ", ", ".join(profile.get("strengths", [])))
    st.write("**Pontos de atencao**: ", ", ".join(profile.get("risks", [])))
    st.write("**Recomendacoes**: ", ", ".join(profile.get("reco", [])))

    html_str = build_html_report(scores, profile, st.session_state.answers)
    st.download_button("⬇️ Baixar HTML", data=html_str, file_name="neuromap_relatorio.html", mime="text/html")

    buf = io.BytesIO()
    build_pdf_report(buf, scores, profile)
    st.download_button(
        "⬇️ Baixar PDF",
        data=buf.getvalue(),
        file_name="neuromap_relatorio.pdf",
        mime="application/pdf",
    )


# =========================
# 🔁 Router
# =========================
if mode == "Login / Cadastro":
    ui_auth()
elif mode == "Questionario":
    ui_questionnaire()
else:
    ui_report()
