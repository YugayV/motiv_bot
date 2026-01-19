import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List

class QuoteDatabase:
    def __init__(self, db_path='quotes.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_database()
    
    def init_database(self):
        """Создает таблицы"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                author TEXT,
                category TEXT,
                tags TEXT,
                used_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                source TEXT DEFAULT 'manual',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    # СУЩЕСТВУЮЩИЕ МЕТОДЫ...
    
    def get_random_quote_for_button(self) -> Optional[Dict]:
        """Получает абсолютно случайную цитату (для кнопки)"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM quotes 
            ORDER BY RANDOM() 
            LIMIT 1
        ''')
        quote = cursor.fetchone()
        
        if quote:
            # Не увеличиваем счетчик для ручного запроса
            return dict(quote)
        return None
    
    def get_quote_by_category(self, category: str) -> Optional[Dict]:
        """Получает случайную цитату по категории"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM quotes 
            WHERE category = ?
            ORDER BY RANDOM() 
            LIMIT 1
        ''', (category,))
        quote = cursor.fetchone()
        return dict(quote) if quote else None
    
    def get_categories(self) -> List[str]:
        """Возвращает список уникальных категорий"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM quotes WHERE category IS NOT NULL')
        return [row['category'] for row in cursor.fetchall()]
    
    def search_quotes(self, keyword: str, limit: int = 5) -> List[Dict]:
        """Ищет цитаты по ключевому слову"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM quotes 
            WHERE text LIKE ? OR author LIKE ?
            LIMIT ?
        ''', (f'%{keyword}%', f'%{keyword}%', limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_daily_stats(self) -> Dict:
        """Статистика за день"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM quotes")
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as used_today FROM quotes WHERE date(last_used) = date('now')")
        used_today = cursor.fetchone()['used_today']
        
        cursor.execute("SELECT COUNT(*) as manual_requests FROM quotes WHERE source = 'button_request'")
        manual_requests = cursor.fetchone()['manual_requests']
        
        return {
            'total': total,
            'used_today': used_today,
            'manual_requests': manual_requests,
            'available': total - used_today
        }