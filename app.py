from flask import Flask, request, jsonify , render_template
from flask_graphql import GraphQLView
from flask_cors import CORS
import jwt
import traceback
import os
# Imports das classes 
from database import Database
from ai_classifier import EmailClassifier
from schema import schema

app = Flask(__name__)
CORS(app)
# Usar variável de ambiente para a chave secreta
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

# Inicializar componentes
try:
    db = Database()
    classifier = EmailClassifier()
    print("Componentes inicializados com sucesso!")
except Exception as e:
    print(f"Erro ao inicializar componentes: {e}")
    db = None
    classifier = None

def get_current_user(token):
    """Extrai informações do usuário do token JWT"""
    if not token or not db:
        return None, False
    
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
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
        self.classifier = classifier
        
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

@app.route('/retrain', methods=['POST'])
def retrain_model():
    """Endpoint para retreinar o modelo com feedback"""
    if not db or not classifier:
        return jsonify({'error': 'Sistema não inicializado'}), 500
    
    auth_header = request.headers.get('Authorization')
    user_id, is_admin = get_current_user(auth_header)
    
    if not user_id or not is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        # Buscar dados de feedback
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT e.subject, e.body, f.corrected_category_id
            FROM feedback f
            JOIN emails e ON f.email_id = e.id
            WHERE f.corrected_category_id IS NOT NULL
        """)
        
        feedback_data = []
        for row in cursor.fetchall():
            feedback_data.append({
                'subject': row[0],
                'body': row[1],
                'correct_category_id': row[2]
            })
        
        # Retreinar modelo
        classifier.retrain_with_feedback(feedback_data)
        
        return jsonify({
            'message': f'Modelo retreinado com {len(feedback_data)} exemplos de feedback',
            'success': True
        })
    
    except Exception as e:
        print(f"Erro no retreinamento: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload_emails', methods=['POST'])
def upload_emails():
    """Endpoint para upload de emails em lote"""
    if not db or not classifier:
        return jsonify({'error': 'Sistema não inicializado'}), 500
    
    auth_header = request.headers.get('Authorization')
    user_id, is_admin = get_current_user(auth_header)
    
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        emails_data = request.json.get('emails', [])
        processed_emails = []
        
        cursor = db.connection.cursor()
        
        for email_data in emails_data:
            sender = email_data.get('sender', '')
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            
            if not all([sender, subject, body]):
                continue
            
            # Classificar email
            category_id, confidence = classifier.classify_email(subject, body)
            suggested_response = classifier.generate_response(category_id, subject, body)
            
            # Salvar no banco
            cursor.execute("""
                INSERT INTO emails (sender, subject, body, category_id, confidence_score, 
                                  suggested_response, user_id, is_processed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (sender, subject, body, category_id, confidence, suggested_response, user_id, True))
            
            processed_emails.append({
                'id': cursor.lastrowid,
                'sender': sender,
                'subject': subject,
                'category_id': category_id,
                'confidence': confidence
            })
        
        db.connection.commit()
        
        return jsonify({
            'message': f'{len(processed_emails)} emails processados com sucesso',
            'emails': processed_emails,
            'success': True
        })
    
    except Exception as e:
        print(f"Erro no upload: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Endpoint para estatísticas do sistema"""
    if not db:
        return jsonify({'error': 'Sistema não inicializado'}), 500
    
    auth_header = request.headers.get('Authorization')
    user_id, is_admin = get_current_user(auth_header)
    
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        cursor = db.connection.cursor()
        
        # Estatísticas gerais
        if is_admin:
            # Total de emails
            cursor.execute("SELECT COUNT(*) FROM emails")
            total_emails = cursor.fetchone()[0]
            
            # Emails por categoria
            cursor.execute("""
                SELECT c.name, COUNT(e.id) as count
                FROM categories c
                LEFT JOIN emails e ON c.id = e.category_id
                GROUP BY c.id, c.name
                ORDER BY count DESC
            """)
            emails_by_category = [{'category': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # Total de usuários
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            # Feedback recebido
            cursor.execute("SELECT COUNT(*) FROM feedback")
            total_feedback = cursor.fetchone()[0]
        else:
            # Estatísticas do usuário atual
            cursor.execute("SELECT COUNT(*) FROM emails WHERE user_id = %s", (user_id,))
            total_emails = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT c.name, COUNT(e.id) as count
                FROM categories c
                LEFT JOIN emails e ON c.id = e.category_id AND e.user_id = %s
                GROUP BY c.id, c.name
                ORDER BY count DESC
            """, (user_id,))
            emails_by_category = [{'category': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            total_users = 1  # Apenas o usuário atual
            
            cursor.execute("SELECT COUNT(*) FROM feedback WHERE user_id = %s", (user_id,))
            total_feedback = cursor.fetchone()[0]
        
        # Confiança média das classificações
        if is_admin:
            cursor.execute("SELECT AVG(confidence_score) FROM emails WHERE confidence_score > 0")
        else:
            cursor.execute("SELECT AVG(confidence_score) FROM emails WHERE user_id = %s AND confidence_score > 0", (user_id,))
        
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        return jsonify({
            'total_emails': total_emails,
            'total_users': total_users,
            'total_feedback': total_feedback,
            'avg_confidence': round(float(avg_confidence), 3),
            'emails_by_category': emails_by_category,
            'success': True
        })
    
    except Exception as e:
        print(f"Erro nas estatísticas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Página inicial - servir HTML"""
    try:
         return render_template('index.html')
    except FileNotFoundError:
        return jsonify({
            'message': 'Email Classifier API está rodando',
            'graphql': '/graphql',
            'status': 'ok'
        })

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

if __name__ == '__main__':
    if not db or not classifier:
        print("ERRO: Sistema não foi inicializado corretamente!")
        print("Verifique:")
        print("1. Se o MySQL está rodando")
        print("2. Se as credenciais do banco estão corretas")
        print("3. Se todas as dependências estão instaladas")
        exit(1)
    
    # Executar com gunicorn em produção
    if os.environ.get('PRODUCTION'):
        # Não usar app.run() em produção
        pass
    else:
        app.run(debug=True, host='0.0.0.0', port=5000)