# deepseek_generator.py
import os
import json
import random
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class DeepSeekGenerator:
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.api_url = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
        
        if not self.api_key:
            print("⚠️  DEEPSEEK_API_KEY не установлен. AI генерация отключена.")
            self.enabled = False
        else:
            self.enabled = True
        
        # Темы для генерации
        self.topics = [
            "успех и достижения",
            "преодоление трудностей", 
            "саморазвитие и рост",
            "целеустремленность",
            "уверенность в себе",
            "позитивное мышление",
            "время и продуктивность",
            "мужество и смелость",
            "настойчивость",
            "творчество и вдохновение",
            "лидерство",
            "баланс жизни и работы",
            "принятие решений",
            "обучение на ошибках"
        ]
        
        # Стили цитат
        self.styles = [
            "древняя мудрость",
            "современная психология",
            "философская мысль",
            "практический совет",
            "поэтическое высказывание",
            "деловая мудрость",
            "спортивная мотивация",
            "научный подход",
            "художественное выражение"
        ]
        
        # Известные авторы для стилизации
        self.authors = [
            "Сократ", "Аристотель", "Конфуций", "Лао-цзы", 
            "Марк Аврелий", "Сенека", "Фридрих Ницше", 
            "Альберт Эйнштейн", "Стив Джобс", "Илон Маск",
            "Михаил Булгаков", "Федор Достоевский", "Лев Толстой",
            "Нельсон Мандела", "Махатма Ганди", "Мартин Лютер Кинг",
            "Опра Уинфри", "Тони Роббинс", "Наполеон Хилл",
            "Дейл Карнеги", "Робин Шарма", "Экхарт Толле"
        ]
    
    def generate_motivational_quote(self, topic: str = None, style: str = None) -> Dict:
        """Генерирует уникальную мотивационную цитату"""
        if not self.enabled:
            return self._get_fallback_quote()
        
        topic = topic or random.choice(self.topics)
        style = style or random.choice(self.styles)
        
        prompt = self._create_quote_prompt(topic, style)
        
        try:
            response = self._call_deepseek_api(prompt)
            
            if response:
                return self._parse_quote_response(response, topic, style)
            else:
                return self._get_fallback_quote()
                
        except Exception as e:
            print(f"❌ Ошибка генерации цитаты: {e}")
            return self._get_fallback_quote()
    
    def generate_quote_with_explanation(self) -> Dict:
        """Генерирует цитату с объяснением"""
        if not self.enabled:
            return self._get_fallback_quote_with_explanation()
        
        prompt = """Создай мотивационную цитату и краткое объяснение к ней.

Формат ответа JSON:
{
  "quote": "Текст цитаты",
  "author": "Автор или источник",
  "explanation": "Краткое объяснение смысла (2-3 предложения)",
  "category": "Основная тема",
  "tags": ["тег1", "тег2"]
}

Цитата должна быть:
1. Оригинальной и вдохновляющей
2. Не длиннее 2 предложений
3. На русском языке
4. Соответствовать теме мотивации и саморазвития

Объяснение должно быть:
1. Практичным и полезным
2. Помогать применить цитату в жизни
3. Не более 3 предложений"""
        
        try:
            response = self._call_deepseek_api(prompt, json_mode=True)
            
            if response:
                quote_data = self._parse_json_response(response)
                if quote_data:
                    return quote_data
            
            return self._get_fallback_quote_with_explanation()
            
        except Exception as e:
            print(f"❌ Ошибка генерации с объяснением: {e}")
            return self._get_fallback_quote_with_explanation()
    
    def generate_daily_wisdom(self) -> Dict:
        """Генерирует мудрость дня с практическим заданием"""
        if not self.enabled:
            return self._get_fallback_daily_wisdom()
        
        day_of_week = datetime.now().strftime("%A")
        
        prompt = f"""Сегодня {day_of_week}. Создай "Мудрость дня" с практическим заданием.

Структура:
1. **Цитата дня** - вдохновляющее высказывание
2. **Разбор** - почему это важно сегодня
3. **Практическое задание** - конкретное действие на день
4. **Ключевая мысль** - главный вывод
5. **Эмодзи** - подходящий символ

Тема: {random.choice(self.topics)}
Стиль: {random.choice(['практичный', 'философский', 'мотивационный'])}

Верни ответ в JSON формате."""
        
        try:
            response = self._call_deepseek_api(prompt, temperature=0.8, json_mode=True)
            
            if response:
                wisdom_data = self._parse_json_response(response)
                if wisdom_data:
                    wisdom_data['generated_by'] = 'deepseek'
                    wisdom_data['generated_at'] = datetime.now().isoformat()
                    return wisdom_data
            
            return self._get_fallback_daily_wisdom()
            
        except Exception as e:
            print(f"❌ Ошибка генерации мудрости дня: {e}")
            return self._get_fallback_daily_wisdom()
    
    def generate_personalized_quote(self, user_context: Dict = None) -> Dict:
        """Генерирует персонализированную цитату"""
        if not self.enabled:
            return self._get_fallback_quote()
        
        context = user_context or {}
        name = context.get('name', 'друг')
        mood = context.get('mood', 'нейтральный')
        
        prompt = f"""Создай персонализированную мотивационную цитату для человека по имени {name}.

Его/ее текущее состояние: {mood}

Цитата должна:
1. Быть обращена лично к {name}
2. Учитывать настроение: {mood}
3. Быть поддерживающей и вдохновляющей
4. Содержать практический совет
5. Быть не длиннее 3 предложений

Верни в JSON формате."""
        
        try:
            response = self._call_deepseek_api(prompt, json_mode=True)
            
            if response:
                personalized_data = self._parse_json_response(response)
                if personalized_data:
                    personalized_data['personalized_for'] = name
                    return personalized_data
            
            return self._get_fallback_quote()
            
        except Exception as e:
            print(f"❌ Ошибка персонализированной генерации: {e}")
            return self._get_fallback_quote()
    
    def _create_quote_prompt(self, topic: str, style: str) -> str:
        """Создает промпт для генерации цитаты"""
        author = random.choice(self.authors)
        
        prompts = [
            f"""Сгенерируй оригинальную мотивационную цитату в стиле {author} на тему "{topic}".

Требования:
1. Цитата должна быть уникальной (не существующей ранее)
2. Стиль: {style}
3. Длина: 1-2 предложения
4. Язык: русский
5. Формат: "Цитата" - Автор
6. Добавь 3 хэштега по теме""",

            f"""Придумай новую, никогда не публиковавшуюся цитату о {topic}.

Стилизуй под {style}.
Используй манеру высказываний {author}.

Формат ответа:
Цитата: [текст]
Автор: [имя]
Хэштеги: [3-5 тегов]""",

            f"""Создай уникальное мудрое высказывание на тему "{topic}".

Критерии:
- Оригинальность 100%
- Стиль: {style}
- Вдохновляющий эффект
- Лаконичность
- Практическая ценность

Подпиши как: - {author}"""
        ]
        
        return random.choice(prompts)
    
    def _call_deepseek_api(self, prompt: str, temperature: float = 0.7, json_mode: bool = False) -> Optional[str]:
        """Вызывает DeepSeek API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': 'Ты помощник, генерирующий уникальные мотивационные цитаты. Отвечай на русском языке.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': temperature,
            'max_tokens': 500
        }
        
        if json_mode:
            data['response_format'] = {'type': 'json_object'}
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Ошибка запроса к DeepSeek: {e}")
            return None
        except Exception as e:
            print(f"⚠️  Ошибка обработки ответа: {e}")
            return None
    
    def _parse_quote_response(self, response: str, topic: str, style: str) -> Dict:
        """Парсит ответ от AI"""
        try:
            # Пытаемся найти цитату и автора
            lines = response.strip().split('\n')
            quote = ""
            author = "Генератор мудрости"
            
            for line in lines:
                line = line.strip()
                if '—' in line or '-' in line:
                    parts = line.split('—') if '—' in line else line.split('-')
                    if len(parts) >= 2:
                        quote = parts[0].strip().strip('"').strip("'")
                        author = parts[1].strip()
                        break
                elif 'Цитата:' in line:
                    quote = line.replace('Цитата:', '').strip()
                elif 'Автор:' in line:
                    author = line.replace('Автор:', '').strip()
            
            if not quote:
                quote = response.split('\n')[0].strip().strip('"').strip("'")
            
            # Извлекаем хэштеги
            tags = []
            for line in lines:
                if '#' in line or 'Хэштеги:' in line or 'Теги:' in line:
                    tag_line = line.replace('Хэштеги:', '').replace('Теги:', '').strip()
                    tags.extend([tag.strip().strip('#') for tag in tag_line.split() if '#' in tag])
            
            if not tags:
                tags = [topic.replace(' ', '').lower(), 'мотивация', 'цитата']
            
            return {
                'text': quote,
                'author': author,
                'category': topic,
                'tags': tags,
                'style': style,
                'source': 'ai',
                'ai_model': 'deepseek-chat',
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️  Ошибка парсинга: {e}")
            return self._get_fallback_quote()
    
    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """Парсит JSON ответ"""
        try:
            # Очищаем ответ от возможных markdown
            clean_response = response.strip()
            if '```json' in clean_response:
                clean_response = clean_response.split('```json')[1].split('```')[0].strip()
            elif '```' in clean_response:
                clean_response = clean_response.split('```')[1].split('```')[0].strip()
            
            data = json.loads(clean_response)
            
            # Добавляем метаданные
            data['source'] = 'ai'
            data['ai_model'] = 'deepseek-chat'
            data['generated_at'] = datetime.now().isoformat()
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Ошибка парсинга JSON: {e}")
            print(f"Ответ AI: {response}")
            return None
    
    # Фолбэк методы на случай недоступности AI
    def _get_fallback_quote(self) -> Dict:
        """Возвращает запасную цитату"""
        fallback_quotes = [
            {
                'text': 'Дорогу осилит идущий, а сидящий дома так и останется сидеть.',
                'author': 'Народная мудрость',
                'category': 'мотивация',
                'tags': ['действие', 'начало', 'путь'],
                'source': 'fallback'
            },
            {
                'text': 'Лучшее время для начала было вчера. Следующее лучшее время — сейчас.',
                'author': 'Китайская пословица',
                'category': 'продуктивность',
                'tags': ['время', 'старт', 'сейчас'],
                'source': 'fallback'
            },
            {
                'text': 'Не жди идеальных условий. Идеальные условия создаются в процессе.',
                'author': 'Правило действия',
                'category': 'рост',
                'tags': ['условия', 'процесс', 'действие'],
                'source': 'fallback'
            }
        ]
        
        quote = random.choice(fallback_quotes)
        quote['generated_at'] = datetime.now().isoformat()
        return quote
    
    def _get_fallback_quote_with_explanation(self) -> Dict:
        """Запасной вариант с объяснением"""
        return {
            'quote': 'Камень точит не сила, а частота падения капель.',
            'author': 'Восточная мудрость',
            'explanation': 'Успех достигается не разовыми героическими усилиями, а регулярными небольшими действиями. Постоянство важнее интенсивности.',
            'category': 'настойчивость',
            'tags': ['постоянство', 'процесс', 'регулярность'],
            'source': 'fallback',
            'generated_at': datetime.now().isoformat()
        }
    
    def _get_fallback_daily_wisdom(self) -> Dict:
        """Запасная мудрость дня"""
        return {
            'quote': 'Утро вечера мудренее.',
            'analysis': 'Иногда лучший способ решить проблему — дать себе время. Сон и отдых помогают взглянуть на ситуацию по-новому.',
            'task': 'Если сегодня вас что-то беспокоит, запишите это и отложите до завтрашнего утра.',
            'key_thought': 'Время — лучший советчик.',
            'emoji': '⏰',
            'source': 'fallback',
            'generated_at': datetime.now().isoformat()
        }

    def generate_interaction_reply(self, message_text: str, context_type: str = "comment") -> str:
        """Generates a reply for a comment or DM"""
        if not self.enabled:
            return "Спасибо!"
            
        system_prompt = (
            "Ты - мудрый и дружелюбный бот, который публикует мотивационные цитаты. "
            "Твоя задача - отвечать на комментарии или сообщения пользователей. "
            "Ответ должен быть кратким (не более 15 слов), вежливым и вдохновляющим. "
            "Используй эмодзи. Не используй хештеги."
        )
        
        user_prompt = f"Ответь на {context_type}: \"{message_text}\""
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                reply = result['choices'][0]['message']['content'].strip()
                return reply
            else:
                print(f"DeepSeek API Error (Interaction): {response.status_code}")
                return "Спасибо за ваш отклик! 🙏"
                
        except Exception as e:
            print(f"Error generating interaction reply: {e}")
            return "Спасибо! ✨"

# Создаем глобальный экземпляр
deepseek_gen = DeepSeekGenerator()