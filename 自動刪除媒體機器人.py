import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 定义机器人令牌
TOKEN = '7720654732:AAGc-CbQhXx73auptB1JbZTjTY7rjFnWfPI'
DEFAULT_DELETE_TIME = 60  # 默认删除时间，单位为秒

# 检查是否是管理员
async def is_admin(update: Update) -> bool:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_member = await update.effective_chat.get_member(user_id)
    return chat_member.status in ['administrator', 'creator']

# 处理启动命令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        reply = await update.message.reply_text("此命令仅管理员可用。")
        await asyncio.sleep(5)  # 5秒后删除
        await update.message.delete()
        await reply.delete()
        return
    
    await update.message.reply_text(
        "你好！使用 /set <秒数> 设置本次删除时间，或直接发送媒体消息，使用默认删除时间。"
    )

# 设置删除时间的命令
async def set_delete_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        reply = await update.message.reply_text("此命令仅管理员可用。")
        await asyncio.sleep(5)  # 5秒后删除
        await update.message.delete()
        await reply.delete()
        return
    
    try:
        delete_time = int(context.args[0])
        context.user_data['delete_time'] = delete_time
        reply = await update.message.reply_text(f"本次删除时间已设置为 {delete_time} 秒。")
    except (IndexError, ValueError):
        reply = await update.message.reply_text("请使用正确的格式: /set <秒数>")
    
    # 自动删除管理员回复的命令（若需要的话）
    await asyncio.sleep(5)
    await reply.delete()

# 处理媒体消息
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = message.chat_id
    message_id = message.message_id

    # 获取用户设置的删除时间，如果没有设置则使用默认删除时间
    delete_time = context.user_data.get('delete_time', DEFAULT_DELETE_TIME)

    # 等待指定的删除时间后直接删除消息
    await asyncio.sleep(delete_time)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"删除消息失败: {e}")

# 设置主要函数来启动机器人
def main():
    # 创建机器人应用
    application = Application.builder().token(TOKEN).build()

    # 添加命令和消息处理
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set", set_delete_time))  # 使用 /set 命令设置删除时间
    application.add_handler(MessageHandler(filters.ATTACHMENT, handle_media))

    # 启动机器人
    application.run_polling()

if __name__ == "__main__":
    main()
