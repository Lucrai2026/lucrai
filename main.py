#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PlayLucro Bot - Sistema Completo de Monetização de Vídeos
Bot Telegram para ganhar dinheiro assistindo vídeos
Versão: 2.0 (Sistema Completo)
"""

import os
import sqlite3
import logging
import uuid
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters, ContextTypes

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token do bot
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8403406649:AAHbopbUcKYTSHXjdS3LX3gvkKMBe560s8o')

# Banco de dados
DB_FILE = 'lucrai_db.sqlite'

# Estados da conversa
NOME, CIDADE, IDADE, CONFIRMACAO, PIX_SAQUE, ALTERAR_CAMPO = range(6)
ESTADO_MENU = 10

# ============================================================================
# BANCO DE DADOS
# ============================================================================

def criar_tabelas():
    """Cria as tabelas do banco de dados."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
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
    ''')
    
    # Tabela de vídeos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            url TEXT NOT NULL,
            valor REAL NOT NULL,
            duracao INTEGER,
            fonte TEXT DEFAULT 'teste',
            data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo BOOLEAN DEFAULT 1
        )
    ''')
    
    # Tabela de visualizações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visualizacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            video_id INTEGER NOT NULL,
            data_visualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'completo',
            valor_ganho REAL,
            FOREIGN KEY (user_id) REFERENCES usuarios(user_id),
            FOREIGN KEY (video_id) REFERENCES videos(id)
        )
    ''')
    
    # Tabela de transações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tipo TEXT,
            valor REAL NOT NULL,
            descricao TEXT,
            data_transacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES usuarios(user_id)
        )
    ''')
    
    # Tabela de saques
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saques (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            valor REAL NOT NULL,
            pix TEXT,
            status TEXT DEFAULT 'pendente',
            data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_pagamento TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES usuarios(user_id)
        )
    ''')
    
    # Inserir vídeos de teste
    cursor.execute('SELECT COUNT(*) FROM videos')
    if cursor.fetchone()[0] == 0:
        videos_teste = [
            ('Vídeo 01 - Ganhe Dinheiro', 'https://example.com/video1.mp4', 0.55, 60),
            ('Vídeo 02 - Assista e Lucre', 'https://example.com/video2.mp4', 0.45, 45),
            ('Vídeo 03 - Renda Extra', 'https://example.com/video3.mp4', 0.30, 30),
            ('Vídeo 04 - PlayLucro', 'https://example.com/video4.mp4', 0.75, 90),
            ('Vídeo 05 - Monetização', 'https://example.com/video5.mp4', 0.50, 50),
        ]
        cursor.executemany(
            'INSERT INTO videos (titulo, url, valor, duracao) VALUES (?, ?, ?, ?)',
            videos_teste
        )
    
    conn.commit()
    conn.close()

def usuario_existe(user_id: int) -> bool:
    """Verifica se o usuário existe."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM usuarios WHERE user_id = ?', (user_id,))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe

def obter_usuario(user_id: int) -> dict:
    """Obtém dados do usuário."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, nome, cidade, idade, saldo, pix, afiliado_de, link_afiliado
        FROM usuarios WHERE user_id = ?
    ''', (user_id,))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return {
            'user_id': resultado[0],
            'nome': resultado[1],
            'cidade': resultado[2],
            'idade': resultado[3],
            'saldo': resultado[4],
            'pix': resultado[5],
            'afiliado_de': resultado[6],
            'link_afiliado': resultado[7]
        }
    return None

def atualizar_saldo(user_id: int, valor: float, tipo: str = 'ganho', descricao: str = ''):
    """Atualiza o saldo do usuário."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Atualizar saldo
    cursor.execute('UPDATE usuarios SET saldo = saldo + ? WHERE user_id = ?', (valor, user_id))
    
    # Registrar transação
    cursor.execute('''
        INSERT INTO transacoes (user_id, tipo, valor, descricao)
        VALUES (?, ?, ?, ?)
    ''', (user_id, tipo, valor, descricao))
    
    conn.commit()
    conn.close()

def obter_videos() -> list:
    """Obtém lista de vídeos disponíveis."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, titulo, valor, duracao FROM videos WHERE ativo = 1')
    videos = cursor.fetchall()
    conn.close()
    return videos

def registrar_visualizacao(user_id: int, video_id: int, valor: float):
    """Registra uma visualização de vídeo."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Registrar visualização
    cursor.execute('''
        INSERT INTO visualizacoes (user_id, video_id, status, valor_ganho)
        VALUES (?, ?, 'completo', ?)
    ''', (user_id, video_id, valor))
    
    # Atualizar saldo
    atualizar_saldo(user_id, valor, 'ganho', f'Vídeo assistido #{video_id}')
    
    # Se tem afiliado, dar comissão
    usuario = obter_usuario(user_id)
    if usuario and usuario['afiliado_de']:
        comissao = valor * 0.10  # 10% para afiliado
        atualizar_saldo(usuario['afiliado_de'], comissao, 'comissao', f'Comissão de afiliado - Usuário {user_id}')
    
    conn.commit()
    conn.close()

def obter_historico(user_id: int, limite: int = 10) -> list:
    """Obtém histórico de vídeos assistidos."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.titulo, vis.data_visualizacao, vis.status, vis.valor_ganho
        FROM visualizacoes vis
        JOIN videos v ON vis.video_id = v.id
        WHERE vis.user_id = ?
        ORDER BY vis.data_visualizacao DESC
        LIMIT ?
    ''', (user_id, limite))
    historico = cursor.fetchall()
    conn.close()
    return historico

def contar_indicados(user_id: int) -> int:
    """Conta quantos usuários foram indicados."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE afiliado_de = ?', (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def obter_comissoes(user_id: int) -> float:
    """Obtém total de comissões ganhas."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT SUM(valor) FROM transacoes
        WHERE user_id = ? AND tipo = 'comissao'
    ''', (user_id,))
    resultado = cursor.fetchone()[0]
    conn.close()
    return resultado or 0.0

def atualizar_usuario(user_id: int, **kwargs):
    """Atualiza dados do usuário."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    campos = []
    valores = []
    
    for chave, valor in kwargs.items():
        campos.append(f'{chave} = ?')
        valores.append(valor)
    
    valores.append(user_id)
    
    query = f'UPDATE usuarios SET {", ".join(campos)} WHERE user_id = ?'
    cursor.execute(query, valores)
    
    conn.commit()
    conn.close()

def solicitar_saque(user_id: int, valor: float, pix: str):
    """Cria uma solicitação de saque."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Registrar saque
    cursor.execute('''
        INSERT INTO saques (user_id, valor, pix, status)
        VALUES (?, ?, ?, 'pendente')
    ''', (user_id, valor, pix))
    
    # Reduzir saldo
    cursor.execute('UPDATE usuarios SET saldo = saldo - ? WHERE user_id = ?', (valor, user_id))
    
    # Registrar transação
    cursor.execute('''
        INSERT INTO transacoes (user_id, tipo, valor, descricao)
        VALUES (?, ?, ?, ?)
    ''', (user_id, 'saque', -valor, f'Saque solicitado - PIX: {pix}'))
    
    conn.commit()
    conn.close()

# ============================================================================
# HANDLERS
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /start."""
    user_id = update.effective_user.id
    
    # Verificar se vem de link de afiliado
    if context.args and context.args[0].startswith('ref_'):
        try:
            afiliado_id = int(context.args[0].split('_')[1])
            context.user_data['afiliado_de'] = afiliado_id
        except (ValueError, IndexError):
            pass
    
    if usuario_existe(user_id):
        await menu_principal(update, context)
    else:
        texto = '''🎬 <b>Seja bem-vindo ao PlayLucro!</b> 🚀

PlayLucro é a sua plataforma de renda extra no Telegram.
<b>Clicou, Assistiu e Lucrou!</b> 💰

📖 <b>Como funciona?</b>
Você realiza tarefas simples: assistir vídeos que o PlayLucro disponibiliza para você.

🎯 <b>Veja como é simples:</b>

1️⃣ Empresas de publicidade nos enviam vídeos
2️⃣ Nós disponibilizamos para você assistir
3️⃣ A empresa nos paga pela visualização
4️⃣ Você recebe sua parte aqui no PlayLucro! 💵

🔥 <b>Chega de enganações na internet!</b>
Vamos com tudo no PlayLucro - Deu Play, Lucrou! 🎮💸

Proto para começar essa jornada de renda extra incrível?'''
        
        keyboard = [[InlineKeyboardButton("🚀 Clique aqui para Cadastrar", callback_data='cadastrar')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            texto,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

async def cadastrar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o processo de cadastro."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text='Ótimo! 🎉\n\nVamos começar seu cadastro!\n\nQual é o seu <b>nome</b>?',
        parse_mode='HTML'
    )
    
    return NOME

async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe o nome do usuário."""
    context.user_data['nome'] = update.message.text
    
    await update.message.reply_text(
        f'Prazer, {context.user_data["nome"]}! 😊\n\nQual é a sua <b>cidade</b>?',
        parse_mode='HTML'
    )
    
    return CIDADE

async def receber_cidade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe a cidade do usuário."""
    context.user_data['cidade'] = update.message.text
    
    await update.message.reply_text(
        f'Ótimo! Você é de {context.user_data["cidade"]}! 🏙️\n\nQuantos <b>anos</b> você tem?',
        parse_mode='HTML'
    )
    
    return IDADE

async def receber_idade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe a idade do usuário."""
    try:
        idade = int(update.message.text)
        context.user_data['idade'] = idade
        
        texto = f'''📋 <b>Resumo do seu cadastro:</b>

👤 <b>Nome:</b> {context.user_data['nome']}
🏙️ <b>Cidade:</b> {context.user_data['cidade']}
🎂 <b>Idade:</b> {context.user_data['idade']} anos

Está tudo correto?'''
        
        keyboard = [
            [InlineKeyboardButton('✅ Sim, está correto!', callback_data='confirmar_cadastro')],
            [InlineKeyboardButton('❌ Não, quero corrigir', callback_data='cancelar_cadastro')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(texto, reply_markup=reply_markup, parse_mode='HTML')
        
        return CONFIRMACAO
    
    except ValueError:
        await update.message.reply_text('Por favor, digite um número válido para a idade.')
        return IDADE

async def confirmar_cadastro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirma o cadastro do usuário."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    link_afiliado = f'https://t.me/playlucro_bot?start=ref_{user_id}'
    afiliado_de = context.user_data.get('afiliado_de')
    
    # Salvar no banco de dados
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usuarios (user_id, nome, cidade, idade, saldo, link_afiliado, afiliado_de)
        VALUES (?, ?, ?, ?, 0.0, ?, ?)
    ''', (user_id, context.user_data['nome'], context.user_data['cidade'], context.user_data['idade'], link_afiliado, afiliado_de))
    conn.commit()
    conn.close()
    
    await query.edit_message_text(
        text='''🎉 <b>Parabéns! Seu cadastro foi realizado com sucesso!</b>

Bem-vindo ao PlayLucro! 🚀

Em breve você poderá começar a ganhar dinheiro assistindo vídeos! 💵

👤 <b>PAINEL DO USUÁRIO</b>

👤 <b>Usuário:</b> ''' + context.user_data['nome'] + '''
💰 <b>Saldo:</b> R$ 0,00

O que você quer fazer?''',
        parse_mode='HTML',
        reply_markup=get_menu_keyboard()
    )
    
    return ConversationHandler.END

async def cancelar_cadastro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela o cadastro."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(text='Cadastro cancelado. Digite /start para começar novamente.')
    
    return ConversationHandler.END

async def menu_principal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra o menu principal."""
    user_id = update.effective_user.id
    usuario = obter_usuario(user_id)
    
    if not usuario:
        await update.message.reply_text('Usuário não encontrado. Digite /start para cadastrar.')
        return
    
    texto = f'''👤 <b>PAINEL DO USUÁRIO</b>

👤 <b>Usuário:</b> {usuario['nome']}
💰 <b>Saldo:</b> R$ {usuario['saldo']:.2f}

O que você quer fazer?'''
    
    await update.message.reply_text(
        texto,
        reply_markup=get_menu_keyboard(),
        parse_mode='HTML'
    )

def get_menu_keyboard():
    """Retorna o teclado do menu principal."""
    keyboard = [
        [
            InlineKeyboardButton('🎬 Assistir Vídeos', callback_data='videos'),
            InlineKeyboardButton('🔗 Indique e Ganhe', callback_data='afiliado')
        ],
        [
            InlineKeyboardButton('💸 Sacar Saldo', callback_data='saque'),
            InlineKeyboardButton('📊 Histórico', callback_data='historico')
        ],
        [
            InlineKeyboardButton('⚙️ Configurações', callback_data='config'),
            InlineKeyboardButton('💬 Suporte', callback_data='suporte')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para callbacks dos botões."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    usuario = obter_usuario(user_id)
    
    if query.data == 'videos':
        await mostrar_videos(query, usuario)
    elif query.data == 'saque':
        await mostrar_saque(query, usuario)
    elif query.data == 'afiliado':
        await mostrar_afiliado(query, usuario)
    elif query.data == 'historico':
        await mostrar_historico(query, usuario)
    elif query.data == 'config':
        await mostrar_config(query, usuario)
    elif query.data == 'suporte':
        await mostrar_suporte(query, usuario)
    elif query.data == 'menu':
        await menu_principal(query, context)
    elif query.data.startswith('video_'):
        video_id = int(query.data.split('_')[1])
        await assistir_video(query, usuario, video_id)
    elif query.data == 'solicitar_saque':
        await solicitar_saque_callback(query, usuario, context)
    elif query.data == 'cadastrar_pix':
        context.user_data['modo'] = 'cadastrar_pix'
        await query.edit_message_text(
            text='📱 <b>Cadastrar PIX</b>\n\nQual é sua chave PIX? (CPF, Email, Telefone ou Chave Aleatória)',
            parse_mode='HTML'
        )
    elif query.data == 'alterar_pix':
        context.user_data['modo'] = 'alterar_pix'
        await query.edit_message_text(
            text='📱 <b>Alterar PIX</b>\n\nQual é sua nova chave PIX?',
            parse_mode='HTML'
        )
    elif query.data == 'alt_nome':
        context.user_data['modo'] = 'alterar_nome'
        await query.edit_message_text(
            text='👤 <b>Alterar Nome</b>\n\nQual é seu novo nome?',
            parse_mode='HTML'
        )
    elif query.data == 'alt_cidade':
        context.user_data['modo'] = 'alterar_cidade'
        await query.edit_message_text(
            text='🏙️ <b>Alterar Cidade</b>\n\nQual é sua nova cidade?',
            parse_mode='HTML'
        )
    elif query.data == 'alt_idade':
        context.user_data['modo'] = 'alterar_idade'
        await query.edit_message_text(
            text='🎂 <b>Alterar Idade</b>\n\nQual é sua nova idade?',
            parse_mode='HTML'
        )

async def mostrar_videos(query, usuario):
    """Mostra lista de vídeos disponíveis."""
    videos = obter_videos()
    
    if not videos:
        await query.edit_message_text('Nenhum vídeo disponível no momento.')
        return
    
    texto = '🎬 <b>VÍDEOS DISPONÍVEIS</b>\n\n'
    
    for video in videos:
        video_id, titulo, valor, duracao = video
        texto += f'📹 <b>{titulo}</b>\n'
        texto += f'   Assista por completo e ganhe R$ {valor:.2f}\n'
        texto += f'   ⏱️ Duração: {duracao}s\n\n'
    
    keyboard = []
    for video in videos:
        video_id, titulo, valor, duracao = video
        keyboard.append([InlineKeyboardButton(f'▶️ {titulo}', callback_data=f'video_{video_id}')])
    
    keyboard.append([InlineKeyboardButton('◀️ Voltar ao Menu', callback_data='menu')])
    
    await query.edit_message_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def assistir_video(query, usuario, video_id):
    """Processa a assistência de um vídeo."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT titulo, url, valor FROM videos WHERE id = ?', (video_id,))
    video = cursor.fetchone()
    conn.close()
    
    if not video:
        await query.edit_message_text('Vídeo não encontrado.')
        return
    
    titulo, url, valor = video
    
    # Registrar visualização
    registrar_visualizacao(usuario['user_id'], video_id, valor)
    
    # Atualizar saldo do usuário
    usuario_atualizado = obter_usuario(usuario['user_id'])
    
    texto = f'''✅ <b>Vídeo Assistido com Sucesso!</b>

📹 <b>{titulo}</b>
💰 <b>Você ganhou: R$ {valor:.2f}</b>

💵 <b>Seu novo saldo:</b> R$ {usuario_atualizado['saldo']:.2f}

Parabéns! Continue assistindo para ganhar mais! 🎉'''
    
    keyboard = [[InlineKeyboardButton('🎬 Voltar aos Vídeos', callback_data='videos')]]
    
    await query.edit_message_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def mostrar_saque(query, usuario):
    """Mostra opções de saque."""
    texto = f'''💸 <b>SACAR SALDO</b>

💰 <b>Seu saldo atual:</b> R$ {usuario['saldo']:.2f}
💵 <b>Saldo mínimo para sacar:</b> R$ 20,00

'''
    
    if usuario['saldo'] >= 20.00:
        if usuario['pix']:
            texto += f'''✅ <b>Sua chave PIX:</b> {usuario['pix']}

Clique em "Solicitar Saque" para processar o pagamento.
Nossa equipe validará e você receberá em breve!'''
            keyboard = [
                [InlineKeyboardButton('✅ Solicitar Saque', callback_data='solicitar_saque')],
                [InlineKeyboardButton('🔄 Alterar PIX', callback_data='alterar_pix')],
                [InlineKeyboardButton('◀️ Voltar ao Menu', callback_data='menu')]
            ]
        else:
            texto += '''Você ainda não cadastrou sua chave PIX.
Clique em "Cadastrar PIX" para continuar.'''
            keyboard = [
                [InlineKeyboardButton('📝 Cadastrar PIX', callback_data='cadastrar_pix')],
                [InlineKeyboardButton('◀️ Voltar ao Menu', callback_data='menu')]
            ]
    else:
        falta = 20.00 - usuario['saldo']
        texto += f'''❌ Você ainda não atingiu o saldo mínimo.
Faltam R$ {falta:.2f} para poder sacar.

Continue assistindo vídeos para ganhar mais! 💪'''
        keyboard = [[InlineKeyboardButton('◀️ Voltar ao Menu', callback_data='menu')]]
    
    await query.edit_message_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def solicitar_saque_callback(query, usuario, context):
    """Processa solicitação de saque."""
    if not usuario['pix']:
        await query.edit_message_text('Você precisa cadastrar uma chave PIX primeiro.')
        return
    
    if usuario['saldo'] < 20.00:
        await query.edit_message_text('Seu saldo é insuficiente para sacar.')
        return
    
    # Registrar saque
    solicitar_saque(usuario['user_id'], usuario['saldo'], usuario['pix'])
    
    texto = f'''✅ <b>Saque Solicitado com Sucesso!</b>

💰 <b>Valor:</b> R$ {usuario['saldo']:.2f}
📱 <b>PIX:</b> {usuario['pix']}

Nossa equipe irá validar seu saque e você receberá em breve!

Obrigado por usar o PlayLucro! 🎉'''
    
    keyboard = [[InlineKeyboardButton('◀️ Voltar ao Menu', callback_data='menu')]]
    
    await query.edit_message_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def mostrar_afiliado(query, usuario):
    """Mostra programa de afiliados."""
    link_afiliado = usuario['link_afiliado']
    indicados = contar_indicados(usuario['user_id'])
    comissoes = obter_comissoes(usuario['user_id'])
    
    # Mostrar imagem do banner
    try:
        with open('banner_afiliado.png', 'rb') as banner_file:
            await query.message.reply_photo(
                photo=banner_file,
                caption='🔗 <b>INDIQUE E GANHE</b>',
                parse_mode='HTML'
            )
    except FileNotFoundError:
        logger.warning('⚠️ Banner de afiliado não encontrado!')
    
    texto = f'''🔗 <b>INDIQUE E GANHE</b>

Compartilhe seu link único e ganhe 10% de tudo que seus indicados fizerem!

🔗 <b>Seu link de indicação:</b>
<code>{link_afiliado}</code>

📊 <b>Seus indicados:</b> {indicados}
💵 <b>Comissões ganhas:</b> R$ {comissoes:.2f}

💡 <b>Como funciona:</b>
• Você compartilha seu link
• Seus amigos clicam e se cadastram
• Para cada vídeo que eles assistem, você ganha 10%
• Sua % pode aumentar de acordo com seu desempenho como afiliado

💰 <b>Repartição com afiliado:</b>
• 10% para você (afiliado)
• 25% para PlayLucro
• 65% para quem assiste o vídeo

Comece a indicar e ganhe mais! 🚀'''
    
    keyboard = [[InlineKeyboardButton('◀️ Voltar ao Menu', callback_data='menu')]]
    
    await query.message.reply_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def mostrar_historico(query, usuario):
    """Mostra histórico de vídeos."""
    historico = obter_historico(usuario['user_id'], 10)
    
    if not historico:
        texto = '📊 <b>HISTÓRICO</b>\n\nVocê ainda não assistiu a nenhum vídeo.'
    else:
        texto = '📊 <b>HISTÓRICO DE VÍDEOS</b>\n\n'
        
        for titulo, data, status, valor_ganho in historico:
            status_emoji = '✅' if status == 'completo' else '❌'
            valor_texto = f'R$ {valor_ganho:.2f}' if valor_ganho else 'Não recebido'
            
            # Formatar data
            data_obj = datetime.fromisoformat(data)
            data_formatada = data_obj.strftime('%d/%m/%Y %H:%M')
            
            texto += f'{status_emoji} <b>{titulo}</b>\n'
            texto += f'   {data_formatada} - {valor_texto}\n\n'
    
    keyboard = [[InlineKeyboardButton('◀️ Voltar ao Menu', callback_data='menu')]]
    
    await query.edit_message_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def mostrar_config(query, usuario):
    """Mostra opções de configuração."""
    texto = f'''⚙️ <b>CONFIGURAÇÕES</b>

👤 <b>Nome:</b> {usuario['nome']}
🏙️ <b>Cidade:</b> {usuario['cidade']}
🎂 <b>Idade:</b> {usuario['idade']} anos
📱 <b>PIX:</b> {usuario['pix'] if usuario['pix'] else 'Não cadastrado'}

O que você quer alterar?'''
    
    keyboard = [
        [InlineKeyboardButton('👤 Alterar Nome', callback_data='alt_nome')],
        [InlineKeyboardButton('🏙️ Alterar Cidade', callback_data='alt_cidade')],
        [InlineKeyboardButton('🎂 Alterar Idade', callback_data='alt_idade')],
        [InlineKeyboardButton('📱 Alterar PIX', callback_data='alterar_pix')],
        [InlineKeyboardButton('◀️ Voltar ao Menu', callback_data='menu')]
    ]
    
    await query.edit_message_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def mostrar_suporte(query, usuario):
    """Mostra informações de suporte."""
    texto = '''💬 <b>SUPORTE</b>

Tem dúvidas ou precisa de ajuda?

Clique no botão abaixo para ir ao nosso grupo de suporte:'''
    
    keyboard = [
        [InlineKeyboardButton('💬 Ir para Suporte', url='https://t.me/playlucro_suporte')],
        [InlineKeyboardButton('◀️ Voltar ao Menu', callback_data='menu')]
    ]
    
    await query.edit_message_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def receber_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para receber texto (PIX, Nome, Cidade, Idade)."""
    user_id = update.effective_user.id
    texto = update.message.text
    modo = context.user_data.get('modo')
    
    if modo == 'cadastrar_pix':
        atualizar_usuario(user_id, pix=texto)
        await update.message.reply_text(
            f'✅ PIX cadastrado com sucesso!\n\nSua chave: {texto}',
            parse_mode='HTML'
        )
        context.user_data['modo'] = None
        usuario = obter_usuario(user_id)
        await mostrar_saque(update.message, usuario)
    
    elif modo == 'alterar_pix':
        atualizar_usuario(user_id, pix=texto)
        await update.message.reply_text(
            f'✅ PIX alterado com sucesso!\n\nSua nova chave: {texto}',
            parse_mode='HTML'
        )
        context.user_data['modo'] = None
        usuario = obter_usuario(user_id)
        await mostrar_saque(update.message, usuario)
    
    elif modo == 'alterar_nome':
        atualizar_usuario(user_id, nome=texto)
        await update.message.reply_text(
            f'✅ Nome alterado com sucesso!\n\nSeu novo nome: {texto}',
            parse_mode='HTML'
        )
        context.user_data['modo'] = None
        usuario = obter_usuario(user_id)
        await mostrar_config(update.message, usuario)
    
    elif modo == 'alterar_cidade':
        atualizar_usuario(user_id, cidade=texto)
        await update.message.reply_text(
            f'✅ Cidade alterada com sucesso!\n\nSua nova cidade: {texto}',
            parse_mode='HTML'
        )
        context.user_data['modo'] = None
        usuario = obter_usuario(user_id)
        await mostrar_config(update.message, usuario)
    
    elif modo == 'alterar_idade':
        try:
            idade = int(texto)
            atualizar_usuario(user_id, idade=idade)
            await update.message.reply_text(
                f'✅ Idade alterada com sucesso!\n\nSua nova idade: {idade}',
                parse_mode='HTML'
            )
            context.user_data['modo'] = None
            usuario = obter_usuario(user_id)
            await mostrar_config(update.message, usuario)
        except ValueError:
            await update.message.reply_text('Por favor, digite um número válido.')

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /menu."""
    await menu_principal(update, context)

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Função principal."""
    # Criar tabelas
    criar_tabelas()
    
    # Criar aplicação
    app = Application.builder().token(TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('menu', menu_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_texto))
    
    # Conversation handler para cadastro
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(cadastrar_callback, pattern='cadastrar')],
        states={
            NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_nome)],
            CIDADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_cidade)],
            IDADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_idade)],
            CONFIRMACAO: [
                CallbackQueryHandler(confirmar_cadastro, pattern='confirmar_cadastro'),
                CallbackQueryHandler(cancelar_cadastro, pattern='cancelar_cadastro')
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    
    app.add_handler(conv_handler)
    
    # Iniciar bot
    logger.info('✅ Bot iniciado com sucesso!')
    app.run_polling()

if __name__ == '__main__':
    main()
