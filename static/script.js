// Estado da aplicação
let currentUser = null;
let authToken = null;
let categories = [];
let currentEmailId = null;

// URLs da API
const API_BASE = 'http://localhost:5000';
const GRAPHQL_URL = `${API_BASE}/graphql`;

// ========== UTILITÁRIOS ==========

/**
 * Exibe notificação para o usuário
 * @param {string} message - Mensagem a ser exibida
 * @param {string} type - Tipo da notificação (success, error, info)
 */
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.innerHTML = `<i class="fas fa-${getNotificationIcon(type)} mr-2"></i>${message}`;
    notification.className = `notification ${type} show`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}

/**
 * Retorna o ícone apropriado para cada tipo de notificação
 * @param {string} type - Tipo da notificação
 * @returns {string} Nome do ícone
 */
function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        default: return 'info-circle';
    }
}

/**
 * Exibe o loader no botão durante operações assíncronas
 * @param {string} formId - ID do formulário
 * @param {string} loaderId - ID do elemento de loading
 * @param {string} textId - ID do texto do botão
 */
function showLoader(formId, loaderId, textId) {
    const form = document.getElementById(formId);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    submitBtn.disabled = true;
    document.getElementById(loaderId).classList.remove('hidden');
    document.getElementById(textId).classList.add('hidden');
    form.classList.add('form-loading');
}

/**
 * Oculta o loader do botão
 * @param {string} formId - ID do formulário
 * @param {string} loaderId - ID do elemento de loading
 * @param {string} textId - ID do texto do botão
 */
function hideLoader(formId, loaderId, textId) {
    const form = document.getElementById(formId);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    submitBtn.disabled = false;
    document.getElementById(loaderId).classList.add('hidden');
    document.getElementById(textId).classList.remove('hidden');
    form.classList.remove('form-loading');
}

// ========== MODAL E UI ==========

/**
 * Exibe o modal de login
 */
function showLoginModal() {
    document.getElementById('loginModal').classList.add('show');
    document.getElementById('mainContent').classList.remove('show');
    document.getElementById('userInfo').classList.remove('show');
}

/**
 * Oculta o modal de login e exibe o conteúdo principal
 */
function hideLoginModal() {
    document.getElementById('loginModal').classList.remove('show');
    document.getElementById('mainContent').classList.add('show');
    document.getElementById('userInfo').classList.add('show');
}

/**
 * Atualiza as informações do usuário na interface
 * @param {Object} user - Dados do usuário
 */
function updateUserInfo(user) {
    document.getElementById('userName').textContent = user.username;
    document.getElementById('userEmail').textContent = user.email;
    document.getElementById('userAvatar').textContent = user.username.charAt(0).toUpperCase();
    
    // Adicionar indicador de admin se necessário
    const userNameElement = document.getElementById('userName');
    if (user.isAdmin) {
        userNameElement.innerHTML = `${user.username} <span class="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full ml-2">Admin</span>`;
    }
}

/**
 * Limpa os formulários de login e registro
 */
function clearForms() {
    // Limpar formulário de login
    document.getElementById('loginUsername').value = '';
    document.getElementById('loginPassword').value = '';
    
    // Limpar formulário de registro
    document.getElementById('registerUsername').value = '';
    document.getElementById('registerEmail').value = '';
    document.getElementById('registerPassword').value = '';
}

// ========== REQUISIÇÕES GRAPHQL ==========

/**
 * Realiza requisições GraphQL
 * @param {string} query - Query GraphQL
 * @param {Object} variables - Variáveis da query
 * @returns {Promise<Object>} Dados da resposta
 */
async function graphqlRequest(query, variables = {}) {
    try {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }

        const response = await fetch(GRAPHQL_URL, {
            method: 'POST',
            headers,
            body: JSON.stringify({ query, variables })
        });

        const result = await response.json();
        
        if (result.errors) {
            throw new Error(result.errors[0].message);
        }

        return result.data;
    } catch (error) {
        console.error('GraphQL Error:', error);
        throw error;
    }
}

// ========== AUTENTICAÇÃO ==========

/**
 * Realiza login do usuário
 * @param {string} username - Nome do usuário
 * @param {string} password - Senha do usuário
 * @returns {Promise<Object>} Resultado do login
 */
async function login(username, password) {
    const query = `
        mutation LoginUser($username: String!, $password: String!) {
            loginUser(username: $username, password: $password) {
                authPayload {
                    token
                    user {
                        id
                        username
                        email
                        isAdmin
                    }
                    message
                }
            }
        }
    `;

    const data = await graphqlRequest(query, { username, password });

    if (data.loginUser.authPayload.token) {
        authToken = data.loginUser.authPayload.token;
        currentUser = data.loginUser.authPayload.user;
        
        // Salvar no localStorage
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        
        // Atualizar interface
        updateUserInfo(currentUser);
        
        return { 
            success: true, 
            message: data.loginUser.authPayload.message,
            user: currentUser
        };
    } else {
        throw new Error(data.loginUser.authPayload.message);
    }
}

/**
 * Registra novo usuário
 * @param {string} username - Nome do usuário
 * @param {string} email - Email do usuário  
 * @param {string} password - Senha do usuário
 * @returns {Promise<string>} Mensagem de sucesso
 */
async function register(username, email, password) {
    const query = `
        mutation RegisterUser($username: String!, $email: String!, $password: String!) {
            registerUser(username: $username, email: $email, password: $password) {
                user {
                    id
                    username
                    email
                }
                message
            }
        }
    `;

    const data = await graphqlRequest(query, { username, email, password });
    
    if (data.registerUser.user) {
        // Após registrar com sucesso, fazer login automaticamente
        await login(username, password);
        return data.registerUser.message;
    } else {
        throw new Error(data.registerUser.message);
    }
}

/**
 * Realiza logout do usuário
 */
function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    
    clearForms();
    showLoginModal();
    showNotification('Logout realizado com sucesso!', 'info');
}

/**
 * Verifica se há um token salvo ao carregar a página
 */
function checkAuthOnLoad() {
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('currentUser');
    
    if (savedToken && savedUser) {
        try {
            authToken = savedToken;
            currentUser = JSON.parse(savedUser);
            updateUserInfo(currentUser);
            hideLoginModal();
            
            // Mostrar notificação de boas-vindas
            setTimeout(() => {
                showNotification(`Bem-vindo de volta, ${currentUser.username}!`, 'success');
            }, 500);
        } catch (error) {
            console.error('Erro ao recuperar dados do usuário:', error);
            logout();
        }
    }
}

// ========== EVENT LISTENERS ==========

/**
 * Configura todos os event listeners da aplicação
 */
function setupEventListeners() {
    // Alternância entre tabs de login e registro
    document.getElementById('loginTab').addEventListener('click', function () {
        document.getElementById('loginForm').classList.remove('hidden');
        document.getElementById('registerForm').classList.add('hidden');
        this.classList.add('tab-active');
        document.getElementById('registerTab').classList.remove('tab-active');
    });

    document.getElementById('registerTab').addEventListener('click', function () {
        document.getElementById('registerForm').classList.remove('hidden');
        document.getElementById('loginForm').classList.add('hidden');
        this.classList.add('tab-active');
        document.getElementById('loginTab').classList.remove('tab-active');
    });

    // Processamento do formulário de login
    document.getElementById('loginForm').addEventListener('submit', async function (e) {
        e.preventDefault();
        
        const username = document.getElementById('loginUsername').value.trim();
        const password = document.getElementById('loginPassword').value;

        if (!username || !password) {
            showNotification('Por favor, preencha todos os campos', 'error');
            return;
        }

        showLoader('loginForm', 'loginLoader', 'loginBtnText');
        
        try {
            const result = await login(username, password);
            hideLoginModal();
            clearForms();
            
            const welcomeMessage = currentUser.isAdmin 
                ? `Bem-vindo, Admin ${currentUser.username}! Acesso total concedido.`
                : `Bem-vindo, ${currentUser.username}! Login realizado com sucesso.`;
            
            showNotification(welcomeMessage, 'success');
            
        } catch (error) {
            showNotification('Erro no login: ' + error.message, 'error');
        } finally {
            hideLoader('loginForm', 'loginLoader', 'loginBtnText');
        }
    });

    // Processamento do formulário de registro
    document.getElementById('registerForm').addEventListener('submit', async function (e) {
        e.preventDefault();
        
        const username = document.getElementById('registerUsername').value.trim();
        const email = document.getElementById('registerEmail').value.trim();
        const password = document.getElementById('registerPassword').value;

        if (!username || !email || !password) {
            showNotification('Por favor, preencha todos os campos', 'error');
            return;
        }

        if (password.length < 6) {
            showNotification('A senha deve ter pelo menos 6 caracteres', 'error');
            return;
        }

        showLoader('registerForm', 'registerLoader', 'registerBtnText');
        
        try {
            await register(username, email, password);
            hideLoginModal();
            clearForms();
            
            showNotification(`🎉 Conta criada com sucesso! Bem-vindo ao sistema, ${currentUser.username}!`, 'success');
            
            // Voltar para a aba de login para próximas visitas
            document.getElementById('loginTab').click();
            
        } catch (error) {
            showNotification('Erro no registro: ' + error.message, 'error');
        } finally {
            hideLoader('registerForm', 'registerLoader', 'registerBtnText');
        }
    });

    // Botão de logout
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Fechar modal ao clicar fora dele (opcional)
    document.getElementById('loginModal').addEventListener('click', function(e) {
        if (e.target === this) {
            // Não permitir fechar se não estiver logado
            if (!currentUser) {
                showNotification('É necessário fazer login para continuar', 'info');
            }
        }
    });

    // Atalhos de teclado
    document.addEventListener('keydown', function(e) {
        // ESC para logout (apenas se logado)
        if (e.key === 'Escape' && currentUser) {
            logout();
        }
        
        // Enter no modal para submeter o formulário visível
        if (e.key === 'Enter' && document.getElementById('loginModal').classList.contains('show')) {
            const loginFormVisible = !document.getElementById('loginForm').classList.contains('hidden');
            const registerFormVisible = !document.getElementById('registerForm').classList.contains('hidden');
            
            if (loginFormVisible) {
                document.getElementById('loginForm').dispatchEvent(new Event('submit'));
            } else if (registerFormVisible) {
                document.getElementById('registerForm').dispatchEvent(new Event('submit'));
            }
        }
    });
}

// ========== INICIALIZAÇÃO ==========

/**
 * Inicializa a aplicação
 */
function initApp() {
    console.log('🚀 Iniciando Classificador de Emails...');
    
    // Verificar autenticação existente
    checkAuthOnLoad();
    
    // Configurar event listeners
    setupEventListeners();
    
    console.log('✅ Aplicação inicializada com sucesso!');
}

// Aguarda o carregamento da página
document.addEventListener('DOMContentLoaded', initApp);

// ========== EXPORT PARA POSSÍVEL USO FUTURO ==========
// Se houver necessidade de usar essas funções em outros arquivos
window.AppAuth = {
    login,
    register,
    logout,
    getCurrentUser: () => currentUser,
    getAuthToken: () => authToken,
    showNotification
};