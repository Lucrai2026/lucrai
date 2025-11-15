# 🎬 GUIA DE INTEGRAÇÃO COM APIs DE ADS

## 📋 ÍNDICE
1. [Opções de APIs](#opções-de-apis)
2. [AdscendMedia](#adscendmedia)
3. [CPMLink](#cpmlink)
4. [YouTube API](#youtube-api)
5. [Implementação](#implementação)
6. [Testes](#testes)

---

## 🎯 OPÇÕES DE APIs

### Comparação

| API | Vantagens | Desvantagens | Comissão |
|-----|-----------|--------------|----------|
| **AdscendMedia** | Fácil integração, suporte bom | Requer aprovação | 30-50% |
| **CPMLink** | Muitos vídeos, confiável | Mais complexo | 20-40% |
| **YouTube** | Conteúdo de qualidade | Requer OAuth2 | Variável |
| **Simples** | Rápido de implementar | Poucos vídeos | 50% |

---

## 🔑 ADSCENDMEDIA

### Passo 1: Criar Conta

1. Acesse: https://adscendmedia.com
2. Clique em "Sign Up"
3. Preencha formulário
4. Aguarde aprovação (24-48h)

### Passo 2: Obter Credenciais

```
Dashboard → Settings → API Keys
- Publisher ID: xxxxx
- API Key: xxxxx
```

### Passo 3: Implementar no Bot

```python
import aiohttp
import json

ADSCEND_API_KEY = "sua_api_key_aqui"
ADSCEND_PUBLISHER_ID = "seu_publisher_id_aqui"

async def obter_videos_adscend():
    """Busca vídeos da AdscendMedia"""
    url = "https://api.adscendmedia.com/videos"
    headers = {
        "Authorization": f"Bearer {ADSCEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data['videos']
            else:
                logger.error(f"Erro ao buscar vídeos: {response.status}")
                return []

async def validar_visualizacao_adscend(video_id, user_id):
    """Valida se vídeo foi realmente assistido"""
    url = f"https://api.adscendmedia.com/validate/{video_id}"
    headers = {
        "Authorization": f"Bearer {ADSCEND_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data['valid']
            else:
                return False

async def registrar_visualizacao_adscend(video_id, user_id, valor):
    """Registra visualização e recebe confirmação"""
    # Validar com API
    if await validar_visualizacao_adscend(video_id, user_id):
        # Registrar no banco local
        registrar_visualizacao(user_id, video_id, valor)
        return True
    else:
        logger.warning(f"Visualização inválida: {user_id} - {video_id}")
        return False
```

### Passo 4: Atualizar Função assistir_video

```python
async def assistir_video(query, usuario, video_id):
    """Processa a assistência de um vídeo (com validação AdscendMedia)"""
    try:
        # Buscar vídeo do banco
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute('SELECT titulo, url, valor FROM videos WHERE id = ?', (video_id,))
        video = cursor.fetchone()
        conn.close()
        
        if not video:
            await query.edit_message_text('Vídeo não encontrado.')
            return
        
        titulo, url, valor = video
        
        # NOVO: Validar com AdscendMedia
        if not await registrar_visualizacao_adscend(video_id, usuario['user_id'], valor):
            await query.message.reply_text('❌ Erro ao validar visualização. Tente novamente.')
            return
        
        # Atualizar saldo do usuário
        usuario_atualizado = obter_usuario(usuario['user_id'])
        
        texto = f'''✅ <b>Vídeo Assistido com Sucesso!</b>

📹 <b>{titulo}</b>
💰 <b>Você ganhou: R$ {valor:.2f}</b>

💵 <b>Seu novo saldo:</b> R$ {usuario_atualizado['saldo']:.2f}

Parabéns! Continue assistindo para ganhar mais! 🎉'''
        
        keyboard = [[InlineKeyboardButton('🎬 Voltar aos Vídeos', callback_data='videos')]]
        
        try:
            await query.message.delete()
        except:
            pass
        
        await query.message.reply_text(
            texto,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f'Erro ao assistir vídeo: {e}')
        try:
            await query.edit_message_text(f'Erro: {str(e)}')
        except:
            pass
```

---

## 🔗 CPMLINK

### Passo 1: Criar Conta

1. Acesse: https://cpmlink.com
2. Clique em "Register"
3. Preencha formulário
4. Aguarde aprovação

### Passo 2: Obter Credenciais

```
Account → API Settings
- User ID: xxxxx
- API Token: xxxxx
```

### Passo 3: Implementar

```python
async def obter_videos_cpmlink():
    """Busca vídeos da CPMLink"""
    url = "https://api.cpmlink.com/videos"
    headers = {
        "Authorization": f"Bearer {CPMLINK_API_TOKEN}",
        "User-ID": CPMLINK_USER_ID
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                # Transformar para formato local
                videos = []
                for v in data['videos']:
                    videos.append({
                        'id': v['video_id'],
                        'titulo': v['title'],
                        'valor': v['reward'],
                        'url': v['video_url']
                    })
                return videos
            return []
```

---

## 📺 YOUTUBE API

### Passo 1: Criar Projeto Google Cloud

1. Acesse: https://console.cloud.google.com
2. Crie novo projeto
3. Ative YouTube Data API v3
4. Crie credenciais OAuth 2.0

### Passo 2: Implementar

```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

async def obter_videos_youtube(channel_id):
    """Busca vídeos do YouTube"""
    youtube = build('youtube', 'v3', credentials=get_youtube_credentials())
    
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        type='video',
        maxResults=10,
        order='date'
    )
    
    response = request.execute()
    
    videos = []
    for item in response['items']:
        videos.append({
            'id': item['id']['videoId'],
            'titulo': item['snippet']['title'],
            'valor': 0.50,  # Valor fixo
            'url': f"https://youtube.com/watch?v={item['id']['videoId']}"
        })
    
    return videos
```

---

## 💻 IMPLEMENTAÇÃO COMPLETA

### Estrutura Recomendada

```python
# config.py
ADS_PROVIDER = "adscendmedia"  # ou "cpmlink", "youtube"

ADS_CONFIG = {
    "adscendmedia": {
        "api_key": os.getenv("ADSCEND_API_KEY"),
        "publisher_id": os.getenv("ADSCEND_PUBLISHER_ID"),
        "base_url": "https://api.adscendmedia.com"
    },
    "cpmlink": {
        "api_token": os.getenv("CPMLINK_API_TOKEN"),
        "user_id": os.getenv("CPMLINK_USER_ID"),
        "base_url": "https://api.cpmlink.com"
    }
}

# ads_service.py
class AdsService:
    def __init__(self, provider):
        self.provider = provider
        self.config = ADS_CONFIG[provider]
    
    async def obter_videos(self):
        if self.provider == "adscendmedia":
            return await self._obter_videos_adscend()
        elif self.provider == "cpmlink":
            return await self._obter_videos_cpmlink()
    
    async def validar_visualizacao(self, video_id, user_id):
        if self.provider == "adscendmedia":
            return await self._validar_adscend(video_id, user_id)
        elif self.provider == "cpmlink":
            return await self._validar_cpmlink(video_id, user_id)
    
    # ... implementar métodos específicos

# main.py
ads_service = AdsService(ADS_PROVIDER)

async def assistir_video(query, usuario, video_id):
    # Usar ads_service
    if await ads_service.validar_visualizacao(video_id, usuario['user_id']):
        # Registrar ganho
        pass
```

---

## 🧪 TESTES

### Teste Local

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_obter_videos():
    videos = await obter_videos_adscend()
    assert len(videos) > 0
    assert 'id' in videos[0]
    assert 'titulo' in videos[0]
    assert 'valor' in videos[0]

@pytest.mark.asyncio
async def test_validar_visualizacao():
    # Usar video_id e user_id de teste
    resultado = await validar_visualizacao_adscend(1, 123456)
    assert isinstance(resultado, bool)

# Rodar testes
# pytest test_ads.py -v
```

### Teste com Sandbox

```bash
# Criar arquivo .env
ADSCEND_API_KEY=sua_chave_teste
ADSCEND_PUBLISHER_ID=seu_id_teste

# Rodar bot em modo teste
python main.py --test-mode
```

---

## 📊 MONITORAMENTO

### Logs

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Registrar todas as chamadas à API
logger.info(f"Buscando vídeos da {ADS_PROVIDER}")
logger.info(f"Validando visualização: video={video_id}, user={user_id}")
logger.error(f"Erro ao validar: {error}")
```

### Métricas

```python
# Rastrear sucesso/falha
stats = {
    'videos_buscados': 0,
    'visualizacoes_validadas': 0,
    'visualizacoes_falhadas': 0,
    'ganhos_totais': 0.0
}

async def registrar_visualizacao_adscend(video_id, user_id, valor):
    if await validar_visualizacao_adscend(video_id, user_id):
        stats['visualizacoes_validadas'] += 1
        stats['ganhos_totais'] += valor
        return True
    else:
        stats['visualizacoes_falhadas'] += 1
        return False
```

---

## 🚀 DEPLOYMENT

### Variáveis de Ambiente

```bash
# .env
TELEGRAM_BOT_TOKEN=seu_token
DATABASE_URL=sqlite:///lucrai_db.sqlite

# AdscendMedia
ADSCEND_API_KEY=sua_chave
ADSCEND_PUBLISHER_ID=seu_id

# Ou CPMLink
CPMLINK_API_TOKEN=seu_token
CPMLINK_USER_ID=seu_id

# Ou YouTube
YOUTUBE_API_KEY=sua_chave
YOUTUBE_CHANNEL_ID=seu_channel
```

### Docker

```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

---

## 📞 SUPORTE

### Contatos das Plataformas

| Plataforma | Email | Site |
|-----------|-------|------|
| AdscendMedia | support@adscendmedia.com | https://adscendmedia.com |
| CPMLink | support@cpmlink.com | https://cpmlink.com |
| YouTube | support.google.com | https://youtube.com |

---

**Versão:** 1.0  
**Data:** 15/11/2025  
**Status:** ✅ Pronto para implementação
