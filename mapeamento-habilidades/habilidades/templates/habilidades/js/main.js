/**
 * main.js
 * Lógica JavaScript para o frontend do SkillMap.
 * Responsável por lidar com o envio de formulários para os Endpoints da API REST.
 */

// URL base da sua API (Seu time de backend definirá a porta e o host)
// Por enquanto, assumimos que a API está rodando no mesmo host (porta 8000)
const API_BASE_URL = '/api/v1'; 

// ------------------------------------------
// 1. Lógica de Registro de Usuário (POST /api/v1/auth/register/)
// ------------------------------------------

function setupRegistrationForm() {
    // 1. Obtenha o formulário de registro pelo ID (você deve dar um ID ao formulário em cadastro_perfil.html)
    const form = document.getElementById('registration-form');
    if (!form) {
        // console.log("Formulário de registro não encontrado. Ignorando a inicialização do JS de registro.");
        return;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // Impede o envio tradicional do formulário (quebra a arquitetura REST)

        // 2. Coletar dados do formulário
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Para o registro, o Django REST Framework (DRF) espera:
        // username, email, password, password2 (se UserCreationForm for usado como base), curso, campus
        
        try {
            // 3. Enviar dados para o endpoint de registro
            const response = await fetch(`${API_BASE_URL}/auth/register/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            // 4. Lidar com a Resposta
            const responseData = await response.json();

            if (response.ok) {
                // Registro bem-sucedido (Endpoint 1. POST /auth/register/)
                alert('Registro realizado com sucesso! Você será redirecionado para o login.');
                
                // Redireciona o usuário para a página de login
                window.location.href = '/login/'; 
            } else {
                // Erros de Validação da API (ex: senhas não conferem, nome de usuário já existe)
                console.error('Erro de registro:', responseData);
                
                // Função placeholder para mostrar erros na interface
                displayFormErrors(responseData); 
            }
        } catch (error) {
            console.error('Erro de conexão ou rede:', error);
            alert('Falha ao conectar ao servidor. Tente novamente.');
        }
    });
}

/**
 * Função placeholder para exibir mensagens de erro da API no formulário.
 * Sua equipe de frontend deve desenvolver essa função para ser amigável.
 * @param {object} errors - Objeto JSON contendo os erros da API.
 */
function displayFormErrors(errors) {
    // Limpar erros anteriores
    // ...

    // Exemplo: Iterar sobre os erros e mostrá-los perto dos campos
    for (const [key, value] of Object.entries(errors)) {
        const errorElement = document.getElementById(`error-${key}`);
        if (errorElement) {
            errorElement.textContent = Array.isArray(value) ? value.join(' ') : value;
        }
    }
    alert('Houve um erro na validação dos dados. Verifique o console para detalhes.');
}


// ------------------------------------------
// 2. Inicialização
// ------------------------------------------

// Inicializa as funções quando o DOM estiver completamente carregado
document.addEventListener('DOMContentLoaded', () => {
    setupRegistrationForm();
    // setupLoginForm(); // Será implementado depois
    // setupSearch(); // Será implementado depois
});