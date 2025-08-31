# app.py
from flask import Flask, request, jsonify , render_template
from flask_graphql import GraphQLView
from flask_cors import CORS
import jwt


# Imports das classes 
from database import Database
from schema import schema
 

#  Cria uma instância da aplicação Flask
# __name__ é uma variável especial que representa o nome do módulo atual
app = Flask(__name__)
CORS(app)

# Inicializar componentes
try:
    db = Database()
    print("Start!")
except Exception as e:
    print(f"Erro ao inicializar Banco de dados: {e}")
    db = None
   

def get_current_user(token):
    """Extrai informações do usuário do token JWT"""
    if not token or not db:
        return None, False
    
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])
        user_id = payload['user_id']
        
        cursor = db.connection.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        
        if user_data:
            return user_id, user_data[0]
        return None, False
    except Exception as e:
        print(f"Erro na autenticação: {e}")
        return None, False

class GraphQLContext:
    def __init__(self):
        self.db = db
        
        
        # Extrair token do cabeçalho
        auth_header = request.headers.get('Authorization')
        user_id, is_admin = get_current_user(auth_header)
        
        self.user_id = user_id
        self.is_admin = is_admin

# Configurar GraphQL endpoint
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True,
        get_context=lambda: GraphQLContext()
    )
)


@app.route('/')
def index():
    """Página inicial - servir HTML"""
    return render_template('index.html')


    
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

if __name__ == '__main__':
    
    # Inicia servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5000)