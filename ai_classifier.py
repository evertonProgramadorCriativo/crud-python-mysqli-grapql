
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import re
import pickle
import os



class EmailClassifier:
    def __init__(self):
        self.model = None
        self.categories = {
            1: 'Suporte Técnico',
            2: 'Vendas', 
            3: 'Marketing',
            4: 'RH',
            5: 'Financeiro',
            6: 'Geral'
        }
        self.model_path = 'email_classifier_model.pkl'
        self.vectorizer_path = 'email_vectorizer.pkl'
        
        # Carregar ou treinar modelo
        if os.path.exists(self.model_path):
            self.load_model()
        else:
            self.train_initial_model()
    
    def preprocess_text(self, text):
        """Preprocessa o texto para classificação (versão sem NLTK)"""
        if not text:
            return ""
        
        # Converter para minúsculas
        text = text.lower()
        
        # Remover caracteres especiais mas manter acentos
        text = re.sub(r'[^a-záàãâéêíóôõúç\s]', ' ', text)
        
        # Tokenização simples (sem NLTK) - dividir por espaços
        tokens = text.split()
        
        # Remover stopwords manualmente (lista básica em português)
        stop_words = {
            'de', 'da', 'do', 'das', 'dos', 'a', 'o', 'as', 'os', 'um', 'uma', 
            'uns', 'umas', 'em', 'por', 'para', 'com', 'sem', 'sob', 'sobre',
            'entre', 'ante', 'após', 'até', 'com', 'contra', 'desde', 'em',
            'entre', 'para', 'perante', 'por', 'sem', 'sob', 'sobre', 'trás',
            'e', 'mas', 'ou', 'pois', 'que', 'se', 'porque', 'como', 'quando',
            'onde', 'qual', 'quem', 'cujo', 'cuja', 'cujos', 'cujas', 'este',
            'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas', 'aquele',
            'aquela', 'aqueles', 'aquelas', 'isto', 'isso', 'aquilo', 'ao', 'aos',
            'na', 'no', 'nas', 'nos', 'pela', 'pelo', 'pelas', 'pelos', 'meu',
            'minha', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'seu', 'sua',
            'seus', 'suas', 'nosso', 'nossa', 'nossos', 'nossas', 'deles', 'delas',
            'algum', 'alguma', 'alguns', 'algumas', 'todo', 'toda', 'todos', 'todas',
            'outro', 'outra', 'outros', 'outras', 'certo', 'certa', 'certos', 'certas',
            'vário', 'vária', 'vários', 'várias', 'qualquer', 'quaisquer', 'tal',
            'tais', 'cada', 'ambos', 'ambas', 'muito', 'muita', 'muitos', 'muitas',
            'pouco', 'pouca', 'poucos', 'poucas', 'alguns', 'algumas', 'tanto',
            'tanta', 'tantos', 'tantas', 'quanto', 'quanta', 'quantos', 'quantas',
            'outrem', 'ninguém', 'nada', 'nenhum', 'nenhuma', 'nenhuns',
            'nenhumas', 'algo', 'alguém', 'ser', 'estar', 'ter', 'haver', 'ir',
            'vir', 'fazer', 'dizer', 'dar', 'ver', 'saber', 'poder', 'querer'
        }
        
        # Filtrar stopwords e palavras muito curtas
        tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def train_initial_model(self):
        """Treina o modelo inicial com dados sintéticos EXPANDIDOS"""
        print("Treinando modelo inicial...")
        
        # Dados de exemplo MUITO MAIS ABUNDANTES para treinamento inicial
        training_data = [
            # SUPORTE TÉCNICO (categoria 1) - 25 exemplos
            ("erro sistema não funciona problema técnico bug falha", 1),
            ("sistema fora do ar não consegue acessar indisponível", 1),
            ("senha não funciona reset login acesso bloqueado", 1),
            ("aplicativo travando erro fatal crash fechando", 1),
            ("banco dados corrompido backup restaurar", 1),
            ("conexão perdida timeout não conecta rede", 1),
            ("página erro 500 server internal error", 1),
            ("lentidão sistema demorado performance ruim", 1),
            ("vírus malware infectado computador limpar", 1),
            ("atualização falhou upgrade problema instalação", 1),
            ("tela branca não carrega loading infinito", 1),
            ("arquivo corrompido não abre danificado", 1),
            ("impressora não funciona driver problema", 1),
            ("email não envia problema servidor smtp", 1),
            ("backup falhou erro cópia segurança", 1),
            ("certificado expirado ssl https problema", 1),
            ("dns não resolve domínio inacessível", 1),
            ("firewall bloqueando acesso porta fechada", 1),
            ("disco cheio espaço insuficiente storage", 1),
            ("memória insuficiente ram processamento lento", 1),
            ("browser não funciona navegador problema", 1),
            ("plugin erro extensão não carrega", 1),
            ("formulário não envia dados perdidos", 1),
            ("login automatico deslogando sessão expira", 1),
            ("api não responde integração falha timeout", 1),
            
            # VENDAS (categoria 2) - 25 exemplos  
            ("interessado produto preço orçamento comprar", 2),
            ("proposta comercial desconto negociação valor", 2),
            ("valor investimento compra venda cotação", 2),
            ("cliente potencial lead oportunidade negócio", 2),
            ("contrato assinatura fechamento acordo", 2),
            ("demonstração produto apresentação comercial", 2),
            ("reunião vendas proposta cliente", 2),
            ("prazo entrega produto disponibilidade", 2),
            ("condições pagamento parcelamento financiamento", 2),
            ("catálogo produtos lista preços tabela", 2),
            ("representante comercial vendedor consultor", 2),
            ("meta vendas comissão target objetivo", 2),
            ("pipeline vendas funil conversão", 2),
            ("follow up acompanhamento cliente prospect", 2),
            ("upsell cross sell venda adicional", 2),
            ("renovação contrato upgrade serviço", 2),
            ("trial gratuito teste experiência", 2),
            ("referência indicação cliente satisfeito", 2),
            ("concorrente comparação diferencial", 2),
            ("personalização customização produto específico", 2),
            ("volume desconto quantidade atacado", 2),
            ("exclusividade distribuição parceria", 2),
            ("garantia produto suporte pós venda", 2),
            ("implementação projeto cronograma entrega", 2),
            ("roi retorno investimento benefício", 2),
            
            # MARKETING (categoria 3) - 25 exemplos
            ("campanha promoção divulgação marketing publicidade", 3),
            ("newsletter email marketing propaganda anúncio", 3),
            ("evento lançamento produto novidade", 3),
            ("desconto promoção oferta especial liquidação", 3),
            ("redes sociais mídia digital facebook instagram", 3),
            ("branding marca identidade visual logo", 3),
            ("seo otimização busca google ranking", 3),
            ("conteúdo blog artigo material educativo", 3),
            ("webinar palestra apresentação online", 3),
            ("influencer parceria colaboração digital", 3),
            ("pixel tracking conversão análise", 3),
            ("landing page conversão formulário", 3),
            ("email automation sequência nutrição", 3),
            ("segmentação público alvo persona", 3),
            ("funil marketing awareness consideração", 3),
            ("creative banner arte gráfica design", 3),
            ("budget verba investimento marketing", 3),
            ("kpi métrica performance resultado", 3),
            ("a/b test otimização conversão", 3),
            ("remarketing retargeting audiência", 3),
            ("affiliate programa parceiros comissão", 3),
            ("pr assessoria imprensa release", 3),
            ("feira exposição evento networking", 3),
            ("pesquisa mercado tendência comportamento", 3),
            ("copywriting texto persuasivo vendas", 3),
            
            # RH (categoria 4) - 25 exemplos
            ("vaga emprego curriculo recursos humanos", 4),
            ("entrevista seleção candidato processo seletivo", 4),
            ("benefícios salário folha pagamento", 4),
            ("treinamento capacitação desenvolvimento", 4),
            ("demissão rescisão contrato trabalho", 4),
            ("férias licença atestado médico", 4),
            ("avaliação performance desempenho funcionário", 4),
            ("recrutamento headhunter busca talento", 4),
            ("onboarding integração novo colaborador", 4),
            ("política empresa código conduta", 4),
            ("clima organizacional pesquisa satisfação", 4),
            ("plano carreira promoção crescimento", 4),
            ("feedback colaborador desenvolvimento pessoal", 4),
            ("vale refeição transporte benefício", 4),
            ("home office trabalho remoto híbrido", 4),
            ("carga horária expediente ponto eletrônico", 4),
            ("banco horas compensação overtime", 4),
            ("programa trainee jovem aprendiz", 4),
            ("diversidade inclusão igualdade oportunidade", 4),
            ("saúde segurança trabalho epi", 4),
            ("sindicato convenção coletiva acordo", 4),
            ("turnover retenção rotatividade", 4),
            ("cultura organizacional valores missão", 4),
            ("mentoria coaching desenvolvimento liderança", 4),
            ("sucessão planejamento carreira talento", 4),
            
            # FINANCEIRO (categoria 5) - 25 exemplos
            ("fatura cobrança pagamento financeiro", 5),
            ("nota fiscal boleto vencimento quitação", 5),
            ("contabilidade impostos tributos declaração", 5),
            ("fluxo caixa receita despesa movimentação", 5),
            ("relatório financeiro balanço demonstrativo", 5),
            ("orçamento budget planejamento financeiro", 5),
            ("investimento aplicação rentabilidade juros", 5),
            ("empréstimo financiamento capital giro", 5),
            ("auditoria compliance fiscal conformidade", 5),
            ("custo centro resultado margem lucro", 5),
            ("inadimplência atraso cobrança recuperação", 5),
            ("conciliação bancária extrato movimentação", 5),
            ("provisão reserva contingência risco", 5),
            ("depreciação amortização ativo imobilizado", 5),
            ("dre resultado exercício lucro prejuízo", 5),
            ("cash flow projeção entrada saída", 5),
            ("renegociação parcelamento acordo dívida", 5),
            ("capital trabalho liquidez solvência", 5),
            ("análise crédito score rating risco", 5),
            ("controladoria gestão financeira planejamento", 5),
            ("treasury tesouraria aplicação recursos", 5),
            ("budget revisão meta financeira", 5),
            ("closing fechamento contábil mensal", 5),
            ("ifrs normas contábeis padrão", 5),
            ("hedge proteção câmbio moeda risco", 5),
            
            # GERAL (categoria 6) - 25 exemplos
            ("informação geral dúvida consulta esclarecimento", 6),
            ("reunião agenda compromisso encontro", 6),
            ("documentos arquivo anexo arquivo", 6),
            ("contato telefone endereço localização", 6),
            ("outros assuntos diversos variados", 6),
            ("cadastro registro informação dados", 6),
            ("certificado diploma documento oficial", 6),
            ("protocolo número processo acompanhamento", 6),
            ("horário funcionamento atendimento", 6),
            ("localização endereço como chegar", 6),
            ("política privacidade termos uso", 6),
            ("cancelamento interrupção serviço", 6),
            ("alteração mudança modificação dados", 6),
            ("confirmação agendamento marcação", 6),
            ("sugestão melhoria feedback opinião", 6),
            ("reclamação insatisfação problema geral", 6),
            ("elogio parabéns reconhecimento", 6),
            ("parceria colaboração cooperação", 6),
            ("voluntariado ação social comunidade", 6),
            ("sustentabilidade meio ambiente eco", 6),
            ("inovação tecnologia futuro tendência", 6),
            ("pesquisa acadêmica estudo científico", 6),
            ("imprensa jornalista mídia comunicação", 6),
            ("juridico legal advogado assessoria", 6),
            ("outros diversos variado geral comum", 6)
        ]
        
        # Processar textos
        texts = [self.preprocess_text(text) for text, _ in training_data]
        labels = [label for _, label in training_data]
        
        print(f"Treinando com {len(texts)} exemplos:")
        for cat_id, cat_name in self.categories.items():
            count = labels.count(cat_id)
            print(f"  {cat_name}: {count} exemplos")
        
        # Criar pipeline com parâmetros otimizados
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=2000,  # Aumentei o número de features
                ngram_range=(1, 3),  # Inclui trigramas para melhor contexto
                min_df=1,  # Frequência mínima do documento
                max_df=0.95,  # Frequência máxima do documento
                sublinear_tf=True,  # Escala sublinear para TF
                use_idf=True,
                smooth_idf=True
            )),
            ('classifier', MultinomialNB(
                alpha=0.01,  # Suavização menor para dados maiores
                fit_prior=True  # Usar priors baseados na frequência das classes
            ))
        ])
        
        # Treinar modelo
        self.model.fit(texts, labels)
        
        # Avaliar modelo nos dados de treino
        predictions = self.model.predict(texts)
        accuracy = accuracy_score(labels, predictions)
        print(f"Acurácia no treinamento: {accuracy:.3f}")
        
        # Salvar modelo
        self.save_model()
        
        print("Modelo inicial treinado com sucesso!")
    
    def classify_email(self, subject, body):
        """Classifica um email com melhor lógica de decisão"""
        if not self.model:
            print("Modelo não carregado, retornando categoria padrão")
            return 6, 0.5  # Categoria geral com baixa confiança
        
        # Combinar assunto e corpo (assunto tem peso maior)
        full_text = f"{subject} {subject} {body}"  # Duplicar assunto para dar mais peso
        processed_text = self.preprocess_text(full_text)
        
        if not processed_text or len(processed_text.strip()) < 3:
            print("Texto muito curto após processamento")
            return 6, 0.3
        
        try:
            # Fazer predição
            prediction = self.model.predict([processed_text])[0]
            probabilities = self.model.predict_proba([processed_text])[0]
            confidence = max(probabilities)
            
            # Log para debug
            print(f"Texto processado: {processed_text[:100]}...")
            print(f"Predição: {prediction} ({self.categories[prediction]})")
            print(f"Confiança: {confidence:.3f}")
            print(f"Probabilidades por categoria:")
            for i, prob in enumerate(probabilities):
                cat_id = self.model.classes_[i]
                print(f"  {self.categories[cat_id]}: {prob:.3f}")
            
            # Se confiança muito baixa, classificar como geral
            if confidence < 0.4:
                print("Confiança muito baixa, classificando como Geral")
                return 6, confidence
            
            return int(prediction), float(confidence)
            
        except Exception as e:
            print(f"Erro na classificação: {e}")
            return 6, 0.3
    
    def generate_response(self, category_id, subject, body):
        """Gera resposta automática baseada na categoria"""
        responses = {
            1: f"Obrigado por entrar em contato sobre '{subject}'. Nossa equipe de suporte técnico analisará sua solicitação e retornará em até 24 horas com uma solução.",
            2: f"Agradecemos seu interesse em nossos produtos/serviços. Um consultor comercial entrará em contato em breve para apresentar uma proposta personalizada sobre '{subject}'.",
            3: f"Obrigado pelo seu interesse em nossa campanha. Acompanhe nossas redes sociais e newsletter para mais novidades sobre '{subject}'.",
            4: f"Recebemos sua mensagem sobre '{subject}'. O setor de RH analisará sua solicitação e retornará o contato conforme necessário.",
            5: f"Sua solicitação financeira sobre '{subject}' foi recebida. O departamento financeiro processará a informação e retornará em até 2 dias úteis.",
            6: f"Obrigado por entrar em contato sobre '{subject}'. Analisaremos sua mensagem e retornaremos o contato conforme apropriado."
        }
        
        return responses.get(category_id, responses[6])
    
    def retrain_with_feedback(self, feedback_data):
        """Retreina o modelo com dados de feedback"""
        if not feedback_data:
            print("Nenhum dado de feedback fornecido")
            return
        
        try:
            # Preparar dados de feedback
            texts = []
            labels = []
            
            for feedback in feedback_data:
                subject = feedback.get('subject', '')
                body = feedback.get('body', '')
                correct_category = feedback.get('correct_category_id')
                
                if correct_category and correct_category in self.categories:
                    full_text = f"{subject} {subject} {body}"  # Duplicar assunto
                    processed_text = self.preprocess_text(full_text)
                    
                    if processed_text:
                        texts.append(processed_text)
                        labels.append(correct_category)
            
            if texts and labels:
                print(f"Retreinando com {len(texts)} exemplos de feedback")
                
                # Combinar com dados originais se necessário
                if len(texts) < 20:  # Se tiver poucos feedbacks, manter dados originais
                    print("Poucos feedbacks, mantendo treinamento incremental...")
                    # Fazer treinamento incremental (apenas com novos dados)
                    self.model.fit(texts, labels)
                else:
                    # Com muitos feedbacks, retreinar completamente
                    print("Retreinamento completo com feedbacks...")
                    self.model.fit(texts, labels)
                
                self.save_model()
                print(f"Modelo retreinado com sucesso!")
            else:
                print("Nenhum dado válido para retreinamento")
        
        except Exception as e:
            print(f"Erro no retreinamento: {e}")
    
    def save_model(self):
        """Salva o modelo treinado"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            print("Modelo salvo com sucesso")
        except Exception as e:
            print(f"Erro ao salvar modelo: {e}")
    
    def load_model(self):
        """Carrega o modelo salvo"""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            print("Modelo carregado com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}")
            print("Treinando novo modelo...")
            self.train_initial_model()

    def test_categories(self):
        """Método para testar as categorias com exemplos"""
        test_cases = [
            ("Sistema com erro", "O sistema está apresentando erro 500 e não consigo acessar"),
            ("Orçamento produto", "Gostaria de um orçamento para o produto X, qual o preço?"),
            ("Newsletter", "Gostaria de receber informações sobre promoções e novidades"),
            ("Vaga desenvolvedor", "Tenho interesse na vaga de desenvolvedor publicada"),
            ("Boleto vencido", "Meu boleto venceu, como posso quitar?"),
            ("Informações gerais", "Qual o horário de funcionamento da empresa?")
        ]
        
        print("\n=== TESTE DE CATEGORIAS ===")
        for subject, body in test_cases:
            category_id, confidence = self.classify_email(subject, body)
            category_name = self.categories.get(category_id, "Desconhecida")
            print(f"\nTeste: {subject}")
            print(f"Resultado: {category_name} (confiança: {confidence:.3f})")
            print("-" * 50)