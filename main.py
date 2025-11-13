# =================================================================================
# ||||||||||||||||||||||||||| PROJETO LUCRAÍ ||||||||||||||||||||||||||||||||||||
# =================================================================================
# Arquivo: main.py
# Descrição: Código principal do bot do Telegram para o projeto Lucraí.
# Versão: 1.6 (Correção Final do Fluxo de Cadastro)
# =================================================================================

import logging
import sqlite3
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
INICIO, NOME, DATA_NASCIMENTO, CIDADE, EMAIL, CONFIRMACAO, MENU = range(7)

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
            indicador_id INTEGER
        )
        """
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
    await update.message.reply_text("Você está na seção de Vídeos. Em breve, as tarefas de vídeos estarão disponíveis aqui.")
    return MENU

async def menu_pesquisas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exibe o menu de tarefas de pesquisas."""
    await update.message.reply_text("Você está na seção de Pesquisas. Em breve, as tarefas de pesquisas estarão disponíveis aqui.")
    return MENU

async def menu_apps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exibe o menu de tarefas de aplicativos."""
    await update.message.reply_text("Você está na seção de Aplicativos. Em breve, as tarefas de aplicativos estarão disponíveis aqui.")
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
        await update.message.reply_text("Aqui você poderá solicitar o saque do seu saldo. Por favor, cadastre sua chave PIX para continuar.")
    elif texto == "👤 Meu Perfil":
        return await menu_perfil(update, context)
    elif texto == "🎬 Ganhe assistindo a vídeos":
        return await menu_videos(update, context)
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

def main() -> None:
    """Função principal que configura e inicia o bot."""
    
    # Inicializa o banco de dados antes de iniciar o bot
    init_db()
    
    import os
    
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
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
