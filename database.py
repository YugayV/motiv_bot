import sqlite3
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from deepseek_generator import deepseek_gen


class QuoteDatabase:
    """Database manager for quotes"""
    
    def __init__(self, db_path: str = 'quotes.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Quotes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                author TEXT,
                category TEXT,
                tags TEXT,
                source TEXT DEFAULT 'manual',
                ai_model TEXT,
                used_count INTEGER DEFAULT 0,
                last_used_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User favorites table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quote_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quote_id) REFERENCES quotes(id),
                UNIQUE(user_id, quote_id)
            )
        ''')
        
        # Usage stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id INTEGER NOT NULL,
                used_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                context TEXT,
                FOREIGN KEY (quote_id) REFERENCES quotes(id)
            )
        ''')
        
        self.conn.commit()
    
    def get_random_quote_for_button(self) -> Optional[Dict]:
        """Get a random quote for button press"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM quotes 
            ORDER BY RANDOM()
            LIMIT 1
        ''')
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_quote_by_category(self, category: str) -> Optional[Dict]:
        """Get a random quote from specific category"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM quotes 
            WHERE category = ?
            ORDER BY RANDOM()
            LIMIT 1
        ''', (category,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def search_quotes(self, query: str, limit: int = 5) -> List[Dict]:
        """Search quotes by author or text"""
        cursor = self.conn.cursor()
        search_pattern = f'%{query}%'
        cursor.execute('''
            SELECT * FROM quotes 
            WHERE author LIKE ? OR text LIKE ?
            ORDER BY used_count ASC
            LIMIT ?
        ''', (search_pattern, search_pattern, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_user_favorites(self, user_id: int) -> List[Dict]:
        """Get user's favorite quotes"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT q.* FROM quotes q
            INNER JOIN user_favorites uf ON q.id = uf.quote_id
            WHERE uf.user_id = ?
            ORDER BY uf.created_at DESC
        ''', (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def add_to_favorites(self, user_id: int, quote_id: int) -> bool:
        """Add quote to user's favorites"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO user_favorites (user_id, quote_id)
                VALUES (?, ?)
            ''', (user_id, quote_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Already in favorites
    
    def get_daily_stats(self) -> Dict:
        """Get daily statistics"""
        cursor = self.conn.cursor()
        
        # Total quotes
        cursor.execute("SELECT COUNT(*) as total FROM quotes")
        total = cursor.fetchone()['total']
        
        # Available quotes (not used today)
        cursor.execute('''
            SELECT COUNT(*) as available FROM quotes 
            WHERE date(last_used_at) != date('now') OR last_used_at IS NULL
        ''')
        available = cursor.fetchone()['available']
        
        # Used today
        cursor.execute('''
            SELECT COUNT(*) as used_today FROM quotes 
            WHERE date(last_used_at) = date('now')
        ''')
        used_today = cursor.fetchone()['used_today']
        
        return {
            'total': total,
            'available': available,
            'used_today': used_today,
            'manual_requests': 0  # Can be tracked separately
        }
    
    def get_next_quote(self) -> Optional[Dict]:
        """Get next quote for scheduled posting"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM quotes 
            WHERE date(last_used_at) != date('now') OR last_used_at IS NULL
            ORDER BY used_count ASC, RANDOM()
            LIMIT 1
        ''')
        row = cursor.fetchone()
        
        if row:
            quote = dict(row)
            # Mark as used
            cursor.execute('''
                UPDATE quotes 
                SET used_count = used_count + 1, last_used_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (quote['id'],))
            self.conn.commit()
            return quote
        
        return None
    
    def generate_and_save_ai_quote(self, topic: str = None, style: str = None) -> Optional[Dict]:
        """Generate and save AI quote"""
        if not deepseek_gen.enabled:
            print("⚠️  AI generation disabled")
            return None
        
        # Generate quote
        quote_data = deepseek_gen.generate_motivational_quote(topic, style)
        
        if quote_data:
            # Save to database
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO quotes (text, author, category, tags, source, ai_model)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                quote_data['text'],
                quote_data['author'],
                quote_data['category'],
                json.dumps(quote_data.get('tags', [])),
                'ai',
                quote_data.get('ai_model', 'deepseek-chat')
            ))
            
            quote_id = cursor.lastrowid
            self.conn.commit()
            
            quote_data['id'] = quote_id
            print(f"✅ AI quote saved with ID: {quote_id}")
            
            return quote_data
        
        return None
    
    def get_ai_generation_stats(self) -> Dict:
        """Get AI generation statistics"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM quotes WHERE source = 'ai'")
        total_ai = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as today FROM quotes WHERE source = 'ai' AND date(created_at) = date('now')")
        today_ai = cursor.fetchone()['today']
        
        cursor.execute("SELECT COUNT(DISTINCT ai_model) as models FROM quotes WHERE source = 'ai' AND ai_model IS NOT NULL")
        models = cursor.fetchone()['models']
        
        return {
            'total_ai_quotes': total_ai,
            'today_ai_quotes': today_ai,
            'ai_models_used': models,
            'ai_enabled': deepseek_gen.enabled
        }
    
    def get_next_quote_with_ai_fallback(self) -> Optional[Dict]:
        """Get next quote, generate AI if manual quotes are exhausted"""
        # First try manual quotes
        quote = self.get_next_quote()
        
        if not quote:
            print("📝 Manual quotes exhausted, generating AI...")
            # Generate AI quote
            quote_data = self.generate_and_save_ai_quote()
            
            if quote_data:
                return quote_data
            else:
                # If AI failed, get any old quote
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT * FROM quotes 
                    ORDER BY used_count ASC, RANDOM()
                    LIMIT 1
                ''')
                fallback = cursor.fetchone()
                return dict(fallback) if fallback else None
        
        return quote
    
    def add_quote(self, text: str, author: str, category: str, tags: List[str] = None) -> int:
        """Add a new quote manually"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO quotes (text, author, category, tags, source)
            VALUES (?, ?, ?, ?, 'manual')
        ''', (text, author, category, json.dumps(tags or [])))
        
        quote_id = cursor.lastrowid
        self.conn.commit()
        return quote_id
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()