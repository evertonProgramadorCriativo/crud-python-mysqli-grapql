
// Exibe o loader (carregando) no botão ao enviar formulário
function showLoader(btnId, loaderId, textId) {
    document.getElementById(btnId).disabled = true;
    document.getElementById(loaderId).classList.remove('hidden');
    document.getElementById(textId).classList.add('hidden');
}

// Exibe o modal de login na tela
function showLoginModal() {
    document.getElementById('loginModal').classList.add('show');
}


// Aguarda o carregamento da página e adiciona os eventos nos botões e formulários
document.addEventListener('DOMContentLoaded', function() {

    // Alterna para o formulário de login
    document.getElementById('loginTab').addEventListener('click', function() {
        document.getElementById('loginForm').classList.remove('hidden');
        document.getElementById('registerForm').classList.add('hidden');
        this.classList.add('tab-active');
        document.getElementById('registerTab').classList.remove('tab-active');
    });

    // Alterna para o formulário de registro
    document.getElementById('registerTab').addEventListener('click', function() {
        document.getElementById('registerForm').classList.remove('hidden');
        document.getElementById('loginForm').classList.add('hidden');
        this.classList.add('tab-active');
        document.getElementById('loginTab').classList.remove('tab-active');
    });

    // Processa o envio do formulário de login
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

    // Processa o envio do formulário de registro
    document.getElementById('registerForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const username = document.getElementById('registerUsername').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        showLoader('registerForm', 'registerLoader', 'registerBtnText');
        try {
            const message = await register(username, email, password);
            showNotification(message, 'success');
            // Volta para o formulário de login
            document.getElementById('loginTab').click();
        } catch (error) {
            showNotification('Erro no registro: ' + error.message, 'error');
        } finally {
            hideLoader('registerForm', 'registerLoader', 'registerBtnText');
        }
    });

    // Realiza logout ao clicar no botão
    document.getElementById('logoutBtn').addEventListener('click', logout);

});
 