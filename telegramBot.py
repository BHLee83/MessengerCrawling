from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from config import Config

import os
import logging
import crawler
import nest_asyncio
nest_asyncio.apply()



# 로깅 설정
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 봇 토큰 설정
TOKEN = Config.TOKEN

# 대화방 ID 설정
ALLOWED_CHAT_ID = Config.chatID

# 최대 메시지 길이 제한
MAX_LENGTH = Config.MAX_LENGTH

# 프록시 설정
if Config.USE_PROXY:
    os.environ['HTTP_PROXY'] = Config.HTTP_PROXY
    os.environ['HTTPS_PROXY'] = Config.HTTPS_PROXY


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """채팅 시작 시 호출됩니다."""
    chat_id = update.message.chat_id
    if chat_id == ALLOWED_CHAT_ID:
        await update.message.reply_text('/(slash)와 함께 검색을 원하는 내용을 입력해주세요. ex) /23-11')


async def proc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """봇이 메시지를 전송합니다."""
    chat_id = update.message.chat_id
    if chat_id == ALLOWED_CHAT_ID:
        text = update.message.text
        if text.startswith('/'):
            text = text.removeprefix('/').strip()
            ret = crawler.search(text)  # 메신저 내용 가져오기
            if ret.empty:
                await update.message.reply_text(f'{text}이(가) 포함된 내용이 없습니다')
            else:
                msg = "\n".join(ret['Original'])
                # 메시지 길이가 최대 길이를 초과하는지 확인
                if len(msg) > MAX_LENGTH:
                    # 메시지를 허용된 길이만큼 잘라서 보냄
                    message_to_send = msg[-MAX_LENGTH:]
                else:
                    # 메시지 길이가 허용 범위 내이면 그대로 전송
                    message_to_send = msg
                await update.message.reply_text(f'{message_to_send}')
            


def main() -> None:
    """봇을 생성하고 명령을 처리하는 메인 함수입니다."""
    # 애플리케이션 인스턴스 생성
    application = Application.builder().token(TOKEN).build()
    
    # 시작 명령 처리 핸들러
    application.add_handler(CommandHandler("start", start))

    # 텍스트 메시지 처리 핸들러
    application.add_handler(MessageHandler(filters.TEXT, proc))

    # 봇을 시작하고 작동시킵니다.
    application.run_polling()