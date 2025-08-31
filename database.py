import mysql.connector
from mysql.connector import Error
import bcrypt
import os

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        
        try:
            # ALTERE AQUI SUAS CREDENCIAIS DO MYSQL
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'email_classifier_teste'),
                user=os.getenv('DB_USER', 'dudu-e'),
                password=os.getenv('DB_PASSWORD', 'dudu'),
                port=os.getenv('DB_PORT', 3306)

                  
            )
            if self.connection.is_connected():
                print("Conectado ao MySQL")
        except Error as e:
            print(f"Erro ao conectar com MySQL: {e}")
            print("Verifique se:")
            print("1. O MySQL está rodando")
            print("2. As credenciais estão corretas")
            print("3. O banco 'email_classifier_teste' existe")
    
    def create_tables(self):
        if not self.connection or not self.connection.is_connected():
            print("Erro: Não há conexão com o banco de dados")
            return
            
        cursor = self.connection.cursor()
        
        # Tabela de usuários
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # Tabela de categorias
        create_categories_table = """
        CREATE TABLE IF NOT EXISTS categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            color VARCHAR(7) DEFAULT '#007bff',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # Tabela de emails
        create_emails_table = """
        CREATE TABLE IF NOT EXISTS emails (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender VARCHAR(255) NOT NULL,
            subject VARCHAR(500) NOT NULL,
            body TEXT NOT NULL,
            category_id INT,
            confidence_score FLOAT DEFAULT 0.0,
            suggested_response TEXT,
            user_id INT NOT NULL,
            is_processed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        
        # Tabela de feedback para treinamento
        create_feedback_table = """
        CREATE TABLE IF NOT EXISTS feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email_id INT NOT NULL,
            user_id INT NOT NULL,
            original_category_id INT,
            corrected_category_id INT,
            feedback_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (original_category_id) REFERENCES categories(id) ON DELETE SET NULL,
            FOREIGN KEY (corrected_category_id) REFERENCES categories(id) ON DELETE SET NULL
        )
        """
        
        try:
            cursor.execute(create_users_table)
            cursor.execute(create_categories_table)
            cursor.execute(create_emails_table)
            cursor.execute(create_feedback_table)
            self.connection.commit()
            
            # Inserir categorias padrão
            self.insert_default_categories()
            
            # Criar usuário admin padrão
            self.create_default_admin()
            
            print("Tabelas criadas/verificadas com sucesso")
            
        except Error as e:
            print(f"Erro ao criar tabelas: {e}")
    
    def insert_default_categories(self):
        cursor = self.connection.cursor()
        
        categories = [
            ('Suporte Técnico', 'Emails relacionados a problemas técnicos', '#dc3545'),
            ('Vendas', 'Emails de consultas e negociações de vendas', '#28a745'),
            ('Marketing', 'Emails promocionais e campanhas', '#ffc107'),
            ('RH', 'Emails de recursos humanos', '#17a2b8'),
            ('Financeiro', 'Emails relacionados a finanças', '#6610f2'),
            ('Geral', 'Emails diversos não categorizados', '#6c757d')
        ]
        
        for name, description, color in categories:
            try:
                cursor.execute(
                    "INSERT IGNORE INTO categories (name, description, color) VALUES (%s, %s, %s)",
                    (name, description, color)
                )
            except Error as e:
                print(f"Erro ao inserir categoria {name}: {e}")
        
        self.connection.commit()
    
    def create_default_admin(self):
        cursor = self.connection.cursor()
        
        # Verificar se admin já existe
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if cursor.fetchone():
            return  # Admin já existe
        
        password = "admin123"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)",
                ("admin", "admin@example.com", password_hash.decode('utf-8'), True)
            )
            self.connection.commit()
            print("Usuário admin criado com sucesso (admin/admin123)")
        except Error as e:
            print(f"Erro ao criar admin: {e}")
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexão MySQL fechada")