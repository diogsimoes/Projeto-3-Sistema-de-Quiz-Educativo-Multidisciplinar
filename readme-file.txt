# Sistema de Quiz Educativo Multidisciplinar

Um sistema de quiz interativo em Python que permite testar conhecimentos em diversas áreas temáticas e acompanhar o progresso de aprendizagem.

## Características

- Banco de perguntas organizadas por categorias e níveis de dificuldade
- Sistema de jogadores com perfis e histórico de desempenho
- Diferentes modos de jogo:
  - Treino: modo regular para praticar
  - Contra-relógio: pontos extras por respostas rápidas
  - Eliminatórias: quiz termina ao errar uma questão
- Feedback imediato com explicações para respostas incorretas
- Sistema de pontuação baseado em dificuldade e tempo de resposta
- Estatísticas de progresso e áreas para melhorar

## Como Usar

1. Clone o repositório
2. Execute o arquivo `quiz_system.py`
3. Siga as instruções no terminal para jogar

```bash
python quiz_system.py
```

## Estrutura do Projeto

O sistema usa programação orientada a objetos com as seguintes classes:

- `Pergunta`: Armazena dados sobre uma questão individual
- `Categoria`: Organiza perguntas em grupos temáticos
- `Jogador`: Mantém perfil e estatísticas do usuário
- `SessaoQuiz`: Gerencia uma instância de jogo
- `SistemaQuiz`: Controla todo o sistema

## Conceitos Utilizados

- Classes e objetos
- Listas e dicionários
- Gestão de tempo
- Estatísticas e cálculos de pontuação
- Interface de texto interativa
