# 📋 COMANDOS DO PLAYLUCRO BOT v2.0

## 🎮 COMANDOS PRINCIPAIS

| Comando | Descrição | Como Usar | Resultado |
|---------|-----------|-----------|-----------|
| `/start` | Inicia o bot | Digite `/start` no Telegram | Mostra mensagem de boas-vindas com imagem |
| `🚀 Clique aqui para Cadastrar` | Cadastra novo usuário | Clique no botão após `/start` | Pede nome, cidade e idade |
| `🎬 Assistir Vídeos` | Abre menu de vídeos | Clique no botão no menu principal | Mostra lista de vídeos disponíveis |
| `▶️ Vídeo 01-05` | Assiste um vídeo | Clique em um vídeo específico | Simula assistência e credita valor |
| `💸 Sacar Saldo` | Abre menu de saque | Clique no botão no menu principal | Mostra saldo e opções de saque |
| `📝 Cadastrar PIX` | Cadastra chave PIX | Clique no botão em "Sacar Saldo" | Pede para digitar a chave PIX |
| `✅ Solicitar Saque` | Solicita saque de saldo | Clique no botão após cadastrar PIX | Cria solicitação de saque (mín. R$ 20) |
| `🔗 Indique e Ganhe` | Abre menu de afiliados | Clique no botão no menu principal | Mostra link de indicação e comissões |
| `📊 Histórico` | Mostra histórico de vídeos | Clique no botão no menu principal | Lista últimos 10 vídeos assistidos |
| `⚙️ Configurações` | Abre configurações | Clique no botão no menu principal | Permite alterar dados do perfil |
| `👤 Alterar Nome` | Muda o nome | Clique em "Configurações" → "Alterar Nome" | Pede novo nome |
| `🏙️ Alterar Cidade` | Muda a cidade | Clique em "Configurações" → "Alterar Cidade" | Pede nova cidade |
| `🎂 Alterar Idade` | Muda a idade | Clique em "Configurações" → "Alterar Idade" | Pede nova idade |
| `📱 Alterar PIX` | Muda a chave PIX | Clique em "Configurações" → "Alterar PIX" | Pede nova chave PIX |
| `💬 Suporte` | Abre grupo de suporte | Clique no botão no menu principal | Redireciona para grupo do Telegram |
| `◀️ Voltar ao Menu` | Volta ao menu anterior | Clique em qualquer botão "Voltar" | Retorna ao menu principal |

---

## 👑 COMANDOS DO DONO (ADMIN)

| Comando | Descrição | Como Usar | Resultado |
|---------|-----------|-----------|-----------|
| `/broadcast` | Envia mensagem para TODOS | `/broadcast Olá pessoal! Novo vídeo disponível!` | Envia a mensagem para todos os usuários cadastrados |
| `/broadcast_image` | Envia imagem para TODOS | `/broadcast_image Legenda aqui` + responda com imagem | Envia a imagem com legenda para todos os usuários |

**Nota:** Apenas o dono consegue usar estes comandos. Outros usuários recebem "Sem permissão!"

---

## 📊 INFORMAÇÕES DO USUÁRIO

### Dados Armazenados
- **Nome:** Nome do usuário
- **Cidade:** Cidade onde mora
- **Idade:** Idade do usuário
- **PIX:** Chave PIX para receber saques
- **Saldo:** Dinheiro ganho assistindo vídeos
- **Link de Afiliado:** Link único para indicar amigos
- **Comissões:** Total ganho indicando pessoas

### Valores Padrão
- **Vídeo 01:** R$ 0,30
- **Vídeo 02:** R$ 0,40
- **Vídeo 03:** R$ 0,50
- **Vídeo 04:** R$ 0,60
- **Vídeo 05:** R$ 0,75
- **Saldo Mínimo para Sacar:** R$ 20,00
- **Comissão de Afiliado:** 10% do ganho

---

## 🔄 FLUXO DE USO

```
1. /start
   ↓
2. 🚀 Clique aqui para Cadastrar
   ↓
3. Preencher: Nome, Cidade, Idade
   ↓
4. Menu Principal (6 botões)
   ├─ 🎬 Assistir Vídeos → Ganhar dinheiro
   ├─ 💸 Sacar Saldo → Receber via PIX
   ├─ 🔗 Indique e Ganhe → Ganhar comissão
   ├─ 📊 Histórico → Ver atividades
   ├─ ⚙️ Configurações → Alterar dados
   └─ 💬 Suporte → Ir para grupo
```

---

## 💡 DICAS IMPORTANTES

### Para Usuários
1. **Ganhar Dinheiro:** Assista vídeos regularmente
2. **Aumentar Ganhos:** Indique amigos e ganhe 10% de comissão
3. **Sacar Dinheiro:** Acumule R$ 20,00 e solicite saque
4. **Manter Dados Atualizados:** Use "Configurações" para alterar PIX

### Para o Dono
1. **Enviar Notificações:** Use `/broadcast` para avisar sobre novos vídeos
2. **Enviar Imagens:** Use `/broadcast_image` para campanhas visuais
3. **Monitorar Usuários:** Verifique o banco de dados para estatísticas
4. **Validar Saques:** Aprove saques manualmente quando solicitado

---

## 🗄️ BANCO DE DADOS

### Tabelas
- **usuarios:** Dados dos usuários (nome, cidade, idade, PIX, saldo, etc)
- **videos:** Lista de vídeos disponíveis (título, URL, valor, duração)
- **visualizacoes:** Histórico de vídeos assistidos
- **transacoes:** Histórico de ganhos e comissões
- **saques:** Solicitações de saque (status: pendente/pago)

---

## 📱 COMO ACESSAR O BOT

**Link do Bot:** https://t.me/Playlucro_bot

**Ou procure por:** @Playlucro_bot

---

## 🎊 RESUMO

- ✅ 6 botões no menu principal
- ✅ Sistema de vídeos com simulação
- ✅ Sistema de saque com PIX
- ✅ Sistema de afiliados (10% comissão)
- ✅ Histórico de atividades
- ✅ Configurações do perfil
- ✅ Broadcast para notificações
- ✅ Chat sempre limpo

**Versão:** 2.0  
**Data:** 15/11/2025  
**Status:** ✅ Completo e Funcional
