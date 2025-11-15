# 🚀 PlayLucro Bot v2.0 - Guia Rápido

## ✅ O QUE FOI IMPLEMENTADO

### 1. 🎬 **Assistir Vídeos**
- ✅ Lista de 5 vídeos de teste
- ✅ Cada vídeo mostra valor específico
- ✅ Clique para "assistir" e ganhar
- ✅ Crédito automático na conta

**Exemplo:**
```
📹 Vídeo 01 - Ganhe Dinheiro
   Assista por completo e ganhe R$ 0,55
   ⏱️ Duração: 60s
```

### 2. 💸 **Sacar Saldo (PIX)**
- ✅ Mostra saldo atual
- ✅ Saldo mínimo: R$ 20,00
- ✅ Primeira vez: Pergunta PIX
- ✅ PIX armazenado no banco
- ✅ Sua equipe valida e paga

**Fluxo:**
```
Saldo ≥ R$ 20,00?
├─ SIM: Mostra PIX + "Solicitar Saque"
└─ NÃO: Mostra quanto falta
```

### 3. 🔗 **Indique e Ganhe (Afiliados)**
- ✅ Link único por usuário
- ✅ Ganha 10% da receita dos indicados
- ✅ Rastreamento automático
- ✅ Comissão creditada automaticamente

**Repartição:**
```
SEM afiliado:
- PlayLucro: 30%
- Usuário: 70%

COM afiliado:
- Afiliado: 10%
- PlayLucro: 25%
- Usuário: 65%
```

### 4. 📊 **Histórico**
- ✅ Últimos 10 vídeos assistidos
- ✅ Mostra status (✅ Completo / ❌ Não completo)
- ✅ Valor ganho por vídeo
- ✅ Data e hora

### 5. ⚙️ **Configurações**
- ✅ Alterar Nome
- ✅ Alterar Cidade
- ✅ Alterar Idade
- ✅ Alterar PIX

### 6. 💬 **Suporte**
- ✅ Link direto: https://t.me/playlucro_suporte

---

## 🗄️ BANCO DE DADOS

**5 Tabelas criadas automaticamente:**

1. **usuarios** - Dados do usuário, saldo, PIX, link de afiliado
2. **videos** - Lista de vídeos disponíveis
3. **visualizacoes** - Histórico de vídeos assistidos
4. **transacoes** - Todas as transações (ganhos, comissões, saques)
5. **saques** - Solicitações de saque com status

---

## 🚀 COMO RODAR

```bash
# 1. Clonar repositório
git clone https://github.com/Lucrai2026/lucrai.git
cd lucrai

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar token (Windows)
set TELEGRAM_BOT_TOKEN=seu_token_aqui

# 4. Rodar o bot
python main.py
```

**Banco de dados:**
- Arquivo: `lucrai_db.sqlite`
- Criado automaticamente na primeira execução
- 5 vídeos de teste pré-carregados

---

## 📱 TESTANDO O BOT

### Teste 1: Cadastro
```
/start
→ Clique em "Cadastrar"
→ Digite: Nome, Cidade, Idade
→ Confirme
```

### Teste 2: Assistir Vídeo
```
Menu → 🎬 Assistir Vídeos
→ Clique em um vídeo
→ Veja saldo aumentar
```

### Teste 3: Saque
```
Menu → 💸 Sacar Saldo
→ Se saldo < R$ 20: Mostra quanto falta
→ Se saldo ≥ R$ 20: Pede PIX
→ Clique "Solicitar Saque"
```

### Teste 4: Afiliado
```
Menu → 🔗 Indique e Ganhe
→ Copie seu link
→ Compartilhe com amigos
→ Quando indicado assistir vídeo: Você ganha 10%
```

### Teste 5: Histórico
```
Menu → 📊 Histórico
→ Veja todos os vídeos assistidos
```

### Teste 6: Configurações
```
Menu → ⚙️ Configurações
→ Altere Nome, Cidade, Idade ou PIX
```

---

## 💡 EXEMPLOS DE USO

### Exemplo 1: Usuário Novo
```
1. Clica /start
2. Cadastra: João, São Paulo, 25 anos
3. Vai ao menu
4. Clica em "Assistir Vídeos"
5. Assiste "Vídeo 01" e ganha R$ 0,55
6. Saldo: R$ 0,55
7. Repete com mais vídeos até atingir R$ 20,00
8. Clica "Sacar Saldo"
9. Cadastra PIX
10. Solicita saque
11. Sua equipe valida e paga
```

### Exemplo 2: Afiliado
```
1. João tem link: https://t.me/playlucro_bot?start=ref_123456
2. João compartilha com Maria
3. Maria clica no link e se cadastra
4. Maria fica vinculada a João
5. Maria assiste vídeo de R$ 1,00
   - Maria ganha: R$ 0,65
   - João ganha: R$ 0,10 (10% de comissão)
   - PlayLucro ganha: R$ 0,25
```

---

## 🔐 SEGURANÇA

### Implementado
- ✅ Validação de dados
- ✅ Banco de dados com chaves estrangeiras
- ✅ Transações registradas
- ✅ Status de saques (pendente/pago)
- ✅ PIX armazenado

### A Implementar
- 🔲 Confirmação via API do AdscendMedia
- 🔲 Sistema anti-burla
- 🔲 Validação de PIX real
- 🔲 Criptografia de dados sensíveis

---

## 🔄 PRÓXIMAS ETAPAS

### Curto Prazo
1. Testar com usuários reais
2. Ajustar valores dos vídeos
3. Implementar sistema anti-burla

### Médio Prazo
1. Integrar com API real do AdscendMedia
2. Criar painel admin web
3. Adicionar notificações

### Longo Prazo
1. Sistema de níveis de afiliado
2. Bônus por desempenho
3. Múltiplos métodos de pagamento

---

## 📊 ESTATÍSTICAS DO CÓDIGO

- **Linhas de código:** ~800
- **Funções:** 30+
- **Tabelas de banco:** 5
- **Endpoints:** 6 botões principais
- **Estados de conversa:** 6

---

## 🎯 CHECKLIST

- [x] Cadastro de usuários
- [x] Menu com 6 botões
- [x] Sistema de vídeos
- [x] Assistir e ganhar
- [x] Histórico
- [x] Saque com PIX
- [x] Afiliados (10% revenue share)
- [x] Configurações
- [x] Suporte
- [x] Banco de dados
- [ ] API do AdscendMedia
- [ ] Painel admin web
- [ ] Sistema anti-burla

---

## 📞 SUPORTE

**Grupo de Suporte:** https://t.me/playlucro_suporte

**Repositório:** https://github.com/Lucrai2026/lucrai

---

## 🎉 PRONTO PARA USAR!

O bot está **100% funcional** e pronto para testes!

Qualquer dúvida, entre em contato com a equipe de suporte.

**Versão:** 2.0  
**Data:** 15/11/2025  
**Status:** ✅ Completo e Funcional
