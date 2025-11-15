import streamlit as st
import re
from typing import Optional, Tuple
from ...services.auth import AuthManager
from ...utils.validators import EmailValidator, PasswordValidator

class AuthPage:
    """Página de autenticação com UX melhorada"""
    
    def __init__(self):
        self.auth_manager = AuthManager()
        self.email_validator = EmailValidator()
        self.password_validator = PasswordValidator()
    
    def render(self) -> None:
        """Renderiza a página de autenticação"""
        
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='color: #8ab4f8; font-size: 3rem; margin-bottom: 0.5rem;'>
                🧠 NeuroMap
            </h1>
            <p style='color: #a8c7fa; font-size: 1.2rem; margin-bottom: 2rem;'>
                Descubra sua personalidade com precisão científica
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs principais
        tab_login, tab_register, tab_forgot = st.tabs([
            "🔑 Entrar", 
            "📝 Criar Conta", 
            "🔄 Recuperar Senha"
        ])
        
        with tab_login:
            self._render_login_form()
        
        with tab_register:
            self._render_register_form()
        
        with tab_forgot:
            self._render_forgot_password_form()
        
        # Informações sobre segurança
        with st.expander("🔒 Sobre Segurança e Privacidade"):
            st.markdown("""
            **Seus dados estão seguros:**
            - ✅ Criptografia end-to-end
            - ✅ Conformidade com LGPD/GDPR
            - ✅ Dados armazenados no Firebase (Google Cloud)
            - ✅ Nunca compartilhamos informações pessoais
            - ✅ Você pode deletar sua conta a qualquer momento
            """)
    
    def _render_login_form(self) -> None:
        """Renderiza formulário de login"""
        
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### Bem-vindo de volta!")
            
            email = st.text_input(
                "📧 Email",
                placeholder="seu@email.com",
                help="Digite o email usado no cadastro"
            )
            
            password = st.text_input(
                "🔐 Senha",
                type="password",
                placeholder="Sua senha",
                help="Mínimo 6 caracteres"
            )
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                remember_me = st.checkbox("Lembrar de mim")
            
            with col2:
                show_password = st.checkbox("Mostrar senha")
                if show_password:
                    st.text(f"Senha: {password}")
            
            submitted = st.form_submit_button(
                "🚀 Entrar",
                use_container_width=True,
                type="primary"
            )
            
            if submitted:
                self._handle_login(email, password, remember_me)
    
    def _render_register_form(self) -> None:
        """Renderiza formulário de registro"""
        
        with st.form("register_form", clear_on_submit=False):
            st.markdown("### Crie sua conta gratuita")
            
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input(
                    "👤 Nome",
                    placeholder="João",
                    help="Seu primeiro nome"
                )
            
            with col2:
                last_name = st.text_input(
                    "👤 Sobrenome",
                    placeholder="Silva",
                    help="Seu sobrenome"
                )
            
            email = st.text_input(
                "📧 Email",
                placeholder="joao@exemplo.com",
                help="Usaremos para login e comunicações importantes"
            )
            
            password = st.text_input(
                "🔐 Senha",
                type="password",
                placeholder="Mínimo 8 caracteres",
                help="Use letras, números e símbolos para maior segurança"
            )
            
            confirm_password = st.text_input(
                "🔐 Confirmar Senha",
                type="password",
                placeholder="Digite a senha novamente"
            )
            
            # Validação em tempo real da senha
            if password:
                strength = self.password_validator.check_strength(password)
                self._show_password_strength(strength)
            
            # Campos opcionais para personalização
            with st.expander("📊 Informações Opcionais (para insights personalizados)"):
                col1, col2 = st.columns(2)
                
                with col1:
                    age_range = st.selectbox(
                        "Faixa Etária",
                        ["Prefiro não informar", "18-25", "26-35", "36-45", "46-55", "55+"]
                    )
                    
                    industry = st.selectbox(
                        "Área de Atuação",
                        ["Prefiro não informar", "Tecnologia", "Educação", "Saúde", 
                         "Finanças", "Marketing", "Vendas", "RH", "Consultoria", "Outro"]
                    )
                
                with col2:
                    role_level = st.selectbox(
                        "Nível Hierárquico",
                        ["Prefiro não informar", "Estudante", "Estagiário", "Júnior", 
                         "Pleno", "Sênior", "Coordenador", "Gerente", "Diretor", "C-Level"]
                    )
                    
                    team_size = st.selectbox(
                        "Tamanho da Equipe",
                        ["Prefiro não informar", "Trabalho sozinho", "2-5 pessoas", 
                         "6-15 pessoas", "16-50 pessoas", "50+ pessoas"]
                    )
            
            # Termos e condições
            terms_accepted = st.checkbox(
                "Aceito os [Termos de Uso](https://neuromap.com/terms) e [Política de Privacidade](https://neuromap.com/privacy)",
                help="Obrigatório para criar conta"
            )
            
            marketing_consent = st.checkbox(
                "Desejo receber insights e dicas sobre desenvolvimento pessoal por email",
                help="Opcional - você pode alterar isso depois"
            )
            
            submitted = st.form_submit_button(
                "✨ Criar Minha Conta",
                use_container_width=True,
                type="primary",
                disabled=not terms_accepted
            )
            
            if submitted:
                self._handle_registration(
                    email, password, confirm_password, first_name, last_name,
                    age_range, industry, role_level, team_size, marketing_consent
                )
    
    def _render_forgot_password_form(self) -> None:
        """Renderiza formulário de recuperação de senha"""
        
        st.markdown("### Esqueceu sua senha?")
        st.markdown("Sem problemas! Digite seu email e enviaremos um link para redefinir.")
        
        with st.form("forgot_password_form"):
            email = st.text_input(
                "📧 Email da conta",
                placeholder="seu@email.com"
            )
            
            submitted = st.form_submit_button(
                "📨 Enviar Link de Recuperação",
                use_container_width=True
            )
            
            if submitted:
                self._handle_forgot_password(email)
    
    def _handle_login(self, email: str, password: str, remember_me: bool) -> None:
        """Processa tentativa de login"""
        
        # Validações básicas
        if not email or not password:
            st.error("❌ Por favor, preencha email e senha")
            return
        
        if not self.email_validator.is_valid(email):
            st.error("❌ Formato de email inválido")
            return
        
        # Tentativa de login
        with st.spinner("🔐 Autenticando..."):
            try:
                result = self.auth_manager.sign_in(email, password)
                
                if result['success']:
                    # Armazena dados na sessão
                    st.session_state.user_id = result['user_id']
                    st.session_state.id_token = result['id_token']
                    st.session_state.user_email = email
                    st.session_state.remember_me = remember_me
                    
                    # Feedback de sucesso
                    st.success("✅ Login realizado com sucesso!")
                    st.balloons()
                    
                    # Rerun para atualizar interface
                    st.rerun()
                
                else:
                    st.error(f"❌ {result['message']}")
            
            except Exception as e:
                st.error(f"❌ Erro inesperado: {str(e)}")
                st.error("Tente novamente em alguns instantes")
    
    def _handle_registration(
        self, email: str, password: str, confirm_password: str,
        first_name: str, last_name: str, age_range: str, industry: str,
        role_level: str, team_size: str, marketing_consent: bool
    ) -> None:
        """Processa registro de nova conta"""
        
        # Validações
        validation_errors = []
        
        if not email or not password or not first_name or not last_name:
            validation_errors.append("Preencha todos os campos obrigatórios")
        
        if not self.email_validator.is_valid(email):
            validation_errors.append("Formato de email inválido")
        
        if password != confirm_password:
            validation_errors.append("Senhas não conferem")
        
        password_issues = self.password_validator.validate(password)
        if password_issues:
            validation_errors.extend(password_issues)
        
        if validation_errors:
            for error in validation_errors:
                st.error(f"❌ {error}")
            return
        
        # Tentativa de registro
        with st.spinner("📝 Criando sua conta..."):
            try:
                user_profile = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'age_range': age_range if age_range != "Prefiro não informar" else None,
                    'industry': industry if industry != "Prefiro não informar" else None,
                    'role_level': role_level if role_level != "Prefiro não informar" else None,
                    'team_size': team_size if team_size != "Prefiro não informar" else None,
                    'marketing_consent': marketing_consent,
                    'registration_date': st.session_state.get('timestamp', None)
                }
                
                result = self.auth_manager.create_account(email, password, user_profile)
                
                if result['success']:
                    st.success("✅ Conta criada com sucesso!")
                    st.info("📧 Verifique seu email para ativar a conta")
                    st.balloons()
                    
                    # Opcional: login automático após registro
                    if st.button("🚀 Fazer Login Agora"):
                        self._handle_login(email, password, False)
                
                else:
                    st.error(f"❌ {result['message']}")
            
            except Exception as e:
                st.error(f"❌ Erro ao criar conta: {str(e)}")
    
    def _handle_forgot_password(self, email: str) -> None:
        """Processa recuperação de senha"""
        
        if not email:
            st.error("❌ Digite seu email")
            return
        
        if not self.email_validator.is_valid(email):
            st.error("❌ Formato de email inválido")
            return
        
        with st.spinner("📨 Enviando email..."):
            try:
                result = self.auth_manager.reset_password(email)
                
                if result['success']:
                    st.success("✅ Email de recuperação enviado!")
                    st.info("📬 Verifique sua caixa de entrada e spam")
                else:
                    st.error(f"❌ {result['message']}")
            
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    
    def _show_password_strength(self, strength: dict) -> None:
        """Mostra indicador visual da força da senha"""
        
        score = strength['score']
        
        if score >= 4:
            st.success("🔒 Senha muito forte!")
        elif score >= 3:
            st.info("🔐 Senha forte")
        elif score >= 2:
            st.warning("⚠️ Senha média - considere melhorar")
        else:
            st.error("🚨 Senha fraca - use mais caracteres e símbolos")
        
        # Mostra sugestões
        if strength['suggestions']:
            with st.expander("💡 Dicas para melhorar sua senha"):
                for suggestion in strength['suggestions']:
                    st.write(f"• {suggestion}")
