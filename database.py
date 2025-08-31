# database_corrigido.py
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
                host='localhost',
                database='email_classifier_teste',
                user='dudu-e',  # SEU USUARIO MYSQL
                password='dudu',  # SUA SENHA MYSQL
                  
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
        

        
        try:
            cursor.execute(create_users_table)
           
            self.connection.commit()
            
        
            
            # Criar usuário admin padrão
            self.create_default_admin()
            
            print("Tabelas criadas/verificadas com sucesso")
            
        except Error as e:
            print(f"Erro ao criar tabelas: {e}")
    
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


    def create_default_users(self):
        
        
        # Criar usuário comum padrão
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = 'usuario'")
        if not cursor.fetchone():
            password = "user123"
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)",
                ("usuario", "usuario@example.com", password_hash.decode('utf-8'), False)
            )
            self.connection.commit()
            print("Usuário comum criado (usuario/user123)")


    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexão MySQL fechada")