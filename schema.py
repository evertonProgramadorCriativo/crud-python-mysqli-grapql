
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

class Category(ObjectType):
    id = Int()
    name = String()
    description = String()
    color = String()
    created_at = String()

class Email(ObjectType):
    id = Int()
    sender = String()
    subject = String()
    body = String()
    category_id = Int()
    category_name = String()
    confidence_score = Float()
    suggested_response = String()
    user_id = Int()
    is_processed = Boolean()
    created_at = String()

class Feedback(ObjectType):
    id = Int()
    email_id = Int()
    user_id = Int()
    original_category_id = Int()
    corrected_category_id = Int()
    feedback_text = String()
    created_at = String()

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

class ClassifyEmail(graphene.Mutation):
    class Arguments:
        sender = String(required=True)
        subject = String(required=True)
        body = String(required=True)
    
    email = Field(Email)
    message = String()
    
    def mutate(self, info, sender, subject, body):
        db = info.context.db
        classifier = info.context.classifier
        user_id = info.context.user_id
        
        if not user_id:
            return ClassifyEmail(message="Usuário não autenticado")
        
        if not db or not classifier:
            return ClassifyEmail(message="Sistema não inicializado")
        
        try:
            # Classificar email
            category_id, confidence = classifier.classify_email(subject, body)
            
            # Gerar resposta sugerida
            suggested_response = classifier.generate_response(category_id, subject, body)
            
            # Salvar no banco
            cursor = db.connection.cursor()
            cursor.execute("""
                INSERT INTO emails (sender, subject, body, category_id, confidence_score, 
                                  suggested_response, user_id, is_processed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (sender, subject, body, category_id, confidence, suggested_response, user_id, True))
            
            email_id = cursor.lastrowid
            db.connection.commit()
            
            # Buscar nome da categoria
            cursor.execute("SELECT name FROM categories WHERE id = %s", (category_id,))
            category_result = cursor.fetchone()
            category_name = category_result[0] if category_result else "Desconhecida"
            
            email = Email(
                id=email_id,
                sender=sender,
                subject=subject,
                body=body,
                category_id=category_id,
                category_name=category_name,
                confidence_score=confidence,
                suggested_response=suggested_response,
                user_id=user_id,
                is_processed=True
            )
            
            return ClassifyEmail(email=email, message="Email classificado com sucesso")
            
        except Exception as e:
            print(f"Erro na classificação: {e}")
            return ClassifyEmail(message="Erro ao classificar email")

class AddFeedback(graphene.Mutation):
    class Arguments:
        email_id = Int(required=True)
        corrected_category_id = Int(required=True)
        feedback_text = String()
    
    feedback = Field(Feedback)
    message = String()
    
    def mutate(self, info, email_id, corrected_category_id, feedback_text=""):
        db = info.context.db
        user_id = info.context.user_id
        
        if not user_id:
            return AddFeedback(message="Usuário não autenticado")
        
        if not db:
            return AddFeedback(message="Sistema não inicializado")
        
        cursor = db.connection.cursor()
        
        try:
            # Buscar email e categoria original
            cursor.execute("SELECT category_id FROM emails WHERE id = %s", (email_id,))
            email_data = cursor.fetchone()
            
            if not email_data:
                return AddFeedback(message="Email não encontrado")
            
            original_category_id = email_data[0]
            
            # Inserir feedback
            cursor.execute("""
                INSERT INTO feedback (email_id, user_id, original_category_id, 
                                    corrected_category_id, feedback_text)
                VALUES (%s, %s, %s, %s, %s)
            """, (email_id, user_id, original_category_id, corrected_category_id, feedback_text))
            
            feedback_id = cursor.lastrowid
            db.connection.commit()
            
            feedback = Feedback(
                id=feedback_id,
                email_id=email_id,
                user_id=user_id,
                original_category_id=original_category_id,
                corrected_category_id=corrected_category_id,
                feedback_text=feedback_text
            )
            
            return AddFeedback(feedback=feedback, message="Feedback adicionado com sucesso")
            
        except Exception as e:
            print(f"Erro ao adicionar feedback: {e}")
            db.connection.rollback()
            return AddFeedback(message="Erro ao adicionar feedback")

# Queries
class Query(ObjectType):
    users = List(User)
    categories = List(Category)
    emails = List(Email)
    email = Field(Email, id=Int(required=True))
    
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
    
    def resolve_categories(self, info):
        db = info.context.db
        
        if not db:
            return []
        
        try:
            cursor = db.connection.cursor()
            cursor.execute("SELECT id, name, description, color, created_at FROM categories")
            categories_data = cursor.fetchall()
            
            return [Category(
                id=cat[0],
                name=cat[1],
                description=cat[2],
                color=cat[3],
                created_at=str(cat[4])
            ) for cat in categories_data]
        except Exception as e:
            print(f"Erro ao buscar categorias: {e}")
            return []
    
    def resolve_emails(self, info):
        db = info.context.db
        user_id = info.context.user_id
        is_admin = info.context.is_admin
        
        if not user_id or not db:
            return []
        
        try:
            cursor = db.connection.cursor()
            
            if is_admin:
                query = """
                    SELECT e.id, e.sender, e.subject, e.body, e.category_id, c.name,
                           e.confidence_score, e.suggested_response, e.user_id, 
                           e.is_processed, e.created_at
                    FROM emails e
                    LEFT JOIN categories c ON e.category_id = c.id
                    ORDER BY e.created_at DESC
                    LIMIT 100
                """
                cursor.execute(query)
            else:
                query = """
                    SELECT e.id, e.sender, e.subject, e.body, e.category_id, c.name,
                           e.confidence_score, e.suggested_response, e.user_id, 
                           e.is_processed, e.created_at
                    FROM emails e
                    LEFT JOIN categories c ON e.category_id = c.id
                    WHERE e.user_id = %s
                    ORDER BY e.created_at DESC
                    LIMIT 100
                """
                cursor.execute(query, (user_id,))
            
            emails_data = cursor.fetchall()
            
            return [Email(
                id=email[0],
                sender=email[1],
                subject=email[2],
                body=email[3],
                category_id=email[4],
                category_name=email[5] or "Desconhecida",
                confidence_score=email[6] or 0.0,
                suggested_response=email[7],
                user_id=email[8],
                is_processed=email[9],
                created_at=str(email[10])
            ) for email in emails_data]
            
        except Exception as e:
            print(f"Erro ao buscar emails: {e}")
            return []
    
    def resolve_email(self, info, id):
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
    classify_email = ClassifyEmail.Field()
    add_feedback = AddFeedback.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)