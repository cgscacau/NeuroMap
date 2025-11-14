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
    # ❗ corrigido: sem ?mask.fieldPaths=
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
        # ajuda a debugar caso ainda dê erro
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
# 🧾 Relatórios (HTML / PDF com fpdf2)
# =========================
def build_html_report(scores: ScorePack, profile: Dict, answers: Dict[int, int]) -> str:
    disc = scores.disc
    b5 = scores.b5
    return f"""
    <html><head><meta charset='utf-8'><title>Relatório NeuroMap</title>
    <style>
      body {{ font-family: Arial, sans-serif; background:#0b0f17; color:#e6edf3; }}
      .card {{ background:#121826; padding:18px; border-radius:12px; margin:12px 0; }}
      h1, h2 {{ color:#8ab4f8; }}
      table {{ width:100%; border-collapse: collapse; }}
      th, td {{ border-bottom: 1px solid #223; padding: 8px; }}
      th {{ text-align:left; color:#a8c7fa; }}
      .pill {{ display:inline-block; padding:4px 10px; border-radius:999px; background:#1e2a44; margin-right:6px; }}
    </style></head><body>
      <h1>Relatório de Personalidade – NeuroMap</h1>
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
          <tr><th>Estabilidade Emocional (−N)</th><td>{100 - b5.get('B5_N',0)}%</td></tr>
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


def build_pdf_report(buf: io.BytesIO, scores: ScorePack, profile: Dict):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    disc = scores.disc
    b5 = scores.b5

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório de Personalidade – NeuroMap", ln=1)

    pdf.set_font("Arial", "", 12)
    pdf.ln(4)
    pdf.cell(0, 8, f"MBTI: {scores.mbti_type}", ln=1)
    pdf.cell(
        0,
        8,
        f"D: {disc.get('DISC_D',0)}%  I: {disc.get('DISC_I',0)}%  "
        f"S: {disc.get('DISC_S',0)}%  C: {disc.get('DISC_C',0)}%",
        ln=1,
    )

    pdf.ln(4)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Big Five", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 6, f"Abertura (O): {b5.get('B5_O',0)}%", ln=1)
    pdf.cell(0, 6, f"Conscienciosidade (C): {b5.get('B5_C',0)}%", ln=1)
    pdf.cell(0, 6, f"Extroversão (E): {b5.get('B5_E',0)}%", ln=1)
    pdf.cell(0, 6, f"Amabilidade (A): {b5.get('B5_A',0)}%", ln=1)
    pdf.cell(0, 6, f"Estabilidade Emocional (−N): {100 - b5.get('B5_N',0)}%", ln=1)

    pdf.ln(4)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Interpretação", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 6, profile.get("summary", ""))

    strengths = ", ".join(profile.get("strengths", []))
    risks = ", ".join(profile.get("risks", []))
    reco = ", ".join(profile.get("reco", []))

    pdf.ln(2)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Pontos fortes:", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 6, strengths or "-")

    pdf.ln(2)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Pontos de atenção:", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 6, risks or "-")

    pdf.ln(2)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Recomendações:", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 6, reco or "-")

    pdf_bytes = pdf.output(dest="S").encode("latin-1")
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
        strengths.append("Liderança e decisão sob pressão")
        risks.append("Impaciência com lentidão/ambiguidade")
        reco.append("Praticar empatia situacional ao cobrar resultados")
    if S > 65:
        strengths.append("Consistência e autocontrole emocional")
        reco.append("Equilibrar constância com experimentação")
    if C > 60:
        strengths.append("Qualidade, método e padrão elevado")
        risks.append("Possível rigidez ou microgestão")
        reco.append("Definir critérios de 'bom o suficiente'")
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
        f"MBTI sugerido: {scores.mbti_type}. Combina orientação a resultados (D {int(D)}%) "
        f"com constância (S {int(S)}%) e método (C {int(C)}%), "
        f"equilibrados por comunicação objetiva (I {int(I)}%). "
        "Big Five indica alta conscienciosidade e foco em performance."
    )

    return {
        "summary": summary,
        "strengths": strengths or ["Foco e aprendizado"],
        "risks": risks or ["Equilíbrio entre performance e bem-estar"],
        "reco": reco or ["Ciclos de revisão e descanso planejados"],
    }


# =========================
# 🖥️ UI – Streamlit
# =========================
st.set_page_config(page_title="NeuroMap – Avaliação", page_icon="🧠", layout="wide")

st.sidebar.title("🧠 NeuroMap")
mode = st.sidebar.radio("Navegação", ["Login / Cadastro", "Questionário", "Meu Relatório"], index=0)

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
                st.success("Conta criada. Verifique seu email e faça login.")
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
    st.subheader("Questionário (48 itens)")
    if not st.session_state.uid:
        st.info("Faça login para vincular e salvar sua avaliação com segurança.")

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
                st.success("Avaliação salva no Firestore.")
            except Exception as e:
                st.error(f"Erro ao salvar no Firestore: {e}")
        else:
            st.warning("Faça login para persistir sua avaliação.")


def ui_report():
    st.subheader("Meu Relatório")

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
            st.error(f"Erro ao carregar relatório: {e}")

    if "scores" not in st.session_state:
        st.info("Você ainda não gerou um relatório. Vá em 'Questionário'.")
        return

    scores: ScorePack = st.session_state.scores
    profile: Dict = st.session_state.profile

    c1, c2 = st.columns(2)
    with c1:
        st.metric("MBTI", scores.mbti_type)
        st.progress(int(scores.disc.get("DISC_D", 0)), text=f"Dominância: {scores.disc.get('DISC_D',0)}%")
        st.progress(int(scores.disc.get("DISC_I", 0)), text=f"Influência: {scores.disc.get('DISC_I',0)}%")
        st.progress(int(scores.disc.get("DISC_S", 0)), text=f"Estabilidade: {scores.disc.get('DISC_S',0)}%")
        st.progress(int(scores.disc.get("DISC_C", 0)), text=f"Conformidade: {scores.disc.get('DISC_C',0)}%")
    with c2:
        st.write("### Big Five")
        st.progress(int(scores.b5.get("B5_O", 0)), text=f"Abertura: {scores.b5.get('B5_O',0)}%")
        st.progress(int(scores.b5.get("B5_C", 0)), text=f"Conscienciosidade: {scores.b5.get('B5_C',0)}%")
        st.progress(int(scores.b5.get("B5_E", 0)), text=f"Extroversão: {scores.b5.get('B5_E',0)}%")
        st.progress(int(scores.b5.get("B5_A", 0)), text=f"Amabilidade: {scores.b5.get('B5_A',0)}%")
        st.progress(
            int(100 - scores.b5.get("B5_N", 0)),
            text=f"Estabilidade emocional: {100 - scores.b5.get('B5_N',0)}%",
        )

    st.divider()
    st.write("### Interpretação")
    st.write(profile.get("summary", ""))
    st.write("**Pontos fortes**: ", ", ".join(profile.get("strengths", [])))
    st.write("**Pontos de atenção**: ", ", ".join(profile.get("risks", [])))
    st.write("**Recomendações**: ", ", ".join(profile.get("reco", [])))

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
elif mode == "Questionário":
    ui_questionnaire()
else:
    ui_report()
