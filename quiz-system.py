# Projeto 3: Sistema de Quiz 
import random
import time
from datetime import datetime

class Pergunta:
    def __init__(self, texto, alternativas, resposta_correta, categoria, nivel_dificuldade, explicacao):
        self.texto = texto
        self.alternativas = alternativas
        self.resposta_correta = resposta_correta
        self.categoria = categoria
        self.nivel_dificuldade = nivel_dificuldade
        self.explicacao = explicacao
    
    def verificar_resposta(self, resposta_usuario):
        return resposta_usuario == self.resposta_correta


class Categoria:
    def __init__(self, nome, descricao):
        self.nome = nome
        self.descricao = descricao
        self.perguntas = []
    
    def adicionar_pergunta(self, pergunta):
        self.perguntas.append(pergunta)
    
    def obter_perguntas_por_nivel(self, nivel):
        return [p for p in self.perguntas if p.nivel_dificuldade == nivel]


class Jogador:
    def __init__(self, nome, email):
        self.nome = nome
        self.email = email
        self.data_registro = datetime.now()
        self.historico = []  # Lista de sessões de quiz realizadas
        self.pontuacao_total = 0
        self.estatisticas_por_categoria = {}  # Dicionário {categoria: {acertos, total, percentual}}
    
    def atualizar_estatisticas(self, sessao):
        self.historico.append(sessao)
        self.pontuacao_total += sessao.pontuacao
        
        # Atualiza estatísticas por categoria
        for categoria, resultados in sessao.estatisticas_por_categoria.items():
            if categoria not in self.estatisticas_por_categoria:
                self.estatisticas_por_categoria[categoria] = {"acertos": 0, "total": 0, "percentual": 0}
            
            self.estatisticas_por_categoria[categoria]["acertos"] += resultados["acertos"]
            self.estatisticas_por_categoria[categoria]["total"] += resultados["total"]
            
            # Recalcula percentual
            total = self.estatisticas_por_categoria[categoria]["total"]
            acertos = self.estatisticas_por_categoria[categoria]["acertos"]
            self.estatisticas_por_categoria[categoria]["percentual"] = (acertos / total) * 100 if total > 0 else 0
    
    def obter_areas_para_melhorar(self):
        areas_para_melhorar = []
        for categoria, stats in self.estatisticas_por_categoria.items():
            if stats["percentual"] < 70 and stats["total"] >= 5:
                areas_para_melhorar.append((categoria, stats["percentual"]))
        
        return sorted(areas_para_melhorar, key=lambda x: x[1])


class SessaoQuiz:
    def __init__(self, jogador, modo, categorias=None, nivel_dificuldade=None, limite_perguntas=10):
        self.jogador = jogador
        self.modo = modo  # "treino", "contra-relogio", "eliminatorias"
        self.categorias = categorias  # Lista de categorias selecionadas
        self.nivel_dificuldade = nivel_dificuldade
        self.limite_perguntas = limite_perguntas
        self.perguntas = []
        self.respostas_usuario = []
        self.tempos_resposta = []
        self.pontuacao = 0
        self.data_inicio = datetime.now()
        self.data_fim = None
        self.estatisticas_por_categoria = {}
    
    def selecionar_perguntas(self, banco_de_perguntas):
        perguntas_disponiveis = []
        
        # Filtra perguntas por categoria e nível, se especificados
        for categoria in banco_de_perguntas:
            if self.categorias is None or categoria.nome in self.categorias:
                if self.nivel_dificuldade:
                    perguntas_disponiveis.extend(categoria.obter_perguntas_por_nivel(self.nivel_dificuldade))
                else:
                    perguntas_disponiveis.extend(categoria.perguntas)
        
        # Seleciona aleatoriamente o número de perguntas definido pelo limite
        if len(perguntas_disponiveis) <= self.limite_perguntas:
            self.perguntas = perguntas_disponiveis
        else:
            self.perguntas = random.sample(perguntas_disponiveis, self.limite_perguntas)
    
    def iniciar_quiz(self, banco_de_perguntas):
        self.selecionar_perguntas(banco_de_perguntas)
        
        # Inicializa estatísticas por categoria
        categorias_presentes = {p.categoria for p in self.perguntas}
        for categoria in categorias_presentes:
            self.estatisticas_por_categoria[categoria] = {"acertos": 0, "total": 0, "percentual": 0}
        
        # Loop principal do quiz
        for i, pergunta in enumerate(self.perguntas):
            print(f"\nPergunta {i+1}/{len(self.perguntas)}:")
            print(f"Categoria: {pergunta.categoria} - Nível: {pergunta.nivel_dificuldade}")
            print(f"\n{pergunta.texto}")
            
            # Mostra alternativas
            for j, alternativa in enumerate(pergunta.alternativas):
                print(f"{chr(65+j)}) {alternativa}")
            
            # Tempo inicial
            tempo_inicio = time.time()
            
            # Recebe resposta do usuário
            resposta_usuario = input("\nSua resposta (A, B, C, D): ").upper()
            
            # Tempo final
            tempo_resposta = time.time() - tempo_inicio
            self.tempos_resposta.append(tempo_resposta)
            
            # Converte letra (A, B, C, D) para índice (0, 1, 2, 3)
            indice_resposta = ord(resposta_usuario) - 65 if resposta_usuario in "ABCD" else -1
            
            # Verifica se a resposta está correta
            if 0 <= indice_resposta < len(pergunta.alternativas):
                esta_correta = pergunta.verificar_resposta(indice_resposta)
                self.respostas_usuario.append(indice_resposta)
                
                # Atualiza estatísticas
                categoria = pergunta.categoria
                self.estatisticas_por_categoria[categoria]["total"] += 1
                
                if esta_correta:
                    print("\n✓ Correto!")
                    self.estatisticas_por_categoria[categoria]["acertos"] += 1
                    
                    # Cálculo de pontuação com base no nível e tempo de resposta
                    pontos_nivel = pergunta.nivel_dificuldade * 10
                    pontos_tempo = max(0, 30 - int(tempo_resposta)) if self.modo == "contra-relogio" else 0
                    pontos_total = pontos_nivel + pontos_tempo
                    self.pontuacao += pontos_total
                    
                    print(f"Você ganhou {pontos_total} pontos!")
                else:
                    print("\n✗ Incorreto!")
                    print(f"A resposta correta era: {chr(65 + pergunta.resposta_correta)}) {pergunta.alternativas[pergunta.resposta_correta]}")
                    print(f"Explicação: {pergunta.explicacao}")
                    
                    # No modo eliminatórias, encerra o quiz se errar
                    if self.modo == "eliminatorias":
                        print("\nModo Eliminatórias: Quiz encerrado após resposta incorreta!")
                        break
            else:
                print("\nResposta inválida! Considere como erro.")
                self.respostas_usuario.append(-1)
                self.estatisticas_por_categoria[pergunta.categoria]["total"] += 1
            
            # Modo contra-relógio: verifica se o tempo excedeu o limite (por exemplo, 5 segundos por pergunta)
            if self.modo == "contra-relogio" and tempo_resposta > 30:
                print("\nTempo excedido para esta pergunta!")
        
        # Finaliza a sessão
        self.data_fim = datetime.now()
        
        # Calcula percentuais para cada categoria
        for categoria, stats in self.estatisticas_por_categoria.items():
            stats["percentual"] = (stats["acertos"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        
        # Exibe resultados
        self.exibir_resultados()
        
        # Atualiza estatísticas do jogador
        self.jogador.atualizar_estatisticas(self)
    
    def exibir_resultados(self):
        perguntas_respondidas = len(self.respostas_usuario)
        acertos = sum(1 for i, resp in enumerate(self.respostas_usuario) if i < len(self.perguntas) and resp == self.perguntas[i].resposta_correta)
        
        print("\n" + "="*50)
        print(f"RESULTADOS DO QUIZ - {self.modo.upper()}")
        print("="*50)
        print(f"Jogador: {self.jogador.nome}")
        print(f"Data: {self.data_inicio.strftime('%d/%m/%Y %H:%M')} a {self.data_fim.strftime('%H:%M')}")
        print(f"Perguntas: {perguntas_respondidas}/{len(self.perguntas)}")
        print(f"Acertos: {acertos} ({acertos/perguntas_respondidas*100:.1f}%)")
        print(f"Pontuação: {self.pontuacao}")
        
        if self.tempos_resposta:
            tempo_medio = sum(self.tempos_resposta) / len(self.tempos_resposta)
            print(f"Tempo médio por pergunta: {tempo_medio:.1f} segundos")
        
        print("\nDesempenho por categoria:")
        for categoria, stats in self.estatisticas_por_categoria.items():
            print(f"- {categoria}: {stats['acertos']}/{stats['total']} ({stats['percentual']:.1f}%)")
        
        areas_melhorar = self.jogador.obter_areas_para_melhorar()
        if areas_melhorar:
            print("\nÁreas para melhorar:")
            for area, percentual in areas_melhorar[:3]:  # Top 3 áreas para melhorar
                print(f"- {area}: {percentual:.1f}%")
        
        print("="*50)


class SistemaQuiz:
    def __init__(self):
        self.categorias = []
        self.jogadores = []
    
    def registrar_jogador(self, nome, email):
        jogador = Jogador(nome, email)
        self.jogadores.append(jogador)
        return jogador
    
    def adicionar_categoria(self, nome, descricao):
        categoria = Categoria(nome, descricao)
        self.categorias.append(categoria)
        return categoria
    
    def iniciar_sessao(self, jogador, modo, categorias=None, nivel_dificuldade=None, limite_perguntas=10):
        sessao = SessaoQuiz(jogador, modo, categorias, nivel_dificuldade, limite_perguntas)
        sessao.iniciar_quiz(self.categorias)
        return sessao
    
    def carregar_banco_de_perguntas_padrao(self):
        # Cria categorias básicas
        categoria_matematica = self.adicionar_categoria("Matemática", "Perguntas sobre aritmética, geometria, álgebra e outros tópicos matemáticos")
        categoria_historia = self.adicionar_categoria("História", "Perguntas sobre eventos históricos, personalidades e civilizações")
        categoria_ciencias = self.adicionar_categoria("Ciências", "Perguntas sobre física, química, biologia e outras ciências naturais")
        
        # Matemática - Nível 1
        p1 = Pergunta(
            "Quanto é 8 × 7?",
            ["42", "54", "56", "64"],
            2,  # Índice da resposta correta (56)
            "Matemática",
            1,  # Nível de dificuldade
            "8 × 7 = 56. Esta é uma operação básica de multiplicação."
        )
        categoria_matematica.adicionar_pergunta(p1)
        
        p2 = Pergunta(
            "Qual é a área de um quadrado com lado de 5 metros?",
            ["10 m²", "20 m²", "25 m²", "30 m²"],
            2,  # Índice da resposta correta (25 m²)
            "Matemática",
            1,
            "A área de um quadrado é calculada como lado × lado. Portanto, 5 × 5 = 25 m²."
        )
        categoria_matematica.adicionar_pergunta(p2)
        
        # Matemática - Nível 2
        p3 = Pergunta(
            "Se um ângulo mede 45 graus, quanto mede o seu ângulo complementar?",
            ["30 graus", "45 graus", "60 graus", "135 graus"],
            1,  # Índice da resposta correta (45 graus)
            "Matemática",
            2,
            "Ângulos complementares somam 90 graus. Portanto, 90 - 45 = 45 graus."
        )
        categoria_matematica.adicionar_pergunta(p3)
        
        # História - Nível 1
        p4 = Pergunta(
            "Quem foi o primeiro presidente do Brasil?",
            ["Dom Pedro I", "Getúlio Vargas", "Marechal Deodoro da Fonseca", "Juscelino Kubitschek"],
            2,  # Índice da resposta correta (Marechal Deodoro da Fonseca)
            "História",
            1,
            "Marechal Deodoro da Fonseca foi o primeiro presidente do Brasil, após a Proclamação da República em 1889."
        )
        categoria_historia.adicionar_pergunta(p4)
        
        # História - Nível 2
        p5 = Pergunta(
            "Qual foi o período conhecido como 'Era Vargas' no Brasil?",
            ["1922 a 1930", "1930 a 1945", "1945 a 1954", "1930 a 1954"],
            3,  # Índice da resposta correta (1930 a 1954)
            "História",
            2,
            "A Era Vargas compreende os períodos em que Getúlio Vargas governou o Brasil, de 1930 a 1945 e de 1951 a 1954."
        )
        categoria_historia.adicionar_pergunta(p5)
        
        # Ciências - Nível 1
        p6 = Pergunta(
            "Qual é o símbolo químico do Oxigênio?",
            ["O", "OX", "Ox", "Og"],
            0,  # Índice da resposta correta (O)
            "Ciências",
            1,
            "O símbolo químico do Oxigênio é 'O', representando o elemento químico de número atômico 8."
        )
        categoria_ciencias.adicionar_pergunta(p6)
        
        # Ciências - Nível 2
        p7 = Pergunta(
            "Qual das seguintes estruturas celulares é responsável pela produção de energia?",
            ["Núcleo", "Ribossomo", "Mitocôndria", "Membrana plasmática"],
            2,  # Índice da resposta correta (Mitocôndria)
            "Ciências",
            2,
            "As mitocôndrias são as 'usinas de energia' das células, onde ocorre a respiração celular e a produção de ATP."
        )
        categoria_ciencias.adicionar_pergunta(p7)


# Exemplo de uso
if __name__ == "__main__":
    # Inicializa o sistema
    sistema = SistemaQuiz()
    sistema.carregar_banco_de_perguntas_padrao()
    
    print("="*50)
    print("  SISTEMA DE QUIZ EDUCATIVO MULTIDISCIPLINAR  ")
    print("="*50)
    
    # Registro de jogador
    nome = input("Digite seu nome: ")
    email = input("Digite seu email: ")
    jogador = sistema.registrar_jogador(nome, email)
    
    while True:
        print("\nMENÚ PRINCIPAL")
        print("1. Iniciar Quiz - Modo Treino")
        print("2. Iniciar Quiz - Modo Contra-Relógio")
        print("3. Iniciar Quiz - Modo Eliminatórias")
        print("4. Ver Estatísticas")
        print("5. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            # Quiz Modo Treino
            sistema.iniciar_sessao(jogador, "treino", limite_perguntas=5)
        elif opcao == "2":
            # Quiz Modo Contra-Relógio
            sistema.iniciar_sessao(jogador, "contra-relogio", limite_perguntas=5)
        elif opcao == "3":
            # Quiz Modo Eliminatórias
            sistema.iniciar_sessao(jogador, "eliminatorias", limite_perguntas=10)
        elif opcao == "4":
            # Ver estatísticas
            print("\n" + "="*50)
            print(f"ESTATÍSTICAS DO JOGADOR: {jogador.nome}")
            print("="*50)
            print(f"Total de quizzes realizados: {len(jogador.historico)}")
            print(f"Pontuação total acumulada: {jogador.pontuacao_total}")
            
            if jogador.estatisticas_por_categoria:
                print("\nDesempenho por categoria:")
                for categoria, stats in jogador.estatisticas_por_categoria.items():
                    print(f"- {categoria}: {stats['acertos']}/{stats['total']} ({stats['percentual']:.1f}%)")
            
            areas_melhorar = jogador.obter_areas_para_melhorar()
            if areas_melhorar:
                print("\nÁreas para melhorar:")
                for area, percentual in areas_melhorar:
                    print(f"- {area}: {percentual:.1f}%")
            print("="*50)
        elif opcao == "5":
            print("Obrigado por usar o Sistema de Quiz Educativo!")
            break
        else:
            print("Opção inválida. Tente novamente.")
