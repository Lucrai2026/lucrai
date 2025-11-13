# =================================================================================
# ||||||||||||||||||||||||||| PROJETO LUCRAÍ ||||||||||||||||||||||||||||||||||||
# =================================================================================
# Arquivo: main.py
# Descrição: Código principal do bot do Telegram para o projeto Lucraí.
# Versão: 1.6 (Correção Final do Fluxo de Cadastro)
# =================================================================================

import logging
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# --- Configuração de Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Definição dos Estágios da Conversa ---
INICIO, NOME, DATA_NASCIMENTO, CIDADE, EMAIL, CONFIRMACAO, MENU, SACAR_SALDO, RECEBER_PIX = range(9)

DB_NAME = "lucrai_db.sqlite"

# =================================================================================
# |||||||||||||||||||||||||||| FUNÇÕES DE BANCO DE DADOS ||||||||||||||||||||||||||
# =================================================================================

def init_db() -> None:
    """Inicializa o banco de dados e cria a tabela de usuários se não existir."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            user_id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            data_nascimento TEXT,
            cidade TEXT,
            email TEXT UNIQUE NOT NULL,
            saldo REAL DEFAULT 0.0,
            indicador_id INTEGER,
            chave_pix TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def update_user_pix(user_id: int, chave_pix: str) -> None:
    """Atualiza a chave PIX de um usuário no banco de dados."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE usuarios SET chave_pix = ? WHERE user_id = ?
        """,
        (chave_pix, user_id),
    )
    conn.commit()
    conn.close()

def get_user(user_id: int) -> Optional[tuple]:
    """Busca um usuário pelo ID no banco de dados."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_saldo(user_id: int, valor: float) -> None:
    """Atualiza o saldo de um usuário no banco de dados."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE usuarios SET saldo = saldo + ? WHERE user_id = ?
        """,
        (valor, user_id),
    )
    conn.commit()
    conn.close()

def save_user(user_id: int, nome: str, data_nascimento: str, cidade: str, email: str) -> None:
    """Salva um novo usuário no banco de dados."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO usuarios (user_id, nome, data_nascimento, cidade, email)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, nome, data_nascimento, cidade, email),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        logger.error(f"Erro de integridade ao salvar usuário {user_id}. Email já existe ou user_id duplicado.")
    finally:
        conn.close()

# =================================================================================
# |||||||||||||||||||||||| FUNÇÕES DO FLUXO DE CADASTRO |||||||||||||||||||||||||
# =================================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia a conversa de cadastro ou exibe o menu principal se já estiver cadastrado."""
    user = update.effective_user
    logger.info(f"Usuário {user.username} (ID: {user.id}) iniciou o bot.")
    
    # Lógica de checagem de cadastro (agora com DB)
    user_data = get_user(user.id)
    if user_data:
        # Salva os dados do DB no user_data do contexto para uso posterior
        context.user_data["nome"] = user_data[1]
        context.user_data["saldo"] = user_data[5]
        await update.message.reply_text("Bem-vindo de volta! Seu painel está pronto.")
        return await menu_principal(update, context)

    texto_boas_vindas = (
        "<b>Seja bem-vindo ao Lucraí!</b> 🚀\n\n"
        "Mas afinal, o que é este poderoso bot no Telegram?\n\n"
        "É uma ferramenta onde você vai ganhar dinheiro diretamente conosco, aqui no Telegram. Simples assim!\n\n"
        "<b>Como funciona?</b>\n"
        "Você se cadastra, recebe \"missões\" (como assistir a vídeos, responder pesquisas, etc.) e, para cada missão completada, você recebe um valor em dinheiro. É uma forma simples e divertida de fazer uma boa renda extra.\n\n"
        "E aí, vamos começar?"
    )
    
    reply_keyboard = [["🚀 Sim, vamos começar!"]]
    
    await update.message.reply_html(
        texto_boas_vindas,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return INICIO

async def iniciar_cadastro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia o processo de cadastro após o usuário clicar no botão."""
    await update.message.reply_text("Ótimo! Para começar, qual o seu nome completo?", reply_markup=ReplyKeyboardRemove())
    return NOME

async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["nome"] = update.message.text
    logger.info(f"Nome recebido: {update.message.text}")
    await update.message.reply_text("Obrigado! Agora, qual é a sua data de nascimento? (Formato: DD/MM/AAAA)")
    return DATA_NASCIMENTO

async def receber_data_nascimento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["data_nascimento"] = update.message.text
    logger.info(f"Data de Nascimento recebida: {update.message.text}")
    await update.message.reply_text("Perfeito. Em qual cidade você mora? Isso nos ajuda a encontrar as melhores atividades na sua região para você!")
    return CIDADE

async def receber_cidade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["cidade"] = update.message.text
    logger.info(f"Cidade recebida: {update.message.text}")
    await update.message.reply_text("Quase lá! Qual é o seu melhor e-mail para contato e notificações?")
    return EMAIL

async def receber_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["email"] = update.message.text
    logger.info(f"Email recebido: {update.message.text}")

    nome = context.user_data.get("nome", "Não informado")
    data_nascimento = context.user_data.get("data_nascimento", "Não informada")
    cidade = context.user_data.get("cidade", "Não informada")
    email = context.user_data.get("email", "Não informado")
    
    reply_keyboard = [["Sim, está tudo certo!"], ["Não, quero corrigir"]]
    
    await update.message.reply_html(
        f"Perfeito! Vamos confirmar seus dados:\n\n"
        f"👤 <b>Nome:</b> {nome}\n"
        f"🎂 <b>Nascimento:</b> {data_nascimento}\n"
        f"🏙️ <b>Cidade:</b> {cidade}\n"
        f"📧 <b>Email:</b> {email}\n\n"
        "Está tudo correto?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return CONFIRMACAO

async def receber_confirmacao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    resposta = update.message.text
    if resposta == "Sim, está tudo certo!":
        logger.info("Usuário confirmou o cadastro.")
        
        user_id = update.effective_user.id
        nome = context.user_data.get("nome", "")
        data_nascimento = context.user_data.get("data_nascimento", "")
        cidade = context.user_data.get("cidade", "")
        email = context.user_data.get("email", "")
        
        save_user(user_id, nome, data_nascimento, cidade, email)
        
        # O saldo inicial é 0.0, mas o menu_principal espera que esteja no context.user_data
        context.user_data["saldo"] = 0.0
        
        await update.message.reply_text("✅ Cadastro concluído com sucesso!", reply_markup=ReplyKeyboardRemove())
        return await menu_principal(update, context)
    else:
        logger.info("Usuário optou por corrigir os dados.")
        await update.message.reply_text("Ok, vamos começar de novo.", reply_markup=ReplyKeyboardRemove())
        return await start(update, context)

# =================================================================================
# |||||||||||||||||||||||||||| FUNÇÕES DE NAVEGAÇÃO ||||||||||||||||||||||||||||
# =================================================================================

async def menu_videos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exibe o menu de tarefas de vídeos."""
    
    videos_keyboard = [
        ["🎥 Vídeo 1 (R$ 0.50)", "🎥 Vídeo 2 (R$ 0.75)"],
        ["🎥 Vídeo 3 (R$ 1.00)", "⬅️ Voltar ao Menu Principal"],
    ]
    
    await update.message.reply_html(
        "<b>🎬 Ganhe assistindo a vídeos</b>\n\n"
        "Assista aos vídeos abaixo e receba o valor creditado em seu saldo imediatamente!",
        reply_markup=ReplyKeyboardMarkup(
            videos_keyboard, resize_keyboard=True, one_time_keyboard=False
        ),
    )
    return MENU

async def assistir_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Simula o ato de assistir a um vídeo e credita o saldo."""
    texto = update.message.text
    user_id = update.effective_user.id
    
    if "Vídeo 1" in texto:
        valor = 0.50
    elif "Vídeo 2" in texto:
        valor = 0.75
    elif "Vídeo 3" in texto:
        valor = 1.00
    else:
        return await navegar_menu(update, context) # Volta para o menu principal se for "Voltar" ou não reconhecido
        
    update_user_saldo(user_id, valor)
    
    await update.message.reply_html(
        f"✅ Você assistiu ao {texto.split('(')[0].strip()} e recebeu <b>R$ {valor:.2f}</b> em seu saldo!\n\n"
        "Selecione o próximo vídeo ou volte ao menu principal."
    )
    return MENU

async def menu_pesquisas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exibe o menu de tarefas de pesquisas."""
    await update.message.reply_text("Você está na seção de Pesquisas. Em breve, as tarefas de pesquisas estarão disponíveis aqui.")
    return MENU

async def menu_apps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exibe o menu de tarefas de aplicativos."""
    await update.message.reply_text("Você está na seção de Aplicativos. Em breve, as tarefas de aplicativos estarão disponíveis aqui.")
    return MENU

async def menu_sacar_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia o fluxo de saque, verificando o saldo e solicitando a chave PIX."""
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if not user_data:
        await update.message.reply_text("Seu perfil não foi encontrado. Por favor, inicie o cadastro novamente com /start.")
        return ConversationHandler.END
        
    saldo_float = user_data[5]
    saldo = f"R$ {saldo_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    if saldo_float < 20.0: # Valor mínimo de saque (exemplo)
        await update.message.reply_html(
            f"Seu saldo atual é de <b>{saldo}</b>.\n\n"
            "O valor mínimo para saque é de <b>R$ 20,00</b>. Continue lucrando para atingir o valor!"
        )
        return MENU
        
    # Se tiver saldo suficiente, pede a chave PIX
    await update.message.reply_html(
        f"Seu saldo atual é de <b>{saldo}</b>. Você pode sacar!\n\n"
        "Para prosseguir, por favor, digite sua **chave PIX** (pode ser CPF, Email, Telefone ou Chave Aleatória)."
    )
    return RECEBER_PIX

async def receber_chave_pix(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recebe a chave PIX e finaliza o fluxo de saque."""
    chave_pix = update.message.text
    user_id = update.effective_user.id
    
    # Salva a chave PIX no banco de dados
    update_user_pix(user_id, chave_pix)
    
    # Simulação de solicitação de saque
    await update.message.reply_html(
        f"✅ **Chave PIX ({chave_pix}) salva com sucesso!**\n\n"
        "Sua solicitação de saque foi enviada para análise. O pagamento será processado em até 24 horas úteis."
    )
    
    return MENU

async def menu_perfil(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exibe os dados cadastrais do usuário."""
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if not user_data:
        await update.message.reply_text("Seu perfil não foi encontrado. Por favor, inicie o cadastro novamente com /start.")
        return ConversationHandler.END
        
    # user_data: (user_id, nome, data_nascimento, cidade, email, saldo, indicador_id)
    nome = user_data[1]
    data_nascimento = user_data[2] if user_data[2] else "Não informado"
    cidade = user_data[3] if user_data[3] else "Não informado"
    email = user_data[4]
    saldo_float = user_data[5]
    saldo = f"R$ {saldo_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    texto_perfil = (
        f"👤 <b>Seu Perfil</b>\n\n"
        f"<b>Nome:</b> {nome}\n"
        f"<b>Nascimento:</b> {data_nascimento}\n"
        f"<b>Cidade:</b> {cidade}\n"
        f"<b>Email:</b> {email}\n\n"
        f"<b>Saldo Atual:</b> {saldo}\n\n"
        "Em breve, você poderá editar seus dados aqui."
    )
    
    await update.message.reply_html(texto_perfil)
    return MENU

async def menu_principal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exibe o menu principal do bot."""
    # Busca o saldo do contexto (preenchido na função start ou após o cadastro)
    saldo_float = context.user_data.get("saldo", 0.0)
    # Formatação para moeda brasileira
    saldo = f"R$ {saldo_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    nome = context.user_data.get("nome", update.effective_user.first_name)
    
    menu_keyboard = [
        ["🎬 Ganhe assistindo a vídeos", "📝 Ganhe respondendo pesquisas"],
        ["📱 Ganhe testando aplicativos", "🔗 Indique e Ganhe"],
        ["💰 Sacar Saldo", "👤 Meu Perfil"],
    ]
    
    await update.message.reply_html(
        f"<b>Painel de Controle de {nome}</b>\n\n"
        f"<b>Saldo Atual:</b> {saldo}\n\n"
        "Selecione uma opção abaixo para começar a lucrar:",
        reply_markup=ReplyKeyboardMarkup(
            menu_keyboard, resize_keyboard=True, one_time_keyboard=False
        ),
    )
    return MENU

async def navegar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Lida com a navegação do menu principal."""
    texto = update.message.text
    
    if texto == "💰 Sacar Saldo":
        return await menu_sacar_saldo(update, context)
    elif texto == "👤 Meu Perfil":
        return await menu_perfil(update, context)
    elif texto == "🎬 Ganhe assistindo a vídeos":
        return await menu_videos(update, context)
    elif texto == "⬅️ Voltar ao Menu Principal":
        return await menu_principal(update, context)
    elif texto == "📝 Ganhe respondendo pesquisas":
        return await menu_pesquisas(update, context)
    elif texto == "📱 Ganhe testando aplicativos":
        return await menu_apps(update, context)
    elif texto == "🔗 Indique e Ganhe":
        await update.message.reply_text("Em breve, você poderá gerar seu link de indicação e começar a ganhar com seus amigos!")
    else:
        await update.message.reply_text(f"Opção '{texto}' não reconhecida. Por favor, selecione uma opção do menu.")
    
    return MENU

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela o processo de cadastro."""
    logger.info("Usuário cancelou a conversa.")
    await update.message.reply_text(
        "Cadastro cancelado. Se mudar de ideia, é só digitar /start quando quiser.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

# =================================================================================
# |||||||||||||||||||||||||||| FUNÇÃO PRINCIPAL (MAIN) ||||||||||||||||||||||||||
# =================================================================================

# =================================================================================
# |||||||||||||||||||||||||||| FUNÇÃO ANTI-SONECA ||||||||||||||||||||||||||||||
# =================================================================================

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive and well!")

def keep_alive_server():
    """Inicia um servidor HTTP simples para responder ao Health Check do Render."""
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("", port), HealthCheckHandler)
    logger.info(f"Servidor de Health Check iniciado na porta {port}")
    server.serve_forever()

def main() -> None:
    """Função principal que configura e inicia o bot."""
    
    # Inicializa o banco de dados antes de iniciar o bot
    init_db()
    
    import os
    
    # Inicia o servidor de Health Check em uma thread separada
    threading.Thread(target=keep_alive_server, daemon=True).start()
    
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("O token do bot não foi encontrado na variável de ambiente TELEGRAM_BOT_TOKEN.")
        return
    
    application = Application.builder().token(TOKEN).build()
    logger.info("Bot iniciado com sucesso!")

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            INICIO: [MessageHandler(filters.Regex("^(🚀 Sim, vamos começar!)$"), iniciar_cadastro)],
            NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(🚀 Sim, vamos começar!)$"), receber_nome)],
            DATA_NASCIMENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data_nascimento)],
            CIDADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_cidade)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_email)],
            CONFIRMACAO: [MessageHandler(filters.Regex("^(Sim, está tudo certo!|Não, quero corrigir)$"), receber_confirmacao)],
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, navegar_menu)],
            SACAR_SALDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_sacar_saldo)], # Não é usado, mas mantido para o fluxo
            RECEBER_PIX: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_chave_pix)],
            # Handler para o fluxo de vídeos
            'VIDEOS': [MessageHandler(filters.Regex("^(🎥 Vídeo 1 \\(R\\$ 0\\.50\\)|🎥 Vídeo 2 \\(R\\$ 0\\.75\\)|🎥 Vídeo 3 \\(R\\$ 1\\.00\\)|⬅️ Voltar ao Menu Principal)$"), assistir_video)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
