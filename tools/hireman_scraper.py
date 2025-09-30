import requests
from bs4 import BeautifulSoup
import time
import json
import re
from urllib.parse import urljoin, urlparse
import logging
from typing import Dict, List, Optional

class HiremanScraper:
    def __init__(self, base_url="https://www.thehireman.co.uk", delay=1):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Product category mapping based on codes
        self.category_mapping = {
            '01': 'Access Equipment',
            '02': 'Air Compressors & Tools',
            '03': 'Breaking & Drilling',
            '04': 'Cleaning Equipment',
            '05': 'Compaction Equipment',
            '06': 'Concrete Equipment',
            '07': 'Cutting & Grinding',
            '08': 'Dehumidifiers',
            '09': 'Electrical Equipment',
            '10': 'Fans & Ventilation',
            '11': 'Floor Care',
            '12': 'Garden Equipment',
            '13': 'Generators',
            '14': 'Hand Tools',
            '15': 'Heating',
            '16': 'Lifting Equipment',
            '17': 'Lighting',
            '18': 'Power Tools',
            '19': 'Pumps',
            '20': 'Safety Equipment',
            '21': 'Site Equipment',
            '22': 'Temporary Structures',
            '23': 'Testing Equipment',
            '24': 'Waste Management',
            '25': 'Welding Equipment'
        }
    
    def analyze_product_code(self, product_code: str) -> Dict:
        """Analyze product code to determine category and type"""
        
        # Extract prefix (e.g., "01" from "01/ABC123")
        prefix_match = re.match(r'^(\d{2})/', product_code)
        
        if prefix_match:
            prefix = prefix_match.group(1)
            category = self.category_mapping.get(prefix, 'Unknown')
            
            return {
                'prefix': prefix,
                'category': category,
                'full_code': product_code,
                'product_identifier': product_code.split('/')[-1] if '/' in product_code else product_code
            }
        
        return {
            'prefix': None,
            'category': 'Unknown',
            'full_code': product_code,
            'product_identifier': product_code
        }
    
    def discover_product_pages(self) -> List[str]:
        """Discover all product pages on the website"""
        
        product_urls = []
        
        try:
            # Start with main product categories
            category_urls = self._find_category_pages()
            
            for category_url in category_urls:
                print(f"Scanning category: {category_url}")
                category_products = self._scrape_category_page(category_url)
                product_urls.extend(category_products)
                time.sleep(self.delay)
            
            # Remove duplicates
            product_urls = list(set(product_urls))
            print(f"Found {len(product_urls)} product pages")
            
        except Exception as e:
            logging.error(f"Error discovering product pages: {e}")
        
        return product_urls
    
    def scrape_product_details(self, product_url: str) -> Optional[Dict]:
        """Scrape detailed information from a single product page"""
        
        try:
            response = self.session.get(product_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product information
            product_data = {
                'url': product_url,
                'title': self._extract_product_title(soup),
                'description': self._extract_product_description(soup),
                'technical_specs': self._extract_technical_specs(soup),
                'images': self._extract_product_images(soup),
                'price_info': self._extract_price_info(soup),
                'category': self._extract_category(soup),
                'brand': self._extract_brand(soup),
                'model': self._extract_model(soup),
                'scraped_at': time.time()
            }
            
            return product_data
            
        except Exception as e:
            logging.error(f"Error scraping product {product_url}: {e}")
            return None
    
    def find_similar_products(self, target_category: str, limit: int = 10) -> List[Dict]:
        """Find products in the same category for style analysis"""
        
        print(f"Finding similar products in category: {target_category}")
        
        # Discover all product pages
        all_products = self.discover_product_pages()
        
        similar_products = []
        
        for product_url in all_products[:50]:  # Limit to prevent too many requests
            try:
                product_data = self.scrape_product_details(product_url)
                
                if product_data and product_data.get('category', '').lower() == target_category.lower():
                    similar_products.append(product_data)
                    
                    if len(similar_products) >= limit:
                        break
                
                time.sleep(self.delay)
                
            except Exception as e:
                logging.error(f"Error processing {product_url}: {e}")
                continue
        
        return similar_products
    
    def analyze_style_patterns(self, products: List[Dict]) -> Dict:
        """Analyze title and description patterns from similar products"""
        
        patterns = {
            'title_patterns': [],
            'description_patterns': [],
            'technical_spec_patterns': [],
            'common_phrases': [],
            'title_structure': {},
            'avg_description_length': 0,
            'common_technical_fields': []
        }
        
        if not products:
            return patterns
        
        # Analyze titles
        titles = [p['title'] for p in products if p.get('title')]
        patterns['title_patterns'] = self._analyze_title_patterns(titles)
        
        # Analyze descriptions
        descriptions = [p['description'] for p in products if p.get('description')]
        patterns['description_patterns'] = self._analyze_description_patterns(descriptions)
        patterns['avg_description_length'] = sum(len(d.split()) for d in descriptions) // len(descriptions) if descriptions else 0
        
        # Analyze technical specs
        tech_specs = [p['technical_specs'] for p in products if p.get('technical_specs')]
        patterns['technical_spec_patterns'] = self._analyze_technical_patterns(tech_specs)
        
        return patterns
    
    def _find_category_pages(self) -> List[str]:
        """Find main category pages"""
        
        category_urls = []
        
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for navigation links, category links, etc.
            # This will need to be adapted based on the actual website structure
            category_selectors = [
                'nav a[href*="category"]',
                'nav a[href*="products"]',
                '.category-link',
                '.product-category',
                'a[href*="hire"]'
            ]
            
            for selector in category_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        category_urls.append(full_url)
            
            # Remove duplicates
            category_urls = list(set(category_urls))
            
        except Exception as e:
            logging.error(f"Error finding category pages: {e}")
        
        return category_urls[:20]  # Limit to prevent too many requests
    
    def _scrape_category_page(self, category_url: str) -> List[str]:
        """Scrape product links from a category page"""
        
        product_urls = []
        
        try:
            response = self.session.get(category_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for product links
            product_selectors = [
                'a[href*="product"]',
                '.product-link',
                '.product-item a',
                'a[href*="hire"]',
                '.product-title a'
            ]
            
            for selector in product_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        product_urls.append(full_url)
            
        except Exception as e:
            logging.error(f"Error scraping category page {category_url}: {e}")
        
        return list(set(product_urls))
    
    def _extract_product_title(self, soup: BeautifulSoup) -> str:
        """Extract product title from page"""
        
        title_selectors = [
            'h1.product-title',
            'h1',
            '.product-name',
            '.product-title',
            'title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 5:  # Reasonable title length
                    return title
        
        return ""
    
    def _extract_product_description(self, soup: BeautifulSoup) -> str:
        """Extract product description from page"""
        
        description_selectors = [
            '.product-description',
            '.description',
            '.product-details',
            '.product-info p',
            '.content p'
        ]
        
        for selector in description_selectors:
            elements = soup.select(selector)
            if elements:
                description_parts = []
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 20:  # Reasonable description length
                        description_parts.append(text)
                
                if description_parts:
                    return ' '.join(description_parts)
        
        return ""
    
    def _extract_technical_specs(self, soup: BeautifulSoup) -> Dict:
        """Extract technical specifications from page"""
        
        specs = {}
        
        # Look for specification tables or lists
        spec_selectors = [
            '.specifications table',
            '.specs table',
            '.technical-specs',
            '.product-specs',
            '.specifications dl'
        ]
        
        for selector in spec_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'table':
                    specs.update(self._parse_spec_table(element))
                elif element.name == 'dl':
                    specs.update(self._parse_spec_list(element))
        
        return specs
    
    def _extract_product_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract product images"""
        
        images = []
        
        img_selectors = [
            '.product-image img',
            '.product-gallery img',
            '.main-image img'
        ]
        
        for selector in img_selectors:
            img_elements = soup.select(selector)
            for img in img_elements:
                src = img.get('src') or img.get('data-src')
                if src:
                    full_url = urljoin(self.base_url, src)
                    images.append(full_url)
        
        return images[:5]  # Limit to first 5 images
    
    def _extract_price_info(self, soup: BeautifulSoup) -> str:
        """Extract price information"""
        
        price_selectors = [
            '.price',
            '.cost',
            '.rate',
            '.hire-rate',
            '.daily-rate'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return ""
    
    def _extract_category(self, soup: BeautifulSoup) -> str:
        """Extract product category"""
        
        category_selectors = [
            '.breadcrumb a',
            '.category',
            '.product-category',
            'nav .active'
        ]
        
        for selector in category_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and text not in ['Home', 'Products']:
                    return text
        
        return ""
    
    def _extract_brand(self, soup: BeautifulSoup) -> str:
        """Extract product brand"""
        
        brand_selectors = [
            '.brand',
            '.manufacturer',
            '.product-brand'
        ]
        
        for selector in brand_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Try to extract from title
        title = self._extract_product_title(soup)
        if title:
            # Common brand names (you can expand this list)
            brands = ['Honda', 'Stihl', 'Makita', 'Bosch', 'Husqvarna', 'DeWalt', 'Hilti', 'Karcher']
            for brand in brands:
                if brand.lower() in title.lower():
                    return brand
        
        return ""
    
    def _extract_model(self, soup: BeautifulSoup) -> str:
        """Extract product model"""
        
        model_selectors = [
            '.model',
            '.product-model',
            '.model-number'
        ]
        
        for selector in model_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return ""
    
    def _parse_spec_table(self, table_element) -> Dict:
        """Parse specifications from table element"""
        
        specs = {}
        
        rows = table_element.select('tr')
        for row in rows:
            cells = row.select('td, th')
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                if key and value:
                    specs[key] = value
        
        return specs
    
    def _parse_spec_list(self, dl_element) -> Dict:
        """Parse specifications from definition list"""
        
        specs = {}
        
        dt_elements = dl_element.select('dt')
        dd_elements = dl_element.select('dd')
        
        for dt, dd in zip(dt_elements, dd_elements):
            key = dt.get_text(strip=True)
            value = dd.get_text(strip=True)
            if key and value:
                specs[key] = value
        
        return specs
    
    def _analyze_title_patterns(self, titles: List[str]) -> Dict:
        """Analyze patterns in product titles"""
        
        patterns = {
            'common_words': [],
            'structure_patterns': [],
            'brand_positions': [],
            'length_range': [0, 0]
        }
        
        if not titles:
            return patterns
        
        # Find common words
        all_words = []
        for title in titles:
            words = title.split()
            all_words.extend([word.lower() for word in words])
        
        word_counts = {}
        for word in all_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get most common words (excluding common articles)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        common_words = [word for word, count in sorted(word_counts.items(), key=lambda x: x[1], reverse=True) 
                       if count > 1 and word not in stop_words]
        
        patterns['common_words'] = common_words[:20]
        
        # Analyze length
        lengths = [len(title.split()) for title in titles]
        patterns['length_range'] = [min(lengths), max(lengths)]
        
        return patterns
    
    def _analyze_description_patterns(self, descriptions: List[str]) -> Dict:
        """Analyze patterns in product descriptions"""
        
        patterns = {
            'common_phrases': [],
            'sentence_starters': [],
            'length_range': [0, 0],
            'tone_indicators': []
        }
        
        if not descriptions:
            return patterns
        
        # Find common sentence starters
        starters = []
        for desc in descriptions:
            sentences = desc.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    words = sentence.split()[:3]  # First 3 words
                    if len(words) >= 2:
                        starters.append(' '.join(words))
        
        starter_counts = {}
        for starter in starters:
            starter_counts[starter] = starter_counts.get(starter, 0) + 1
        
        patterns['sentence_starters'] = [starter for starter, count in sorted(starter_counts.items(), key=lambda x: x[1], reverse=True) if count > 1][:10]
        
        # Analyze length
        lengths = [len(desc.split()) for desc in descriptions]
        patterns['length_range'] = [min(lengths), max(lengths)]
        
        return patterns
    
    def _analyze_technical_patterns(self, tech_specs: List[Dict]) -> Dict:
        """Analyze patterns in technical specifications"""
        
        patterns = {
            'common_fields': [],
            'field_types': {},
            'value_patterns': {}
        }
        
        if not tech_specs:
            return patterns
        
        # Find common specification fields
        all_fields = []
        for specs in tech_specs:
            all_fields.extend(specs.keys())
        
        field_counts = {}
        for field in all_fields:
            field_counts[field] = field_counts.get(field, 0) + 1
        
        patterns['common_fields'] = [field for field, count in sorted(field_counts.items(), key=lambda x: x[1], reverse=True) if count > 1]
        
        return patterns
    
    def save_analysis_data(self, data: Dict, filename: str):
        """Save analysis data to JSON file"""
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            print(f"Analysis data saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving analysis data: {e}")
    
    def load_analysis_data(self, filename: str) -> Dict:
        """Load previously saved analysis data"""
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading analysis data: {e}")
            return {}