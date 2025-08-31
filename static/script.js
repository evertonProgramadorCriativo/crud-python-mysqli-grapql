 document.addEventListener('DOMContentLoaded', function() {
            const helloBtn = document.getElementById('helloBtn');
            const messagesContainer = document.getElementById('messagesContainer');
            const counterElement = document.getElementById('counter');
            let counter = 0;
            
            helloBtn.addEventListener('click', function() {
                // Incrementar o contador
                counter++;
                counterElement.textContent = counter;
                
                // Criar uma nova mensagem
                const message = document.createElement('div');
                message.className = 'message';
                message.textContent = `${counter}. Olá Mundo!`;
                
                // Adicionar a mensagem ao container
                messagesContainer.appendChild(message);
                
                // Rolar para a mensagem mais recente
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            });
        });