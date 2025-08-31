// Estado da aplicação
let currentUser = null;
let authToken = null;
let categories = [];
let currentEmailId = null;

// URLs da API
const API_BASE = 'http://localhost:5000';
const GRAPHQL_URL = `${API_BASE}/graphql`;

// Utilitários
function showNotification(message, type = 'info') {
const notification = document.getElementById('notification');
notification.textContent = message;
notification.className = `notification ${type} show`;
setTimeout(() => {
    notification.classList.remove('show');
}, 3000);
}

function showLoader(btnId, loaderId, textId) {
document.getElementById(btnId).disabled = true;
document.getElementById(loaderId).classList.remove('hidden');
document.getElementById(textId).classList.add('hidden');
}

function hideLoader(btnId, loaderId, textId) {
document.getElementById(btnId).disabled = false;
document.getElementById(loaderId).classList.add('hidden');
document.getElementById(textId).classList.remove('hidden');
}

// Requisições GraphQL
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

// Requisições REST
async function restRequest(url, options = {}) {
try {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    const response = await fetch(`${API_BASE}${url}`, {
        ...options,
        headers
    });

    const result = await response.json();
    
    if (!response.ok) {
        throw new Error(result.error || 'Erro na requisição');
    }

    return result;
} catch (error) {
    console.error('REST Error:', error);
    throw error;
}
}

// Autenticação
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
    localStorage.setItem('authToken', authToken);
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
    return true;
} else {
    throw new Error(data.loginUser.authPayload.message);
}
}

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
return data.registerUser.message;
}

function logout() {
authToken = null;
currentUser = null;
localStorage.removeItem('authToken');
localStorage.removeItem('currentUser');
showLoginModal();
}

// Interface
function showLoginModal() {
document.getElementById('loginModal').classList.add('show');
document.getElementById('mainApp').classList.add('hidden');
}

function hideLoginModal() {
document.getElementById('loginModal').classList.remove('show');
document.getElementById('mainApp').classList.remove('hidden');
updateUserInfo();
loadDashboard();
}

function updateUserInfo() {
const userInfo = document.getElementById('userInfo');
if (currentUser) {
    userInfo.textContent = `${currentUser.username} ${currentUser.isAdmin ? '(Admin)' : ''}`;
    
    // Mostrar tab admin se for admin
    if (currentUser.isAdmin) {
        document.getElementById('adminTab').classList.remove('hidden');
    }
}
}

function switchTab(activeTabId) {
// Desativar todas as tabs
const tabs = ['dashboardTab', 'classifyTab', 'emailsTab', 'uploadTab', 'adminTab'];
const contents = ['dashboardContent', 'classifyContent', 'emailsContent', 'uploadContent', 'adminContent'];

tabs.forEach(tabId => {
    const tab = document.getElementById(tabId);
    tab.classList.remove('border-blue-500', 'text-blue-600');
    tab.classList.add('text-gray-600');
});

contents.forEach(contentId => {
    document.getElementById(contentId).classList.add('hidden');
});

// Ativar tab selecionada
const activeTab = document.getElementById(activeTabId);
activeTab.classList.add('border-blue-500', 'text-blue-600');
activeTab.classList.remove('text-gray-600');

// Mostrar conteúdo correspondente
const contentMap = {
    'dashboardTab': 'dashboardContent',
    'classifyTab': 'classifyContent', 
    'emailsTab': 'emailsContent',
    'uploadTab': 'uploadContent',
    'adminTab': 'adminContent'
};

const contentId = contentMap[activeTabId];
if (contentId) {
    document.getElementById(contentId).classList.remove('hidden');
}

// Carregar dados específicos da tab
switch(activeTabId) {
    case 'dashboardTab':
        loadDashboard();
        break;
    case 'classifyTab':
        loadCategories();
        break;
    case 'emailsTab':
        loadEmails();
        break;
    case 'adminTab':
        loadAdminData();
        break;
}
}

// Dashboard
async function loadDashboard() {
try {
    const stats = await restRequest('/stats');
    
    document.getElementById('totalEmails').textContent = stats.total_emails;
    document.getElementById('totalUsers').textContent = stats.total_users;
    document.getElementById('totalFeedback').textContent = stats.total_feedback;
    document.getElementById('avgConfidence').textContent = `${Math.round(stats.avg_confidence * 100)}%`;

    // Gráfico de categorias
    const chartContainer = document.getElementById('categoryChart');
    chartContainer.innerHTML = '';
    
    if (stats.emails_by_category && stats.emails_by_category.length > 0) {
        const maxCount = Math.max(...stats.emails_by_category.map(item => item.count));
        
        stats.emails_by_category.forEach(item => {
            const percentage = maxCount > 0 ? (item.count / maxCount) * 100 : 0;
            
            const categoryItem = document.createElement('div');
            categoryItem.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg';
            categoryItem.innerHTML = `
                <span class="font-medium text-gray-700">${item.category}</span>
                <div class="flex items-center space-x-3">
                    <div class="w-32 h-2 bg-gray-200 rounded-full">
                        <div class="h-2 bg-blue-500 rounded-full" style="width: ${percentage}%"></div>
                    </div>
                    <span class="text-sm text-gray-600 w-8 text-right">${item.count}</span>
                </div>
            `;
            chartContainer.appendChild(categoryItem);
        });
    }
} catch (error) {
    showNotification('Erro ao carregar dashboard: ' + error.message, 'error');
}
}

// Classificação
async function loadCategories() {
try {
    const query = `
        query {
            categories {
                id
                name
                description
                color
            }
        }
    `;

    const data = await graphqlRequest(query);
    categories = data.categories;
    
    // Atualizar select de feedback
    const feedbackSelect = document.getElementById('feedbackCategory');
    feedbackSelect.innerHTML = '<option value="">Selecione...</option>';
    
    categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat.id;
        option.textContent = cat.name;
        feedbackSelect.appendChild(option);
    });
} catch (error) {
    showNotification('Erro ao carregar categorias: ' + error.message, 'error');
}
}

async function classifyEmail(sender, subject, body) {
const mutation = `
    mutation ClassifyEmail($sender: String!, $subject: String!, $body: String!) {
        classifyEmail(sender: $sender, subject: $subject, body: $body) {
            email {
                id
                categoryId
                categoryName
                confidenceScore
                suggestedResponse
            }
            message
        }
    }
`;

const data = await graphqlRequest(mutation, { sender, subject, body });
return data.classifyEmail;
}

function displayClassificationResult(result) {
const resultDiv = document.getElementById('classificationResult');
const email = result.email;

// Encontrar categoria
const category = categories.find(cat => cat.id == email.categoryId);
const categoryColor = category ? category.color : '#6c757d';

document.getElementById('resultCategory').textContent = email.categoryName;
document.getElementById('resultCategory').style.backgroundColor = categoryColor;

const confidence = Math.round(email.confidenceScore * 100);
document.getElementById('resultConfidence').textContent = `${confidence}%`;
document.getElementById('resultConfidenceBar').style.width = `${confidence}%`;

// Cor da barra baseada na confiança
const confidenceBar = document.getElementById('resultConfidenceBar');
if (confidence >= 80) {
    confidenceBar.className = 'confidence-fill bg-green-500';
} else if (confidence >= 60) {
    confidenceBar.className = 'confidence-fill bg-yellow-500';
} else {
    confidenceBar.className = 'confidence-fill bg-red-500';
}

document.getElementById('suggestedResponse').textContent = email.suggestedResponse;

currentEmailId = email.id;
resultDiv.classList.remove('hidden');
}

async function submitFeedback() {
if (!currentEmailId) return;

const correctedCategoryId = document.getElementById('feedbackCategory').value;
const feedbackText = document.getElementById('feedbackText').value;

if (!correctedCategoryId) {
    showNotification('Por favor, selecione a categoria correta', 'error');
    return;
}

try {
    const mutation = `
        mutation AddFeedback($emailId: Int!, $correctedCategoryId: Int!, $feedbackText: String) {
            addFeedback(emailId: $emailId, correctedCategoryId: $correctedCategoryId, feedbackText: $feedbackText) {
                feedback {
                    id
                }
                message
            }
        }
    `;

    await graphqlRequest(mutation, {
        emailId: parseInt(currentEmailId),
        correctedCategoryId: parseInt(correctedCategoryId),
        feedbackText
    });

    showNotification('Feedback enviado com sucesso!', 'success');
    
    // Limpar formulário
    document.getElementById('feedbackCategory').value = '';
    document.getElementById('feedbackText').value = '';
    
} catch (error) {
    showNotification('Erro ao enviar feedback: ' + error.message, 'error');
}
}

// Emails
async function loadEmails() {
try {
    const query = `
        query {
            emails {
                id
                sender
                subject
                body
                categoryName
                confidenceScore
                createdAt
            }
        }
    `;

    const data = await graphqlRequest(query);
    const emails = data.emails;
    
    const tbody = document.getElementById('emailsTableBody');
    tbody.innerHTML = '';
    
    emails.forEach(email => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';
        
        const confidence = Math.round(email.confidenceScore * 100);
        const date = new Date(email.createdAt).toLocaleDateString('pt-BR');
        
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${email.sender}</td>
            <td class="px-6 py-4 text-sm text-gray-900">
                <div class="max-w-xs truncate" title="${email.subject}">${email.subject}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="category-badge" style="background-color: #3b82f6;">${email.categoryName}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${confidence}%</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${date}</td>
        `;
        
        tbody.appendChild(row);
    });
    
} catch (error) {
    showNotification('Erro ao carregar emails: ' + error.message, 'error');
}
}

// Upload em lote
async function processEmailBatch(emailsData) {
try {
    const result = await restRequest('/upload_emails', {
        method: 'POST',
        body: JSON.stringify({ emails: emailsData })
    });
    
    return result;
} catch (error) {
    throw error;
}
}

function displayUploadResult(result) {
const resultDiv = document.getElementById('uploadResult');
const contentDiv = document.getElementById('uploadResultContent');

if (result.success) {
    resultDiv.className = 'mt-6 p-4 rounded-lg bg-green-50 border border-green-200';
    contentDiv.innerHTML = `
        <div class="flex items-center text-green-800">
            <i class="fas fa-check-circle mr-2"></i>
            <span class="font-medium">${result.message}</span>
        </div>
        <div class="mt-2 text-sm text-green-700">
            ${result.emails.length} emails foram processados e classificados.
        </div>
    `;
} else {
    resultDiv.className = 'mt-6 p-4 rounded-lg bg-red-50 border border-red-200';
    contentDiv.innerHTML = `
        <div class="flex items-center text-red-800">
            <i class="fas fa-exclamation-circle mr-2"></i>
            <span class="font-medium">Erro no processamento</span>
        </div>
    `;
}

resultDiv.classList.remove('hidden');
}

// Admin
async function loadAdminData() {
await loadCategories();
displayCategories();
}

function displayCategories() {
const container = document.getElementById('categoriesList');
container.innerHTML = '';

categories.forEach(category => {
    const categoryDiv = document.createElement('div');
    categoryDiv.className = 'flex items-center justify-between p-3 bg-gray-50 rounded';
    categoryDiv.innerHTML = `
        <div class="flex items-center">
            <div class="w-4 h-4 rounded-full mr-3" style="background-color: ${category.color}"></div>
            <div>
                <div class="font-medium text-gray-900">${category.name}</div>
                <div class="text-sm text-gray-600">${category.description}</div>
            </div>
        </div>
    `;
    container.appendChild(categoryDiv);
});
}

async function retrainModel() {
try {
    const result = await restRequest('/retrain', {
        method: 'POST'
    });
    
    const resultDiv = document.getElementById('retrainResult');
    
    if (result.success) {
        resultDiv.className = 'mt-4 p-3 rounded bg-green-50 border border-green-200 text-green-800';
        resultDiv.textContent = result.message;
    } else {
        resultDiv.className = 'mt-4 p-3 rounded bg-red-50 border border-red-200 text-red-800';
        resultDiv.textContent = 'Erro no retreinamento';
    }
    
    resultDiv.classList.remove('hidden');
    
} catch (error) {
    const resultDiv = document.getElementById('retrainResult');
    resultDiv.className = 'mt-4 p-3 rounded bg-red-50 border border-red-200 text-red-800';
    resultDiv.textContent = 'Erro: ' + error.message;
    resultDiv.classList.remove('hidden');
}
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
// Verificar se há token salvo
const savedToken = localStorage.getItem('authToken');
const savedUser = localStorage.getItem('currentUser');

if (savedToken && savedUser) {
    authToken = savedToken;
    currentUser = JSON.parse(savedUser);
    hideLoginModal();
} else {
    showLoginModal();
}

// Tabs de login/registro
document.getElementById('loginTab').addEventListener('click', function() {
    document.getElementById('loginForm').classList.remove('hidden');
    document.getElementById('registerForm').classList.add('hidden');
    this.classList.add('tab-active');
    document.getElementById('registerTab').classList.remove('tab-active');
});

document.getElementById('registerTab').addEventListener('click', function() {
    document.getElementById('registerForm').classList.remove('hidden');
    document.getElementById('loginForm').classList.add('hidden');
    this.classList.add('tab-active');
    document.getElementById('loginTab').classList.remove('tab-active');
});

// Login form
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    showLoader('loginForm', 'loginLoader', 'loginBtnText');
    
    try {
        await login(username, password);
        hideLoginModal();
        showNotification('Login realizado com sucesso!', 'success');
    } catch (error) {
        showNotification('Erro no login: ' + error.message, 'error');
    } finally {
        hideLoader('loginForm', 'loginLoader', 'loginBtnText');
    }
});

// Register form
document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    showLoader('registerForm', 'registerLoader', 'registerBtnText');
    
    try {
        const message = await register(username, email, password);
        showNotification(message, 'success');
        
        // Voltar para login
        document.getElementById('loginTab').click();
    } catch (error) {
        showNotification('Erro no registro: ' + error.message, 'error');
    } finally {
        hideLoader('registerForm', 'registerLoader', 'registerBtnText');
    }
});

// Logout
document.getElementById('logoutBtn').addEventListener('click', logout);

// Navigation tabs
document.getElementById('dashboardTab').addEventListener('click', () => switchTab('dashboardTab'));
document.getElementById('classifyTab').addEventListener('click', () => switchTab('classifyTab'));
document.getElementById('emailsTab').addEventListener('click', () => switchTab('emailsTab'));
document.getElementById('uploadTab').addEventListener('click', () => switchTab('uploadTab'));
document.getElementById('adminTab').addEventListener('click', () => switchTab('adminTab'));

// Classificar email form
document.getElementById('classifyForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const sender = document.getElementById('emailSender').value;
    const subject = document.getElementById('emailSubject').value;
    const body = document.getElementById('emailBody').value;
    
    showLoader('classifyForm', 'classifyLoader', 'classifyBtnText');
    
    try {
        const result = await classifyEmail(sender, subject, body);
        displayClassificationResult(result);
        showNotification('Email classificado com sucesso!', 'success');
    } catch (error) {
        showNotification('Erro na classificação: ' + error.message, 'error');
    } finally {
        hideLoader('classifyForm', 'classifyLoader', 'classifyBtnText');
    }
});

// Submit feedback
document.getElementById('submitFeedback').addEventListener('click', submitFeedback);

// Refresh emails
document.getElementById('refreshEmails').addEventListener('click', loadEmails);

// Upload file
document.getElementById('selectFileBtn').addEventListener('click', function() {
    document.getElementById('fileUpload').click();
});

document.getElementById('fileUpload').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file && file.type === 'application/json') {
        const reader = new FileReader();
        reader.onload = function(event) {
            document.getElementById('jsonInput').value = event.target.result;
        };
        reader.readAsText(file);
    }
});

// Upload batch
document.getElementById('uploadBtn').addEventListener('click', async function() {
    const jsonInput = document.getElementById('jsonInput').value;
    
    if (!jsonInput.trim()) {
        showNotification('Por favor, forneça os dados JSON', 'error');
        return;
    }
    
    try {
        const data = JSON.parse(jsonInput);
        
        if (!data.emails || !Array.isArray(data.emails)) {
            throw new Error('Formato inválido: esperado objeto com array "emails"');
        }
        
        showLoader('uploadBtn', 'uploadLoader', 'uploadBtnText');
        
        const result = await processEmailBatch(data.emails);
        displayUploadResult(result);
        showNotification('Upload processado com sucesso!', 'success');
        
    } catch (error) {
        if (error instanceof SyntaxError) {
            showNotification('JSON inválido: ' + error.message, 'error');
        } else {
            showNotification('Erro no upload: ' + error.message, 'error');
        }
    } finally {
        hideLoader('uploadBtn', 'uploadLoader', 'uploadBtnText');
    }
});

// Retrain model
document.getElementById('retrainBtn').addEventListener('click', async function() {
    showLoader('retrainBtn', 'retrainLoader', 'retrainBtnText');
    
    try {
        await retrainModel();
    } finally {
        hideLoader('retrainBtn', 'retrainLoader', 'retrainBtnText');
    }
});
});