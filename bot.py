import os
import logging

from datetime import datetime
from telegram import Update, Bot
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from telegram.error import TelegramError
from dotenv import load_dotenv

from database import QuoteDatabase
from keyboards import (
    get_main_keyboard, 
    get_categories_keyboard, 
    get_search_options_keyboard,
    get_quote_actions_keyboard,
    get_admin_keyboard
)

from deepseek_generator import deepseek_gen

from database import QuoteDatabase

# Загрузка переменных
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class WisdomBotWithButtons:
    def __init__(self):
        self.token = os.getenv('BOT_TOKEN')
        self.channel_id = os.getenv('CHANNEL_ID')
        self.admin_id = os.getenv('ADMIN_CHAT_ID')
        
        if not self.token:
            raise ValueError("BOT_TOKEN не установлен в .env файле")
        
        # self.bot удален, так как Application создает своего бота
        # self.bot = Bot(token=self.token)
        self.db = QuoteDatabase()
        
        # Состояния пользователей (для поиска)
        self.user_states = {}
    
    # ==================== КОМАНДЫ ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        # Если приватный чат - приветствие + меню
        if update.effective_chat and update.effective_chat.type == 'private':
            user = update.effective_user
            welcome_text = f"""
👋 Привет, {user.first_name if user else 'друг'}!

Я — *Wisdom Daily Bot* 🤖
Я публикую мудрые цитаты великих людей каждые 12 часов.

📌 *Что я умею:*
• Присылать случайные цитаты по запросу
• Искать цитаты по категориям и авторам
• Показывать статистику
• Публиковать в канале @{self.channel_id.replace('@', '')}

🎯 *Используй кнопки ниже или команды:*
/quote - случайная цитата
/categories - выбрать категорию
/search - поиск цитат
/stats - статистика бота
/help - помощь

👇 *Выбирай действие:*"""
            
            await update.message.reply_text(
                welcome_text, 
                parse_mode='Markdown',
                reply_markup=get_main_keyboard()
            )
            
            # И сразу цитату
            await self.handle_random_quote_button(update, context)
            
        else:
            # В группе/канале только цитату
            await self.handle_random_quote_button(update, context)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📖 *Доступные команды:*

*Основные:*
/start - Запустить бота
/quote - Получить случайную цитату
/categories - Выбрать категорию
/search - Поиск цитат
/stats - Статистика бота

*Для админа:*
/admin - Админ-панель
/force_post - Опубликовать сейчас
/add_quote - Добавить цитату

*Управление:*
/cancel - Отменить текущее действие
/settings - Настройки

📱 *Также используйте кнопки меню!*
        """
        await update.message.reply_text(
            help_text, 
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    # ==================== КНОПКА "СЛУЧАЙНАЯ ЦИТАТА" ====================
    
    async def handle_random_quote_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатия кнопки "Случайная цитата" """
        user_id = update.effective_user.id if update.effective_user else 0
        
        # Получаем случайную цитату
        quote = self.db.get_random_quote_for_button()
        
        # Если цитат нет, пробуем сгенерировать через AI
        if not quote:
            await update.message.reply_chat_action('typing')
            # Генерируем новую
            quote = self.db.generate_and_save_ai_quote()
        
        if quote:
            # Форматируем ответ
            response = self.format_quote_response(quote)
            
            # Отправляем с кнопками действий
            await update.message.reply_text(
                response,
                parse_mode='HTML',
                reply_markup=get_quote_actions_keyboard(quote['id'])
            )
            
            # Логируем запрос
            logger.info(f"Пользователь {user_id} запросил случайную цитату: {quote['id']}")
        else:
            await update.message.reply_text(
                "😔 Не удалось найти или сгенерировать цитату. Попробуйте позже!",
                reply_markup=get_main_keyboard()
            )
    
    # ==================== КНОПКА "ПО КАТЕГОРИЯМ" ====================
    
    async def handle_categories_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кнопки "По категориям" """
        categories_text = """
📚 *Выберите категорию:*

Здесь вы можете получить цитаты на определенную тему. 
Категории основаны на тематике высказываний.
        """
        
        await update.message.reply_text(
            categories_text,
            parse_mode='Markdown',
            reply_markup=get_categories_keyboard()
        )
    
    # ==================== КНОПКА "ПОИСК" ====================
    
    async def handle_search_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кнопки "Поиск" """
        search_text = """
🔍 *Поиск цитат:*

Вы можете искать цитаты:
• По имени автора
• По ключевому слову в тексте
• По тегу

Выберите тип поиска:
        """
        
        await update.message.reply_text(
            search_text,
            parse_mode='Markdown',
            reply_markup=get_search_options_keyboard()
        )
        
        # Устанавливаем состояние поиска
        self.user_states[update.effective_user.id] = 'awaiting_search_type'
    
    # ==================== КНОПКА "СТАТИСТИКА" ====================
    
    async def handle_stats_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кнопки "Статистика" """
        stats = self.db.get_daily_stats()
        
        stats_text = f"""
📊 *Статистика бота:*

📈 *Общая:*
• Всего цитат в базе: {stats['total']}
• Доступно сегодня: {stats['available']}

📅 *Сегодня:*
• Опубликовано в канале: {stats['used_today']}
• Ручных запросов: {stats['manual_requests']}

⏰ *Следующая публикация:*
• В канале: 13:00 и 16:00 (МСК)
        """
        
        await update.message.reply_text(
            stats_text,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    # ==================== КНОПКА "ПОМОЩЬ" ====================
    
    async def handle_help_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кнопки "Помощь" """
        await self.help_command(update, context)
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена текущего действия"""
        user_id = update.effective_user.id
        
        if user_id in self.user_states:
            del self.user_states[user_id]
            await update.message.reply_text(
                "✅ Действие отменено",
                reply_markup=get_main_keyboard()
            )
        else:
            await update.message.reply_text(
                "🤔 Нечего отменять",
                reply_markup=get_main_keyboard()
            )
    
    async def favorites_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать избранные цитаты"""
        user_id = update.effective_user.id
        favorites = self.db.get_user_favorites(user_id)
        
        if favorites:
            response = "❤️ <b>Ваши избранные цитаты:</b>\n\n"
            for quote in favorites[:5]:  # Показываем первые 5
                response += f"• {quote['text'][:80]}...\n\n"
            
            if len(favorites) > 5:
                response += f"\n📚 И еще {len(favorites) - 5} цитат..."
        else:
            response = "📭 У вас пока нет избранных цитат"
        
        await update.message.reply_text(
            response,
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
        # ==================== ОБРАБОТЧИКИ INLINE КНОПОК ====================
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий inline кнопок"""
        query = update.callback_query
        await query.answer()  # Убираем "часики"
        
        data = query.data
        user_id = update.effective_user.id
        
        # Обработка категорий
        if data.startswith('cat_'):
            category = data.replace('cat_', '')
            quote = self.db.get_quote_by_category(category)
            
            if quote:
                response = self.format_quote_response(quote, show_category=True)
                await query.edit_message_text(
                    response,
                    parse_mode='HTML',
                    reply_markup=get_quote_actions_keyboard(quote['id'])
                )
            else:
                await query.edit_message_text(
                    f"😔 В категории '{category}' пока нет цитат",
                    reply_markup=get_categories_keyboard()
                )
        
        # Еще одна цитата
        elif data == 'another_quote':
            quote = self.db.get_random_quote_for_button()
            if quote:
                response = self.format_quote_response(quote)
                await query.edit_message_text(
                    response,
                    parse_mode='HTML',
                    reply_markup=get_quote_actions_keyboard(quote['id'])
                )
        
        # Назад в меню
        elif data == 'back_to_main':
            await query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🏠 *Главное меню:*\nВыберите действие:",
                parse_mode='Markdown',
                reply_markup=get_main_keyboard()
            )
        
        # Поиск по автору
        elif data == 'search_author':
            await query.edit_message_text(
                "✍️ *Поиск по автору:*\nВведите имя или фамилию автора:",
                parse_mode='Markdown'
            )
            self.user_states[user_id] = 'searching_author'
        
        # Добавить в избранное
        elif data.startswith('fav_'):
            quote_id = int(data.replace('fav_', ''))
            # Здесь можно добавить логику избранного
            await query.answer("✅ Добавлено в избранное!", show_alert=True)
    
    # ==================== ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ====================
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user_id = update.effective_user.id
        text = update.message.text
        
        # Проверяем состояние пользователя
        if user_id in self.user_states:
            state = self.user_states[user_id]
            
            # Поиск по автору
            if state == 'searching_author':
                quotes = self.db.search_quotes(text, limit=3)
                
                if quotes:
                    response = "🔍 *Найдены цитаты:*\n\n"
                    for quote in quotes:
                        response += f"• {quote['text'][:100]}... — *{quote['author']}*\n\n"
                    
                    response += "\nДля подробного просмотра используйте кнопки ниже."
                    
                    await update.message.reply_text(
                        response,
                        parse_mode='Markdown',
                        reply_markup=get_main_keyboard()
                    )
                else:
                    await update.message.reply_text(
                        f"😔 Цитаты автора '{text}' не найдены",
                        reply_markup=get_main_keyboard()
                    )
                
                # Сбрасываем состояние
                del self.user_states[user_id]
                return
        
        # Обработка текстовых команд (если не кнопка)
        if text == "🎲 Случайная цитата":
            await self.handle_random_quote_button(update, context)
        elif text == "📚 По категориям":
            await self.handle_categories_button(update, context)
        elif text == "🔍 Поиск":
            await self.handle_search_button(update, context)
        elif text == "📊 Статистика":
            await self.handle_stats_button(update, context)
        elif text == "ℹ️ Помощь":
            await self.handle_help_button(update, context)
        elif text == "/quote":
            await self.handle_random_quote_button(update, context)
        elif text == "/categories":
            await self.handle_categories_button(update, context)
        elif text == "/search":
            await self.handle_search_button(update, context)
        elif text == "/stats":
            await self.handle_stats_button(update, context)
        else:
            # Если неизвестная команда
            await update.message.reply_text(
                "🤔 Не понимаю команду. Используйте кнопки меню или /help",
                reply_markup=get_main_keyboard()
            )
    
    # ==================== АДМИН ПАНЕЛЬ ====================
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Админ-панель"""
        if str(update.effective_user.id) != self.admin_id:
            await update.message.reply_text("⛔ У вас нет доступа к админ-панели")
            return
        
        admin_text = """
⚙️ *Админ-панель:*

*Управление ботом:*
• Опубликовать цитату сейчас
• Добавить/удалить цитаты
• Просмотр полной статистики
• Настройки автоматизации

Используйте кнопки ниже:
        """
        
        await update.message.reply_text(
            admin_text,
            parse_mode='Markdown',
            reply_markup=get_admin_keyboard()
        )
    
    async def handle_admin_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка админских кнопок"""
        if str(update.effective_user.id) != self.admin_id:
            return
        
        text = update.message.text
        
        if text == "📤 Опубликовать сейчас":
            success = await self.post_to_channel_manual(context.bot)
            if success:
                await update.message.reply_text(
                    "✅ Цитата опубликована в канале!",
                    reply_markup=get_admin_keyboard()
                )
            else:
                await update.message.reply_text(
                    "❌ Ошибка публикации!",
                    reply_markup=get_admin_keyboard()
                )
        
        elif text == "📥 Добавить цитату":
            await update.message.reply_text(
                "📝 *Добавление цитаты:*\nОтправьте цитату в формате:\n\n"
                "Текст цитаты\n— Автор\n#категория\n\n"
                "Например:\n"
                "Делай что можешь\n— Теодор Рузвельт\n#motivation",
                parse_mode='Markdown'
            )
        
        elif text == "🏠 В главное меню":
            await self.start_command(update, context)
    
    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================
    
    def format_quote_response(self, quote: dict, show_category: bool = False) -> str:
        """Форматирует цитату для отправки"""
        response = f"💬 <b>Цитата #{quote['id']}</b>\n\n"
        response += f"«{quote['text']}»\n\n"
        
        if quote['author']:
            response += f"— <i>{quote['author']}</i>\n\n"
        
        if show_category and quote['category']:
            response += f"🏷️ Категория: <b>{quote['category']}</b>\n"
        
        # Добавляем статистику использования
        if quote.get('used_count', 0) > 0:
            response += f"📊 Использовалась: {quote['used_count']} раз\n"
        
        response += f"\n🆔 ID: {quote['id']}"
        
        return response
    
    async def post_to_channel_manual(self, bot: Bot):
        """Ручная публикация в канал (для админа)"""
        try:
            quote = self.db.get_next_quote_with_ai_fallback()
            if not quote:
                return False
            
            post_text = f"""
💬 <b>Цитата дня</b>

«{quote['text']}»

— <i>{quote['author']}</i>

#{quote['category']} #ЦитатаДня #Мудрость

🕰 {datetime.now().strftime('%H:%M')} | 📅 {datetime.now().strftime('%d.%m.%Y')}
            """.strip()
            
            await bot.send_message(
                chat_id=self.channel_id,
                text=post_text,
                parse_mode='HTML'
            )
            
            logger.info(f"Ручная публикация: {quote['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка ручной публикации: {e}")
            return False
    
    # ==================== ЗАПУСК БОТА ====================
    
    def run_bot(self):
        """Запускает бота с обработчиками"""
        application = Application.builder().token(self.token).build()
        
        # Команды
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("admin", self.admin_command))
        application.add_handler(CommandHandler("quote", self.handle_random_quote_button))
        application.add_handler(CommandHandler("stats", self.handle_stats_button))
        
        # Обработчики кнопок
        application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Обработчики текстовых сообщений
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_message
        ))
        
        # Обработчики админских кнопок
        application.add_handler(MessageHandler(
            filters.Regex(r'^(📤|📥|🗑️|📊|⚙️|🏠)'), 
            self.handle_admin_buttons
        ))
        
        # Настройка планировщика (JobQueue)
        if application.job_queue:
            job_queue = application.job_queue
            
            # Время публикации (МСК) -> UTC
            # 9:00 MSK = 6:00 UTC
            job_queue.run_daily(self.scheduled_post_job, time=datetime.strptime("13:00", "%H:%M").time())
            # 21:00 MSK = 18:00 UTC
            job_queue.run_daily(self.scheduled_post_job, time=datetime.strptime("16:00", "%H:%M").time())
            
            print("⏰ Планировщик настроен (JobQueue)")
        
        # Запуск
        print(f"🚀 Бот запускается...")
        print(f"👤 Админ: {self.admin_id}")
        print(f"📢 Канал: {self.channel_id}")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    # ==================== АВТОМАТИЧЕСКАЯ ПУБЛИКАЦИЯ (JobQueue) ====================
    
    async def scheduled_post_job(self, context: ContextTypes.DEFAULT_TYPE):
        """Задача для автоматической публикации"""
        try:
            quote = self.db.get_next_quote_with_ai_fallback()
            if not quote:
                return
            
            post_text = f"""
💬 <b>Цитата дня</b>

«{quote['text']}»

— <i>{quote['author']}</i>

#{quote['category']} #ЦитатаДня #Мудрость

🕰 {datetime.now().strftime('%H:%M')} | 📅 {datetime.now().strftime('%d.%m.%Y')}
            """.strip()
            
            # Используем context.bot
            await context.bot.send_message(
                chat_id=self.channel_id,
                text=post_text,
                parse_mode='HTML'
            )
            
            logger.info(f"Автопубликация: {quote['id']}")
            
            # Уведомление админу
            await context.bot.send_message(
                chat_id=self.admin_id,
                text=f"✅ Опубликована цитата #{quote['id']}"
            )
            
        except Exception as e:
            logger.error(f"Ошибка автопубликации: {e}")


def main():
    """Главная функция запуска"""
    bot = WisdomBotWithButtons()
    bot.run_bot()

if __name__ == "__main__":
    main()