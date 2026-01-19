from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from database import QuoteDatabase

db = QuoteDatabase()

def get_main_keyboard():
    """Основная клавиатура меню"""
    keyboard = [
        [KeyboardButton("🎲 Случайная цитата")],
        [KeyboardButton("📚 По категориям"), KeyboardButton("🔍 Поиск")],
        [KeyboardButton("📊 Статистика"), KeyboardButton("ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_categories_keyboard():
    """Клавиатура с категориями"""
    categories = db.get_categories()
    
    # Группируем по 2 кнопки в ряд
    buttons = []
    row = []
    
    for i, category in enumerate(categories):
        emoji = get_category_emoji(category)
        row.append(InlineKeyboardButton(f"{emoji} {category.capitalize()}", callback_data=f"cat_{category}"))
        
        if len(row) == 2 or i == len(categories) - 1:
            buttons.append(row)
            row = []
    
    # Добавляем кнопку "Назад"
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(buttons)

def get_search_options_keyboard():
    """Клавиатура для поиска"""
    keyboard = [
        [InlineKeyboardButton("🔎 По автору", callback_data="search_author")],
        [InlineKeyboardButton("🏷️ По тегу", callback_data="search_tag")],
        [InlineKeyboardButton("📝 По тексту", callback_data="search_text")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_quote_actions_keyboard(quote_id: int, is_favorite: bool = False):
    """Кнопки действий с цитатой"""
    favorite_icon = "❤️" if is_favorite else "🤍"
    
    keyboard = [
        [
            InlineKeyboardButton("🔄 Еще цитату", callback_data="another_quote"),
            InlineKeyboardButton(f"{favorite_icon} В избранное", callback_data=f"fav_{quote_id}")
        ],
        [
            InlineKeyboardButton("📤 Поделиться", callback_data=f"share_{quote_id}"),
            InlineKeyboardButton("📊 Статистика", callback_data="quote_stats")
        ],
        [
            InlineKeyboardButton("🏠 В меню", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard():
    """Клавиатура для админа"""
    keyboard = [
        [KeyboardButton("📤 Опубликовать сейчас")],
        [KeyboardButton("📥 Добавить цитату"), KeyboardButton("🗑️ Удалить цитату")],
        [KeyboardButton("📊 Полная статистика"), KeyboardButton("⚙️ Настройки")],
        [KeyboardButton("🏠 В главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_category_emoji(category: str) -> str:
    """Возвращает эмодзи для категории"""
    emoji_map = {
        'motivation': '🚀',
        'wisdom': '🧠',
        'productivity': '⚡',
        'business': '💼',
        'life': '❤️',
        'creativity': '🎨',
        'success': '🏆',
        'philosophy': '🤔',
        'love': '💕',
        'science': '🔬',
        'art': '🎭',
        'education': '📚',
        'health': '💪',
        'humor': '😄'
    }
    return emoji_map.get(category.lower(), '📌')