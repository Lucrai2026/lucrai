# 💳 GUIA DE SISTEMA DE PAGAMENTO PIX

## 📋 ÍNDICE
1. [Visão Geral](#visão-geral)
2. [Opções de Implementação](#opções-de-implementação)
3. [Banco Inter (RECOMENDADO)](#banco-inter-recomendado)
4. [Nubank](#nubank)
5. [Stripe](#stripe)
6. [Implementação Completa](#implementação-completa)
7. [Segurança](#segurança)

---

## 🎯 VISÃO GERAL

### Fluxo Atual (Manual)
```
Usuário → Solicita Saque → Registra no BD → Status: Pendente
Admin → Valida → Transfere PIX manualmente → Status: Pago
```

### Fluxo Desejado (Automático)
```
Usuário → Solicita Saque → Valida PIX → Transfere Automático → Status: Pago
```

---

## 🔄 OPÇÕES DE IMPLEMENTAÇÃO

### Comparação

| Solução | Vantagens | Desvantagens | Custo |
|---------|-----------|--------------|-------|
| **Banco Inter** | PIX nativo, fácil, rápido | Requer conta | Grátis |
| **Nubank** | Moderno, suporte bom | Menos documentação | Grátis |
| **Stripe** | Confiável, completo | Mais caro, complexo | 2.9% + R$ 0,30 |
| **PayPal** | Internacional | Mais lento | 3.49% + R$ 0,60 |
| **Manual** | Simples | Demorado, propenso a erros | Grátis |

---

## 🏦 BANCO INTER (RECOMENDADO)

### Por Que Banco Inter?
- ✅ API PIX nativa
- ✅ Transferências instantâneas
- ✅ Sem taxa para transferências
- ✅ Ótima documentação
- ✅ Suporte rápido

### Passo 1: Criar Conta

1. Acesse: https://www.bancointer.com.br
2. Clique em "Abrir Conta"
3. Preencha formulário
4. Aguarde aprovação (1-2 dias)

### Passo 2: Gerar Credenciais API

```
Dashboard → Configurações → API
- Client ID: xxxxx
- Client Secret: xxxxx
- Chave PIX: xxxxx
```

### Passo 3: Implementar

```python
import requests
import json
from datetime import datetime

BANCO_INTER_CLIENT_ID = "seu_client_id"
BANCO_INTER_CLIENT_SECRET = "seu_client_secret"
BANCO_INTER_PIX_KEY = "sua_chave_pix"

class BancoInterAPI:
    def __init__(self):
        self.base_url = "https://api.bancointer.com.br/v2"
        self.token = None
        self.token_expiry = None
    
    async def obter_token(self):
        """Obtém token de autenticação"""
        if self.token and datetime.now() < self.token_expiry:
            return self.token
        
        url = f"{self.base_url}/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": BANCO_INTER_CLIENT_ID,
            "client_secret": BANCO_INTER_CLIENT_SECRET
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            result = response.json()
            self.token = result['access_token']
            # Token expira em 3600s, usar 3500s para segurança
            self.token_expiry = datetime.now() + timedelta(seconds=3500)
            return self.token
        else:
            logger.error(f"Erro ao obter token: {response.text}")
            return None
    
    async def validar_pix(self, chave_pix):
        """Valida se chave PIX é válida"""
        token = await self.obter_token()
        if not token:
            return False
        
        url = f"{self.base_url}/pix/validate"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "key": chave_pix
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return True
        else:
            logger.warning(f"PIX inválido: {chave_pix}")
            return False
    
    async def transferir_pix(self, chave_pix, valor, descricao):
        """Realiza transferência PIX"""
        token = await self.obter_token()
        if not token:
            return {'success': False, 'error': 'Erro de autenticação'}
        
        # Validar PIX antes de transferir
        if not await self.validar_pix(chave_pix):
            return {'success': False, 'error': 'PIX inválido'}
        
        url = f"{self.base_url}/pix/transfer"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "key": chave_pix,
            "amount": int(valor * 100),  # Converter para centavos
            "description": descricao,
            "idempotency_key": f"saque_{datetime.now().timestamp()}"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'transaction_id': result['id'],
                'status': 'pago'
            }
        else:
            logger.error(f"Erro ao transferir: {response.text}")
            return {
                'success': False,
                'error': response.json().get('message', 'Erro desconhecido')
            }

# Instância global
banco_inter = BancoInterAPI()
```

### Passo 4: Integrar com Bot

```python
async def processar_saque(query, usuario):
    """Processa solicitação de saque"""
    try:
        # Validar saldo mínimo
        if usuario['saldo'] < 20:
            await query.message.reply_text(
                '❌ Saldo mínimo para sacar é R$ 20,00'
            )
            return
        
        # Validar PIX
        if not usuario['pix']:
            await query.message.reply_text(
                '❌ Você não cadastrou PIX. Use /configuracoes para cadastrar.'
            )
            return
        
        # Transferir PIX
        resultado = await banco_inter.transferir_pix(
            usuario['pix'],
            usuario['saldo'],
            f"Saque PlayLucro - Usuário {usuario['user_id']}"
        )
        
        if resultado['success']:
            # Atualizar banco de dados
            conn = sqlite3.connect(DB_FILE, timeout=10.0)
            cursor = conn.cursor()
            
            # Registrar saque
            cursor.execute('''
                INSERT INTO saques (user_id, valor, pix, status, transaction_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                usuario['user_id'],
                usuario['saldo'],
                usuario['pix'],
                'pago',
                resultado['transaction_id']
            ))
            
            # Zerar saldo
            cursor.execute(
                'UPDATE usuarios SET saldo = 0 WHERE user_id = ?',
                (usuario['user_id'],)
            )
            
            conn.commit()
            conn.close()
            
            # Confirmar para usuário
            await query.message.reply_text(
                f'''✅ <b>Saque Realizado com Sucesso!</b>

💰 <b>Valor:</b> R$ {usuario['saldo']:.2f}
📱 <b>PIX:</b> {usuario['pix']}
⏱️ <b>Status:</b> Pago (instantâneo)

O dinheiro já está na sua conta!

Obrigado por usar PlayLucro! 🎉''',
                parse_mode='HTML'
            )
            
            logger.info(f"Saque realizado: {usuario['user_id']} - R$ {usuario['saldo']:.2f}")
        else:
            await query.message.reply_text(
                f'❌ Erro ao processar saque: {resultado["error"]}'
            )
            logger.error(f"Erro no saque: {resultado['error']}")
    
    except Exception as e:
        logger.error(f"Erro ao processar saque: {e}")
        await query.message.reply_text(f'❌ Erro: {str(e)}')
```

---

## 🏦 NUBANK

### Implementação Similar

```python
class NubankAPI:
    def __init__(self):
        self.base_url = "https://api.nubank.com.br"
        self.api_key = os.getenv("NUBANK_API_KEY")
    
    async def transferir_pix(self, chave_pix, valor, descricao):
        """Transferência PIX via Nubank"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "receiver_key": chave_pix,
            "amount": int(valor * 100),
            "description": descricao
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/pix/transfer",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {'success': True, 'transaction_id': data['id']}
                else:
                    return {'success': False, 'error': 'Erro na transferência'}
```

---

## 💳 STRIPE

### Implementação

```python
import stripe

stripe.api_key = os.getenv("STRIPE_API_KEY")

async def transferir_stripe(chave_pix, valor, descricao):
    """Transferência via Stripe (para cartão)"""
    try:
        # Criar pagamento
        payment = stripe.PaymentIntent.create(
            amount=int(valor * 100),
            currency="brl",
            description=descricao,
            payment_method_types=["card"]
        )
        
        return {
            'success': True,
            'transaction_id': payment.id,
            'client_secret': payment.client_secret
        }
    except stripe.error.CardError as e:
        return {'success': False, 'error': str(e)}
```

---

## 💻 IMPLEMENTAÇÃO COMPLETA

### Estrutura Recomendada

```python
# payment_service.py
class PaymentService:
    def __init__(self, provider="banco_inter"):
        self.provider = provider
        
        if provider == "banco_inter":
            self.api = BancoInterAPI()
        elif provider == "nubank":
            self.api = NubankAPI()
        elif provider == "stripe":
            self.api = StripeAPI()
    
    async def validar_pix(self, chave_pix):
        """Valida chave PIX"""
        if self.provider == "banco_inter":
            return await self.api.validar_pix(chave_pix)
        # ... outros providers
    
    async def transferir(self, chave_pix, valor, descricao):
        """Realiza transferência"""
        return await self.api.transferir_pix(chave_pix, valor, descricao)

# main.py
payment_service = PaymentService("banco_inter")

async def solicitar_saque(query, usuario):
    """Solicita saque"""
    # Validar PIX
    if not await payment_service.validar_pix(usuario['pix']):
        await query.message.reply_text('❌ PIX inválido')
        return
    
    # Transferir
    resultado = await payment_service.transferir(
        usuario['pix'],
        usuario['saldo'],
        f"Saque PlayLucro"
    )
    
    if resultado['success']:
        # Atualizar BD
        pass
```

---

## 🔐 SEGURANÇA

### Boas Práticas

```python
# 1. Nunca armazenar chaves em código
# Usar variáveis de ambiente
BANCO_INTER_API_KEY = os.getenv("BANCO_INTER_API_KEY")

# 2. Validar PIX antes de transferir
if not await validar_pix(chave_pix):
    return False

# 3. Usar HTTPS sempre
# Configurar SSL no servidor

# 4. Implementar rate limiting
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=10, period=60)
async def transferir_pix(chave_pix, valor):
    # Máximo 10 transferências por minuto
    pass

# 5. Registrar todas as transações
logger.info(f"Transferência: {user_id} - R$ {valor} - {chave_pix}")

# 6. Implementar retry automático
async def transferir_com_retry(chave_pix, valor, max_retries=3):
    for attempt in range(max_retries):
        try:
            resultado = await banco_inter.transferir_pix(chave_pix, valor)
            if resultado['success']:
                return resultado
        except Exception as e:
            logger.warning(f"Tentativa {attempt+1} falhou: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    return {'success': False, 'error': 'Falha após múltiplas tentativas'}

# 7. Webhook para confirmação
@app.post("/webhook/pix")
async def webhook_pix(request):
    """Recebe confirmação de PIX"""
    data = await request.json()
    
    # Validar assinatura
    if not validar_assinatura(data):
        return {"error": "Assinatura inválida"}
    
    # Atualizar status
    transaction_id = data['transaction_id']
    status = data['status']
    
    # Atualizar BD
    atualizar_saque_status(transaction_id, status)
    
    return {"success": True}
```

---

## 📊 MONITORAMENTO

### Dashboard de Saques

```python
async def gerar_relatorio_saques():
    """Gera relatório de saques"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            DATE(data_saque) as data,
            COUNT(*) as quantidade,
            SUM(valor) as total,
            COUNT(CASE WHEN status='pago' THEN 1 END) as pagos,
            COUNT(CASE WHEN status='pendente' THEN 1 END) as pendentes
        FROM saques
        GROUP BY DATE(data_saque)
        ORDER BY data DESC
        LIMIT 30
    ''')
    
    relatorio = cursor.fetchall()
    conn.close()
    
    return relatorio

# Enviar relatório diário
async def enviar_relatorio_diario():
    relatorio = await gerar_relatorio_saques()
    
    texto = "📊 <b>Relatório de Saques - Hoje</b>\n\n"
    for data, qtd, total, pagos, pendentes in relatorio[:1]:
        texto += f"📅 Data: {data}\n"
        texto += f"📦 Quantidade: {qtd}\n"
        texto += f"💰 Total: R$ {total:.2f}\n"
        texto += f"✅ Pagos: {pagos}\n"
        texto += f"⏳ Pendentes: {pendentes}\n"
    
    # Enviar para admin
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=texto,
        parse_mode='HTML'
    )
```

---

## 🚀 DEPLOYMENT

### Variáveis de Ambiente

```bash
# .env
PAYMENT_PROVIDER=banco_inter

# Banco Inter
BANCO_INTER_CLIENT_ID=xxxxx
BANCO_INTER_CLIENT_SECRET=xxxxx
BANCO_INTER_PIX_KEY=xxxxx

# Ou Nubank
NUBANK_API_KEY=xxxxx

# Ou Stripe
STRIPE_API_KEY=xxxxx
STRIPE_WEBHOOK_SECRET=xxxxx
```

### Docker Compose

```yaml
version: '3'
services:
  bot:
    build: .
    environment:
      - PAYMENT_PROVIDER=banco_inter
      - BANCO_INTER_CLIENT_ID=${BANCO_INTER_CLIENT_ID}
      - BANCO_INTER_CLIENT_SECRET=${BANCO_INTER_CLIENT_SECRET}
    volumes:
      - ./lucrai_db.sqlite:/app/lucrai_db.sqlite
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Escolher provider de pagamento
- [ ] Criar conta no banco/serviço
- [ ] Obter credenciais API
- [ ] Implementar classe de API
- [ ] Integrar com bot
- [ ] Testar com valores pequenos
- [ ] Implementar validação de PIX
- [ ] Implementar retry automático
- [ ] Configurar webhooks
- [ ] Implementar logging
- [ ] Testar em produção
- [ ] Monitorar transações
- [ ] Configurar alertas

---

**Versão:** 1.0  
**Data:** 15/11/2025  
**Status:** ✅ Pronto para implementação
