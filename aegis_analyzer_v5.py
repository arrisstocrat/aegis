from typing import Dict, List
import re

class AEGISAnalyzer:
    """AEGIS v5.2 FINAL - ПОЛНАЯ ПЕРЕДЕЛКА С ЭМОДЗИ И НОВЫМИ ТРИГГЕРАМИ"""
    
    def __init__(self):
        # === КРИТИЧНЫЕ ТРИГГЕРЫ (Вес 30-35) ===
        self.critical_triggers = {
            'credentials': {
                'weight': 30,
                'keywords': ['пароль', 'пин', 'код', 'реквизит', 'пин-код', 'cvv', 'cvc', 'карта', 'реквизиты', 'логин', 'username', 'password', 'пароль', 'пин код', 'код подтверждения']
            },
            'malware': {
                'weight': 35,
                'keywords': ['.exe', '.bat', '.scr', '.msi', '.dll', '.com', '.zip', '.rar', 'скачай', 'скачаи', 'установи', 'скачайте', 'исполняемый', 'файл exe', 'скачать файл']
            },
            'otp': {
                'weight': 32,
                'keywords': ['код из sms', 'код из смс', 'sms код', '2fa', 'двухфакторная', 'одноразовый код', 'отправь код', 'коды доступа', 'код подтверждения', 'проверка', 'верификация']
            },
            'banking': {
                'weight': 28,
                'keywords': ['сбербанк', 'альфа', 'райффайзен', 'втб', 'газпромбанк', 'яндекс касса', 'тинькофф', 'мегабанк', 'номер карты', 'номер счета', 'счет', 'карта 4']
            },
            'fake_authority': {
                'weight': 28,
                'keywords': ['мвд', 'фсб', 'налоговая', 'центробанк', 'полиция', 'прокуратура', 'суд', 'следствие', 'пристав', 'арест', 'судебный', 'уголовное']
            }
        }
        
        # === СОЦИАЛЬНАЯ ИНЖЕНЕРИЯ (Вес 25-32) ===
        self.social_engineering = {
            'family_scam': {
                'weight': 32,
                'keywords': ['мам', 'мама', 'папа', 'батя', 'бабушка', 'дедушка', 'брат', 'сестра', 'тетя', 'дядя', 'я в беде', 'помоги мне', 'срочно нужны деньги', 'новый номер', 'телефон упал', 'потерял телефон', 'старый номер']
            },
            'friend_scam': {
                'weight': 30,
                'keywords': ['друг', 'одноклассник', 'однокурсник', 'коллега', 'напарник', 'это я', 'узнаешь', 'я застрял', 'я в беде', 'скинь срочно', 'помощь нужна', 'бро', 'брат', 'чувак']
            },
            'baiting_media': {
                'weight': 28,
                'keywords': ['фото', 'видео про тебя', 'выложили', 'группе', 'вк', 'инстаграм', 'тик ток', 'удали пока', 'посмотри что', 'ого', 'жесть', 'ужас', 'компромат']
            },
            'job_scam': {
                'weight': 26,
                'keywords': ['работа', 'вакансия', 'удаленно', 'заработок', 'быстрые деньги', 'подработка', '50000', '100000', 'деньги каждый день', 'без опыта', 'домашняя работа']
            },
            'romance_scam': {
                'weight': 25,
                'keywords': ['люблю', 'девушка', 'парень', 'красивая', 'тебе нравлюсь', 'между нами', 'влюбился', 'ты нравишься', 'свидание', 'встреча', 'единственный']
            },
            'bec': {
                'weight': 31,
                'keywords': ['директор', 'генеральный', 'начальник', 'босс', 'это я', 'не звони', 'конфиденциально', 'никому не говори', 'срочный платеж', 'контракт срывается', 'в самолете', 'интернет плохой']
            }
        }
        
        # === ФИШИНГ И ССЫЛКИ (Вес 22-28) ===
        self.phishing = {
            'suspicious_links': {
                'weight': 28,
                'keywords': ['bit.ly', 'tinyurl', '.xyz', '.tk', '.ml', '.ga', '.cf', '.online', 'verify', 'confirm', 'login', 'update', '-bank', '-account', 'secure-', 'official-']
            },
            'urgency': {
                'weight': 24,
                'keywords': ['срочно', 'спешит', 'скорее', 'быстрее', '24 часа', '1 час', '2 часа', '30 минут', 'не поздно', 'немедленно', 'немедля', 'сейчас', 'срок']
            },
            'threat_pressure': {
                'weight': 26,
                'keywords': ['заблокирован', 'отключу', 'удалю', 'заморозю', 'арестую', 'штраф', 'суд', 'уголовное', '115-фз', 'передам фсб', 'полиция']
            },
            'financial_lure': {
                'weight': 22,
                'keywords': ['деньги', 'рубли', 'доллар', 'евро', 'криптовалюта', 'биткоин', 'ton', 'приз', 'выигрыш', 'лотерея', 'бонус', 'скидка', 'перевод']
            }
        }
        
        # === РЕГИОНАЛЬНЫЕ (Вес 16-20) ===
        self.regional = {
            'messaging_apps': {
                'weight': 18,
                'keywords': ['telegram', 'телеграм', 'вконтакте', 'вк', 'whatsapp', 'viber', 'discord', 'телегра']
            },
            'marketplaces': {
                'weight': 16,
                'keywords': ['авито', 'озон', 'wildberries', 'яндекс.маркет', 'aliexpress', 'ebay', 'steam', 'wb-', 'cdek']
            },
            'payment_systems': {
                'weight': 20,
                'keywords': ['яндекс касса', 'яндекс кошелек', 'qiwi', 'webmoney', 'yandex', 'sberbank', 'tinkoff', '2pay', 'юнистрим']
            }
        }
        
        # === КАРТОЧКА ВЫВОДОВ ===
        self.threat_type_map = {
            'family_scam': '👨‍👩‍👧 Семейный скам',
            'friend_scam': '👥 Скам "друг в беде"',
            'bec': '💼 BEC-атака',
            'malware': '🦠 Вредонос',
            'suspicious_links': '🎣 Фишинг',
            'banking': '🏦 Банковский скам',
            'credentials': '🔑 Кража данных',
            'baiting_media': '📸 Приманка медиа',
            'job_scam': '💼 Скам вакансия',
            'fake_authority': '👮 Подделка власти',
            'otp': '📲 Кража OTP',
            'threat_pressure': '⚖️ Угрозы',
            'financial_lure': '💰 Финансовая приманка'
        }
    
    def analyze(self, text: str) -> Dict:
        """ОСНОВНОЙ АНАЛИЗ"""
        text_lower = text.lower()
        text_length = len(text)
        
        # === ПОИСК ТРИГГЕРОВ ===
        detected_triggers = self._find_triggers(text_lower)
        detected_categories = self._get_categories(detected_triggers)
        
        # === БАЗОВЫЙ SCORE ===
        base_score = sum([t['weight'] for t in detected_triggers])
        
        # === КОМБО-БОНУСЫ ===
        combo_bonus = self._calculate_combo_bonus(detected_categories)
        
        # === СПЕЦИАЛЬНЫЕ ПАТТЕРНЫ ===
        special_bonus = self._special_patterns(text_lower)
        
        # === SHORT_MESSAGE_BOOST ===
        short_boost = self._short_message_boost(detected_triggers, text_length)
        
        # === ФИНАЛЬНЫЙ SCORE ===
        final_score = min(100, base_score + combo_bonus + special_bonus + short_boost)
        
        # === УРОВЕНЬ РИСКА И ЭМОДЗИ ===
        if final_score >= 80:
            risk_level = "CRITICAL"
            emoji = "🔴"
        elif final_score >= 60:
            risk_level = "HIGH"
            emoji = "🟠"
        elif final_score >= 45:
            risk_level = "MEDIUM"
            emoji = "🟡"
        elif final_score >= 25:
            risk_level = "LOW"
            emoji = "🟢"
        else:
            risk_level = "SAFE"
            emoji = "✅"
        
        # === ТИП УГРОЗЫ ===
        threat_type = self._determine_threat_type(detected_categories)
        
        # === ФОРМАТИРОВАННЫЕ РЕЗУЛЬТАТЫ ===
        formatted_detected = []
        for t in detected_triggers[:8]:
            formatted_detected.append(f"• {t['name']}")
        
        return {
            'score': int(final_score),
            'risk_level': risk_level,
            'emoji': emoji,
            'threat_type': threat_type,
            'detected': formatted_detected,
            'flags_count': len(detected_triggers),
            'confidence': min(99, 50 + len(detected_triggers) * 5),
            'base_score': int(base_score),
            'combo_bonus': combo_bonus,
            'special_bonus': special_bonus,
            'short_boost': short_boost
        }
    
    def _find_triggers(self, text: str) -> List[Dict]:
        """Поиск триггеров"""
        triggers = []
        
        # Критичные
        for category, data in self.critical_triggers.items():
            for keyword in data['keywords']:
                if keyword in text:
                    triggers.append({
                        'name': f"{category}: {keyword}",
                        'weight': data['weight'],
                        'category': category
                    })
        
        # Соц. инженерия
        for category, data in self.social_engineering.items():
            for keyword in data['keywords']:
                if keyword in text:
                    triggers.append({
                        'name': f"{category}: {keyword}",
                        'weight': data['weight'],
                        'category': category
                    })
        
        # Фишинг
        for category, data in self.phishing.items():
            for keyword in data['keywords']:
                if keyword in text:
                    triggers.append({
                        'name': f"{category}: {keyword}",
                        'weight': data['weight'],
                        'category': category
                    })
        
        # Региональные
        for category, data in self.regional.items():
            for keyword in data['keywords']:
                if keyword in text:
                    triggers.append({
                        'name': f"{category}: {keyword}",
                        'weight': data['weight'],
                        'category': category
                    })
        
        return triggers
    
    def _get_categories(self, triggers: List[Dict]) -> set:
        """Извлечение категорий"""
        return set([t['category'] for t in triggers])
    
    def _calculate_combo_bonus(self, categories: set) -> int:
        """Расчет комбо-бонусов"""
        bonus = 0
        
        # Семья + деньги + срочно
        if {'family_scam', 'financial_lure', 'urgency'}.issubset(categories):
            bonus += 35
        
        # Вредонос + срочно
        if {'malware', 'urgency'}.issubset(categories):
            bonus += 40
        
        # Банк + крередитная карта + угроза
        if {'banking', 'credentials', 'threat_pressure'}.issubset(categories):
            bonus += 38
        
        # Фальшивая власть + деньги
        if {'fake_authority', 'financial_lure'}.issubset(categories):
            bonus += 36
        
        # Телеграм + фишинг + коды
        if {'messaging_apps', 'suspicious_links', 'credentials'}.issubset(categories):
            bonus += 30
        
        return bonus
    
    def _special_patterns(self, text: str) -> int:
        """Специальные паттерны"""
        bonus = 0
        
        # Номер карты
        if re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b', text):
            bonus += 28
        
        # Кириллица в доменах
        if re.search(r'[а-яё]+[.-][а-яё]+\.(xyz|tk|ml|ga|online)', text):
            bonus += 25
        
        # Множественные URL
        if len(re.findall(r'http[s]?://|www\.|\.com|\.ru', text)) >= 2:
            bonus += 15
        
        # Финансы + спешка
        if any(x in text for x in ['деньги', 'рубли', 'карта']) and any(x in text for x in ['срочно', 'спешит']):
            bonus += 20
        
        return bonus
    
    def _short_message_boost(self, triggers: List[Dict], text_length: int) -> int:
        """SHORT_MESSAGE_BOOST для коротких сообщений"""
        if text_length < 300 and len(triggers) >= 2:
            if len(triggers) == 2:
                return 15
            elif len(triggers) == 3:
                return 25
            else:
                return 35
        return 0
    
    def _determine_threat_type(self, categories: set) -> str:
        """Определение типа угрозы"""
        # Ищем первый найденный тип
        for cat in categories:
            if cat in self.threat_type_map:
                return self.threat_type_map[cat]
        
        # Fallback
        return '⚠️ Неизвестная угроза'
