import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import random
import json
import logging
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OLXParserDebug:
    def __init__(self):
        self.base_url = "https://www.olx.kz"
        self.search_url = "https://www.olx.kz/nedvizhimost/kommercheskie-pomeshcheniya/arenda/"
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        self.session = requests.Session()
        self.max_pages = 3  # Уменьшили для отладки
        self.request_timeout = 10
        self.output_file = "olx_commercial_debug.csv"
        
    def setup_session(self) -> None:
        """Настраивает сессию с правильными заголовками"""
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def scrape_page_debug(self, page_url: str) -> List[Dict]:
        """Отладочная версия парсинга страницы"""
        try:
            self.session.headers['User-Agent'] = random.choice(self.user_agents)
            response = self.session.get(page_url, timeout=self.request_timeout)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем объявления
            items = soup.select('div[data-cy="l-card"]')
            logger.info(f"Найдено {len(items)} элементов div[data-cy='l-card']")
            
            if not items:
                # Пробуем альтернативные селекторы и выводим структуру
                logger.warning("Основной селектор не сработал, анализируем страницу...")
                self._debug_page_structure(soup)
                return []
            
            listings = []
            
            for i, item in enumerate(items[:5]):  # Берем только первые 5 для отладки
                logger.info(f"\n--- Отладка объявления #{i+1} ---")
                listing_data = self._extract_listing_data_debug(item)
                if listing_data:
                    listings.append(listing_data)
                    
            return listings
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге страницы: {e}")
            return []

    def _debug_page_structure(self, soup: BeautifulSoup):
        """Анализирует структуру страницы для отладки"""
        logger.info("=== АНАЛИЗ СТРУКТУРЫ СТРАНИЦЫ ===")
        
        # Проверяем разные возможные селекторы
        selectors_to_check = [
            'div[data-cy="l-card"]',
            '.css-1sw7q4x',
            '[data-testid="l-card"]',
            '.offer-wrapper',
            'div[data-marker="item"]',
            'article',
            '.ad-card'
        ]
        
        for selector in selectors_to_check:
            elements = soup.select(selector)
            logger.info(f"Селектор '{selector}': найдено {len(elements)} элементов")
            
            if elements and len(elements) > 0:
                # Показываем структуру первого элемента
                first_elem = elements[0]
                logger.info(f"Первый элемент '{selector}':")
                logger.info(f"  - Тег: {first_elem.name}")
                logger.info(f"  - Классы: {first_elem.get('class', [])}")
                logger.info(f"  - Атрибуты: {list(first_elem.attrs.keys())}")
                
                # Ищем заголовки внутри
                titles = first_elem.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                logger.info(f"  - Найдено заголовков: {len(titles)}")
                for title in titles[:2]:
                    logger.info(f"    • {title.name}: '{title.get_text(strip=True)[:50]}...'")

    def _extract_listing_data_debug(self, item) -> Optional[Dict]:
        """Отладочная версия извлечения данных"""
        logger.info(f"Структура элемента: {item.name}, классы: {item.get('class', [])}")
        
        # Пробуем разные селекторы для заголовка
        title_selectors = [
            'h6', 'h4', 'h3', 'h2', 'h1',
            '[data-cy="ad-card-title"]', 
            'a[data-cy="listing-ad-title"]',
            '.css-16v5mdi',
            '.css-u2ayx9'
        ]
        
        title = "N/A"
        for selector in title_selectors:
            title_elem = item.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                logger.info(f"✅ Заголовок найден через '{selector}': '{title[:50]}...'")
                break
            else:
                logger.debug(f"❌ Селектор '{selector}' не сработал")
        
        # Пробуем разные селекторы для цены
        price_selectors = [
            '[data-testid="ad-price"]',
            '.price',
            '[data-cy="ad-card-price"]',
            '.css-10b0gli',
            '.css-1uwte2c'
        ]
        
        price_text = "N/A"
        for selector in price_selectors:
            price_elem = item.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                logger.info(f"✅ Цена найдена через '{selector}': '{price_text}'")
                break
            else:
                logger.debug(f"❌ Селектор цены '{selector}' не сработал")
        
        # Извлекаем числовую цену
        price_numeric = self._extract_price_debug(price_text)
        
        # Пробуем разные селекторы для локации
        location_selectors = [
            '[data-testid="location-date"]',
            '.bottom-cell',
            '[data-cy="ad-card-location"]',
            '.css-1a4brun'
        ]
        
        location = "N/A"
        for selector in location_selectors:
            location_elem = item.select_one(selector)
            if location_elem:
                location = location_elem.get_text(strip=True)
                logger.info(f"✅ Локация найдена через '{selector}': '{location}'")
                break
            else:
                logger.debug(f"❌ Селектор локации '{selector}' не сработал")
        
        # Ищем ссылку
        link_elem = item.select_one('a')
        relative_link = link_elem.get('href', '') if link_elem else ''
        full_link = urljoin(self.base_url, relative_link) if relative_link else 'N/A'
        
        # Извлекаем площадь
        area = self._extract_area_debug(title)
        
        result = {
            'title': title,
            'price_text': price_text,
            'price_numeric': price_numeric,
            'area': area,
            'location': location,
            'link': full_link
        }
        
        logger.info(f"📊 Итоговые данные: {result}")
        return result

    def _extract_price_debug(self, price_text: str) -> Optional[float]:
        """Отладочная версия извлечения цены"""
        logger.info(f"Обрабатываем цену: '{price_text}'")
        
        if not price_text or price_text == 'N/A':
            logger.info("Цена пустая или N/A")
            return None
        
        # Убираем все кроме цифр и пробелов
        price_clean = re.sub(r'[^\d\s]', '', price_text)
        price_clean = re.sub(r'\s+', '', price_clean)
        
        logger.info(f"Очищенная цена: '{price_clean}'")
        
        try:
            result = float(price_clean) if price_clean else None
            logger.info(f"Числовая цена: {result}")
            return result
        except ValueError as e:
            logger.info(f"Ошибка конвертации цены: {e}")
            return None

    def _extract_area_debug(self, title: str) -> Optional[float]:
        """Отладочная версия извлечения площади"""
        logger.info(f"Ищем площадь в заголовке: '{title}'")
        
        # Расширенные паттерны для поиска площади
        area_patterns = [
            r'(\d+(?:[.,]\d+)?)\s*м²',        # 50 м², 75.5м²
            r'(\d+(?:[.,]\d+)?)\s*кв\.?м',     # 50 кв.м, 75 кв м
            r'(\d+(?:[.,]\d+)?)\s*m²',         # 50 m²
            r'(\d+(?:[.,]\d+)?)\s*кв\.?\s*м',  # 50 кв м
        ]
        
        for pattern in area_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                try:
                    area_str = match.group(1).replace(',', '.')
                    area = float(area_str)
                    logger.info(f"✅ Площадь найдена по паттерну '{pattern}': {area} м²")
                    return area
                except ValueError:
                    continue
        
        logger.info("❌ Площадь не найдена")
        return None

    def analyze_data_debug(self, listings: List[Dict]):
        """Анализируем собранные данные"""
        logger.info(f"\n=== АНАЛИЗ СОБРАННЫХ ДАННЫХ ===")
        logger.info(f"Всего объявлений: {len(listings)}")
        
        if not listings:
            logger.warning("Нет данных для анализа")
            return
        
        # Анализ цен
        prices = [l['price_numeric'] for l in listings if l['price_numeric'] is not None]
        logger.info(f"Объявлений с ценой: {len(prices)}")
        if prices:
            logger.info(f"Мин. цена: {min(prices):,} тенге")
            logger.info(f"Макс. цена: {max(prices):,} тенге")
            logger.info(f"Средняя цена: {sum(prices)/len(prices):,.0f} тенге")
        
        # Анализ площадей
        areas = [l['area'] for l in listings if l['area'] is not None]
        logger.info(f"Объявлений с площадью: {len(areas)}")
        if areas:
            logger.info(f"Мин. площадь: {min(areas)} м²")
            logger.info(f"Макс. площадь: {max(areas)} м²")
            logger.info(f"Средняя площадь: {sum(areas)/len(areas):.1f} м²")
        
        # Анализ локаций
        locations = [l['location'] for l in listings if l['location'] != 'N/A']
        unique_locations = list(set(locations))
        logger.info(f"Уникальных локаций: {len(unique_locations)}")
        for loc in unique_locations[:5]:
            logger.info(f"  • {loc}")
        
        # Проверяем фильтры
        logger.info(f"\n=== ПРОВЕРКА ФИЛЬТРОВ ===")
        
        # Фильтр по площади (>= 50)
        area_filter_pass = len([l for l in listings if l['area'] and l['area'] >= 50])
        logger.info(f"Прошли фильтр площади (>= 50 м²): {area_filter_pass}")
        
        # Фильтр по цене (<= 500000)
        price_filter_pass = len([l for l in listings if l['price_numeric'] and l['price_numeric'] <= 500000])
        logger.info(f"Прошли фильтр цены (<= 500,000): {price_filter_pass}")
        
        # Фильтр по локации
        location_filter_pass = len([l for l in listings if any(keyword.lower() in l['location'].lower() 
                                                             for keyword in ['алматы', 'центр'])])
        logger.info(f"Прошли фильтр локации (Алматы/центр): {location_filter_pass}")
        
        # Все фильтры вместе
        combined_pass = 0
        for l in listings:
            area_ok = l['area'] and l['area'] >= 50
            price_ok = l['price_numeric'] and l['price_numeric'] <= 500000
            location_ok = any(keyword.lower() in l['location'].lower() for keyword in ['алматы', 'центр'])
            
            if area_ok and price_ok and location_ok:
                combined_pass += 1
        
        logger.info(f"Прошли все фильтры одновременно: {combined_pass}")

    def run_debug(self):
        """Запускает отладочную версию парсинга"""
        logger.info("🔍 ЗАПУСК ОТЛАДОЧНОГО РЕЖИМА")
        self.setup_session()
        
        all_listings = []
        
        for page in range(1, self.max_pages + 1):
            page_url = f"{self.search_url}?page={page}"
            logger.info(f"\n📄 Парсинг страницы {page}: {page_url}")
            
            listings = self.scrape_page_debug(page_url)
            all_listings.extend(listings)
            
            sleep(random.uniform(2, 4))
        
        # Анализируем собранные данные
        self.analyze_data_debug(all_listings)
        
        # Сохраняем для анализа
        if all_listings:
            df = pd.DataFrame(all_listings)
            df.to_csv("debug_results.csv", index=False, encoding='utf-8-sig')
            logger.info("Отладочные данные сохранены в debug_results.csv")


def main():
    parser = OLXParserDebug()
    parser.run_debug()


if __name__ == "__main__":
    main()