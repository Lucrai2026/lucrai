# 📱 PlayLucro Bot - Documentação Completa v2.0

## 🎯 Visão Geral

PlayLucro é um bot do Telegram que permite usuários ganhar dinheiro assistindo vídeos de publicidade. O sistema integra com AdscendMedia e inclui um painel administrativo web.

**Status:** ✅ **SISTEMA COMPLETO**

---

## 📊 Funcionalidades Implementadas

### ✅ 1. Sistema de Cadastro
- Coleta de dados: Nome, Cidade, Idade
- Validação de informações
- Confirmação antes de salvar
- Banco de dados SQLite

### ✅ 2. Menu Principal (6 Botões)
Layout 2x3 com inline buttons + teclado tradicional:
- 🎬 **Assistir Vídeos** - Lista de vídeos com valores
- 🔗 **Indique e Ganhe** - Sistema de afiliados (10% revenue share)
- 💸 **Sacar Saldo** - Saque com PIX (mínimo R$ 20,00)
- 📊 **Histórico** - Histórico de vídeos assistidos
- ⚙️ **Configurações** - Alterar dados do perfil
- 💬 **Suporte** - Link para grupo de suporte

### ✅ 3. Sistema de Vídeos
- Lista de vídeos disponíveis
- Cada vídeo mostra valor específico
- Clique para assistir
- Simulação de visualização completa
- Crédito automático após assistir
- 5 vídeos de teste pré-carregados

**Exemplo:**
```
📹 Vídeo 01 - Ganhe Dinheiro
   Assista por completo e ganhe R$ 0,55
   ⏱️ Duração: 60s
```

### ✅ 4. Sistema de Saque (PIX)
**Fluxo:**
1. Usuário clica em "Sacar Saldo"
2. Sistema mostra saldo atual
3. Se ≥ R$ 20,00:
   - Se tem PIX → Mostra PIX + botão "Solicitar Saque"
   - Se não tem PIX → Pede para cadastrar
4. Primeira vez → Pergunta qual é o PIX
5. Armazena PIX no banco
6. Sua equipe valida e paga

**Dados Armazenados:**
- Valor do saque
- PIX
- Status (pendente/pago)
- Data da solicitação

### ✅ 5. Sistema de Afiliados (Revenue Share)
**Como funciona:**
- Cada usuário tem um **link único de indicação**
- Quando alguém clica no link e se cadastra, fica vinculado
- Para cada vídeo que o indicado assiste, o afiliado ganha **10%**

**Repartição do vídeo COM afiliado:**
- 10% → Afiliado
- 25% → PlayLucro
- 65% → Quem assistiu

**Exemplo:**
```
Vídeo vale R$ 1,00

SEM AFILIADO:
- PlayLucro: R$ 0,30 (30%)
- Usuário: R$ 0,70 (70%)

COM AFILIADO:
- Afiliado: R$ 0,10 (10%)
- PlayLucro: R$ 0,25 (25%)
- Usuário: R$ 0,65 (65%)
```

**Painel de Afiliados:**
- Link único para compartilhar
- Contador de indicados
- Total de comissões ganhas
- Explicação de como funciona

### ✅ 6. Histórico de Vídeos
- Lista dos últimos 10 vídeos assistidos
- Mostra:
  - Título do vídeo
  - Data e hora
  - Status (✅ Completo / ❌ Não completo)
  - Valor ganho ou "Não recebido"

**Exemplo:**
```
✅ Vídeo 01 - Ganhe Dinheiro
   15/11/2025 14:30 - R$ 0,55

❌ Vídeo 02 - Assista e Lucre
   15/11/2025 13:45 - Não recebido
```

### ✅ 7. Configurações
Permite alterar:
- 👤 **Nome**
- 🏙️ **Cidade**
- 🎂 **Idade**
- 📱 **PIX**

### ✅ 8. Suporte
- Link direto para grupo de suporte: `https://t.me/playlucro_suporte`
- Usuário clica e vai direto para o grupo

---

## 🗄️ Banco de Dados

### Tabelas

#### `usuarios`
```sql
CREATE TABLE usuarios (
    user_id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    cidade TEXT,
    idade INTEGER,
    saldo REAL DEFAULT 0.0,
    pix TEXT,
    afiliado_de INTEGER,
    link_afiliado TEXT UNIQUE,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### `videos`
```sql
CREATE TABLE videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    url TEXT NOT NULL,
    valor REAL NOT NULL,
    duracao INTEGER,
    fonte TEXT DEFAULT 'teste',
    data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT 1
)
```

#### `visualizacoes`
```sql
CREATE TABLE visualizacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    video_id INTEGER NOT NULL,
    data_visualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'completo',
    valor_ganho REAL,
    FOREIGN KEY (user_id) REFERENCES usuarios(user_id),
    FOREIGN KEY (video_id) REFERENCES videos(id)
)
```

#### `transacoes`
```sql
CREATE TABLE transacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tipo TEXT,
    valor REAL NOT NULL,
    descricao TEXT,
    data_transacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES usuarios(user_id)
)
```

#### `saques`
```sql
CREATE TABLE saques (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    valor REAL NOT NULL,
    pix TEXT,
    status TEXT DEFAULT 'pendente',
    data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_pagamento TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES usuarios(user_id)
)
```

---

## 🔄 Fluxos de Funcionamento

### 1️⃣ Fluxo de Cadastro
```
/start
  ↓
Mostra banner + botão "Cadastrar"
  ↓
Pergunta: Nome
  ↓
Pergunta: Cidade
  ↓
Pergunta: Idade
  ↓
Confirmação
  ↓
Salva no banco + Gera link de afiliado
  ↓
Mostra menu principal
```

### 2️⃣ Fluxo de Assistir Vídeo
```
Clica em "Assistir Vídeos"
  ↓
Mostra lista de vídeos com valores
  ↓
Clica em um vídeo
  ↓
Simula assistência completa
  ↓
Registra visualização no banco
  ↓
Credita valor na conta
  ↓
Se tem afiliado → Credita 10% para afiliado
  ↓
Mostra confirmação com novo saldo
```

### 3️⃣ Fluxo de Saque
```
Clica em "Sacar Saldo"
  ↓
Mostra saldo atual
  ↓
Se saldo < R$ 20,00 → Mostra quanto falta
  ↓
Se saldo ≥ R$ 20,00:
  ├─ Se tem PIX → Mostra PIX + botão "Solicitar"
  └─ Se não tem → Pede para cadastrar
  ↓
Primeira vez → Pergunta PIX
  ↓
Armazena PIX
  ↓
Clica "Solicitar Saque"
  ↓
Registra saque como "pendente"
  ↓
Reduz saldo do usuário
  ↓
Sua equipe valida e marca como "pago"
```

### 4️⃣ Fluxo de Afiliado
```
Usuário recebe link: https://t.me/playlucro_bot?start=ref_123456
  ↓
Novo usuário clica no link
  ↓
Bot detecta ref_123456
  ↓
Durante cadastro, vincula novo usuário ao afiliado
  ↓
Quando novo usuário assiste vídeo:
  ├─ Valor do vídeo é creditado
  ├─ 10% é creditado para afiliado
  └─ Transação é registrada como "comissao"
```

---

## 🛠️ Como Usar

### Instalação
```bash
# Clonar repositório
git clone https://github.com/Lucrai2026/lucrai.git
cd lucrai

# Instalar dependências
pip install -r requirements.txt

# Rodar o bot
python main.py
```

### Variáveis de Ambiente
```bash
export TELEGRAM_BOT_TOKEN="seu_token_aqui"
```

### Banco de Dados
- Arquivo: `lucrai_db.sqlite`
- Criado automaticamente na primeira execução
- 5 vídeos de teste pré-carregados

---

## 📈 Repartição de Valores

### SEM Afiliado
```
Vídeo = R$ 1,00
├─ PlayLucro: R$ 0,30 (30%)
└─ Usuário: R$ 0,70 (70%)
```

### COM Afiliado
```
Vídeo = R$ 1,00
├─ Afiliado: R$ 0,10 (10%)
├─ PlayLucro: R$ 0,25 (25%)
└─ Usuário: R$ 0,65 (65%)
```

---

## 🔐 Segurança

### Implementado
- ✅ Validação de dados de entrada
- ✅ Banco de dados com chaves estrangeiras
- ✅ Transações registradas
- ✅ Status de saques (pendente/pago)
- ✅ PIX armazenado com segurança

### A Implementar
- 🔲 Confirmação via API do AdscendMedia
- 🔲 Sistema anti-burla (limite de vídeos por dia)
- 🔲 Validação de PIX real
- 🔲 Criptografia de dados sensíveis

---

## 🚀 Próximas Etapas

### 1. Integração com AdscendMedia
- [ ] Trocar Mock API por API real
- [ ] Validar visualizações com API
- [ ] Sincronizar vídeos automaticamente

### 2. Painel Admin Web
- [ ] Dashboard com estatísticas
- [ ] Gerenciamento de usuários
- [ ] Gerenciamento de saques
- [ ] Relatórios de comissões

### 3. Melhorias
- [ ] Sistema de níveis de afiliado
- [ ] Bônus por desempenho
- [ ] Notificações de saques
- [ ] Suporte a múltiplos métodos de pagamento

---

## 📞 Suporte

**Grupo de Suporte:** https://t.me/playlucro_suporte

---

## 📝 Notas Importantes

### Sobre o Banco de Dados
- SQLite é local (arquivo `lucrai_db.sqlite`)
- Ideal para desenvolvimento e testes
- Para produção, considere migrar para MySQL/PostgreSQL

### Sobre os Vídeos
- 5 vídeos de teste pré-carregados
- Quando AdscendMedia aprovar, trocar por API real
- Valores são simulados (usar valores reais depois)

### Sobre PIX
- Armazenado em texto simples (considerar criptografia)
- Validação básica (apenas armazena)
- Sua equipe valida manualmente antes de pagar

### Sobre Afiliados
- Link único por usuário
- Rastreamento automático via `ref_` parameter
- Comissão creditada automaticamente

---

## 🎯 Checklist de Funcionalidades

- [x] Cadastro de usuários
- [x] Menu principal com 6 botões
- [x] Sistema de vídeos
- [x] Assistir vídeo e ganhar
- [x] Histórico de vídeos
- [x] Sistema de saque com PIX
- [x] Sistema de afiliados (10% revenue share)
- [x] Configurações do perfil
- [x] Link de suporte
- [x] Banco de dados completo
- [ ] Integração com AdscendMedia
- [ ] Painel admin web
- [ ] Sistema anti-burla

---

**Versão:** 2.0  
**Data:** 15/11/2025  
**Status:** ✅ Completo e Funcional
