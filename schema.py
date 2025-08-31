# schema_corrigido.py
import graphene
from graphene import ObjectType, String, Int, Float, Boolean, List, Field
import jwt
from datetime import datetime, timedelta
import bcrypt

# Models
class User(ObjectType):
    id = Int()
    username = String()
    email = String()
    is_admin = Boolean()
    created_at = String()

# Payload de Autenticação
class AuthPayload(ObjectType):
    token = String()
    user = Field(User)
    message = String()

# Mutations
class RegisterUser(graphene.Mutation):
    class Arguments:
        username = String(required=True)
        email = String(required=True)
        password = String(required=True)
    
    user = Field(User)
    message = String()
    
    def mutate(self, info, username, email, password):
        db = info.context.db
        
        if not db or not db.connection.is_connected():
            return RegisterUser(message="Erro de conexão com o banco de dados")
            
        cursor = db.connection.cursor()
        
        try:
            # Verificar se usuário já existe
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                return RegisterUser(message="Usuário ou email já existe")
            
            # Hash da senha
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Inserir usuário
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash.decode('utf-8'))
            )
            db.connection.commit()
            
            # Buscar usuário criado
            cursor.execute("SELECT id, username, email, is_admin, created_at FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            
            user = User(
                id=user_data[0],
                username=user_data[1],
                email=user_data[2],
                is_admin=user_data[3],
                created_at=str(user_data[4])
            )
            
            return RegisterUser(user=user, message="Usuário criado com sucesso")
            
        except Exception as e:
            print(f"Erro no registro: {e}")
            db.connection.rollback()
            return RegisterUser(message="Erro ao criar usuário")

class LoginUser(graphene.Mutation):
    class Arguments:
        username = String(required=True)
        password = String(required=True)
    
    auth_payload = Field(AuthPayload)
    
    def mutate(self, info, username, password):
        db = info.context.db
        
        if not db or not db.connection.is_connected():
            return LoginUser(auth_payload=AuthPayload(message="Erro de conexão com o banco de dados"))
            
        cursor = db.connection.cursor()
        
        try:
            # Buscar usuário
            cursor.execute("SELECT id, username, email, password_hash, is_admin FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            
            if not user_data:
                return LoginUser(auth_payload=AuthPayload(message="Credenciais inválidas"))
            
            # Verificar senha
            if not bcrypt.checkpw(password.encode('utf-8'), user_data[3].encode('utf-8')):
                return LoginUser(auth_payload=AuthPayload(message="Credenciais inválidas"))
            
            # Gerar token JWT
            payload = {
                'user_id': user_data[0],
                'exp': datetime.utcnow() + timedelta(days=1)
            }
            token = jwt.encode(payload, 'your_secret_key', algorithm='HS256')
            
            user = User(
                id=user_data[0],
                username=user_data[1],
                email=user_data[2],
                is_admin=user_data[4]
            )
            
            return LoginUser(auth_payload=AuthPayload(token=token, user=user, message="Login realizado com sucesso"))
            
        except Exception as e:
            print(f"Erro no login: {e}")
            return LoginUser(auth_payload=AuthPayload(message="Erro interno"))
# Queries
class Query(ObjectType):
    users = List(User)
  
    
    def resolve_users(self, info):
        db = info.context.db
        user_id = info.context.user_id
        is_admin = info.context.is_admin
        
        if not user_id or not is_admin or not db:
            return []
        
        try:
            cursor = db.connection.cursor()
            cursor.execute("SELECT id, username, email, is_admin, created_at FROM users")
            users_data = cursor.fetchall()
            
            return [User(
                id=user[0],
                username=user[1],
                email=user[2],
                is_admin=user[3],
                created_at=str(user[4])
            ) for user in users_data]
        except Exception as e:
            print(f"Erro ao buscar usuários: {e}")
            return []
    
  
        db = info.context.db
        user_id = info.context.user_id
        is_admin = info.context.is_admin
        
        if not user_id or not db:
            return None
        
        try:
            cursor = db.connection.cursor()
            
            if is_admin:
                query = """
                    SELECT e.id, e.sender, e.subject, e.body, e.category_id, c.name,
                           e.confidence_score, e.suggested_response, e.user_id, 
                           e.is_processed, e.created_at
                    FROM emails e
                    LEFT JOIN categories c ON e.category_id = c.id
                    WHERE e.id = %s
                """
                cursor.execute(query, (id,))
            else:
                query = """
                    SELECT e.id, e.sender, e.subject, e.body, e.category_id, c.name,
                           e.confidence_score, e.suggested_response, e.user_id, 
                           e.is_processed, e.created_at
                    FROM emails e
                    LEFT JOIN categories c ON e.category_id = c.id
                    WHERE e.id = %s AND e.user_id = %s
                """
                cursor.execute(query, (id, user_id))
            
            email_data = cursor.fetchone()
            
            if email_data:
                return Email(
                    id=email_data[0],
                    sender=email_data[1],
                    subject=email_data[2],
                    body=email_data[3],
                    category_id=email_data[4],
                    category_name=email_data[5] or "Desconhecida",
                    confidence_score=email_data[6] or 0.0,
                    suggested_response=email_data[7],
                    user_id=email_data[8],
                    is_processed=email_data[9],
                    created_at=str(email_data[10])
                )
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar email: {e}")
            return None
        
class Mutation(ObjectType):
    register_user = RegisterUser.Field()
    login_user = LoginUser.Field()
   

schema = graphene.Schema(query=Query, mutation=Mutation)