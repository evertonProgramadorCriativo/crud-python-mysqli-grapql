#  Sistema Inteligente de Classificação de Emails

##  Resumo do Projeto

Um sistema completo com  a Tecnologia **Python** , **MySQL Connector Python** e **GraphQL**  de classificação **automática** de emails.

A plataforma combina **Machine Learning** com **GraphQL** para oferecer uma solução robusta de organização e resposta automática de emails corporativos.


[![MySQL Connector Python](https://img.shields.io/badge/MySQL_Connector_Python-8.1.0-4479A1)](https://dev.mysql.com/doc/connector-python/en/)
[![Graphene](https://img.shields.io/badge/Graphene-2.1.9-E10098)](https://graphene-python.org/)
[![GraphQL Core](https://img.shields.io/badge/GraphQL_Core-2.3.2-E535AB)](https://graphql-core.readthedocs.io/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-000000)](https://flask.palletsprojects.com/)
[![Flask GraphQL](https://img.shields.io/badge/Flask_GraphQL-2.0.1-0080FF)](https://github.com/graphql-python/flask-graphql)
[![Flask CORS](https://img.shields.io/badge/Flask_CORS-4.0.0-FF7F50)](https://flask-cors.readthedocs.io/)
[![PyJWT](https://img.shields.io/badge/PyJWT-2.8.0-000000)](https://pyjwt.readthedocs.io/)
[![Bcrypt](https://img.shields.io/badge/Bcrypt-4.2.0-FF6B6B)](https://github.com/pyca/bcrypt/)
[![Scikit Learn](https://img.shields.io/badge/Scikit_Learn-1.7.1-F7931E)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.2.2-150458)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-2.1.1-013243)](https://numpy.org/)
[![NLTK](https://img.shields.io/badge/NLTK-3.9-4B8BBE)](https://www.nltk.org/)


---
1. **Rodando o Projeto**  
   ```bash
   projeto/ 

   pip install -r requirements.txt # Instalação dos pacotes
   python app.py # Start o Projeto

   ```
  Rota: http://localhost:5000/graphql

```bash
# Mutation para login
mutation {
  loginUser(username: "admin", password: "admin123") {
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

# Mutation para registro de novo usuário
mutation {
  registerUser(
    username: "novousuario"
    email: "novo@email.com" 
    password: "senha123"
  ) {
    user {
      id
      username
      email
      isAdmin
    }
    message
  }
}

```

```bash
# Buscar Email Específico
query {
  email(id: 1) {
    id
    sender
    subject
    body
    categoryName
    suggestedResponse
  }
}

# Classificar Email
mutation {
  classifyEmail(sender: "cliente@empresa.com", subject: "Problema no sistema", body: "Preciso de ajuda urgente com o sistema que não está funcionando") {
    email {
      id
      categoryName
      confidenceScore
      suggestedResponse
    }
    message
  }
}

# Adicionar Feedback

mutation {
  addFeedback(emailId: 1, correctedCategoryId: 2, feedbackText: "Categoria corrigida manualmente") {
    feedback {
      id
    }
    message
  }
}

```
##  O que o sistema faz
-  **Classificação Automática:** Usa algoritmo **Naive Bayes** para categorizar emails em **6 categorias**
-  **Dashboard Interativo:** Interface web com estatísticas e visualizações
-  **Autenticação Segura:** Sistema **JWT** com diferentes níveis de permissão
-  **Respostas Automáticas:** Gera sugestões de resposta baseadas na categoria
-  **Aprendizado Contínuo:** Sistema de feedback para melhorar o modelo AI
-  **Upload em Lote:** Processamento múltiplo de emails via **JSON**

---

##  Categorias Suportadas
-  **Suporte Técnico**
-  **Vendas**
-  **Marketing**
-  **Recursos Humanos**
-  **Financeiro**
-  **Geral**

---



### 📋 Pré-requisitos
- Python **3.8+**
- MySQL Server **5.7+**
- pip (gerenciador de pacotes Python)

---

![Formulario](https://i.ibb.co/sds18ryD/Screenshot-19.png) 
![Estrutura do Projeto](https://i.ibb.co/B22DLyTz/Screenshot-21.png) 