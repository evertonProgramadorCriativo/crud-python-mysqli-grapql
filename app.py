 #Importa a classe Flask para criar a aplicação web
from flask import Flask, request, jsonify , render_template
 

#  Cria uma instância da aplicação Flask
# __name__ é uma variável especial que representa o nome do módulo atual
app = Flask(__name__)

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