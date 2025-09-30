import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import json
import os
from typing import Dict, List, Optional
import logging
from urllib.parse import urljoin
import time

class ExcelProductHandler:
    def __init__(self, excel_file_path: str = None):
        self.excel_file_path = excel_file_path
        self.product_data = None
        self.manufacturer_cache = {}
        
    def load_product_data(self, file_path: str = None) -> pd.DataFrame:
        """Load product data from Excel file"""
        
        if file_path:
            self.excel_file_path = file_path
        
        if not self.excel_file_path or not os.path.exists(self.excel_file_path):
            return self._create_sample_product_data()
        
        try:
            # Try to read the Excel file
            df = pd.read_excel(self.excel_file_path, engine='openpyxl')
            self.product_data = self._standardize_columns(df)
            return self.product_data
        except Exception as e:
            logging.error(f"Error loading Excel file: {e}")
            return self._create_sample_product_data()
    
    def get_products_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Get products from the same category for style analysis"""
        
        if self.product_data is None:
            self.product_data = self.load_product_data()
        
        # Filter by category
        category_products = self.product_data[
            self.product_data['category'].str.contains(category, case=False, na=False)
        ]
        
        # Convert to list of dictionaries
        products = []
        for _, row in category_products.head(limit).iterrows():
            product = {
                'stock_number': row.get('stock_number', ''),
                'title': row.get('title', ''),
                'description': row.get('description', ''),
                'technical_specs': self._parse_technical_specs(row),
                'brand': row.get('brand', ''),
                'model': row.get('model', ''),
                'category': row.get('category', ''),
                'manufacturer_website': row.get('manufacturer_website', ''),
                'power_type': row.get('power_type', ''),
                'power_output': row.get('power_output', '')
            }
            products.append(product)
        
        return products
    
    def analyze_product_code(self, product_code: str) -> Dict:
        """Analyze product code to determine category"""
        
        # Product category mapping based on codes
        category_mapping = {
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
        
        # Extract prefix (e.g., "01" from "01/ABC123")
        prefix_match = re.match(r'^(\d{2})/', product_code)
        
        if prefix_match:
            prefix = prefix_match.group(1)
            category = category_mapping.get(prefix, 'Unknown')
            
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
    
    def scrape_manufacturer_info(self, manufacturer_website: str, product_name: str = "") -> Dict:
        """Scrape manufacturer website for additional product information"""
        
        if not manufacturer_website:
            return {}
        
        # Check cache first
        cache_key = f"{manufacturer_website}_{product_name}"
        if cache_key in self.manufacturer_cache:
            return self.manufacturer_cache[cache_key]
        
        try:
            print(f"Scraping manufacturer website: {manufacturer_website}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(manufacturer_website, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            manufacturer_info = {
                'website': manufacturer_website,
                'company_name': self._extract_company_name(soup),
                'product_info': self._find_product_info(soup, product_name),
                'features': self._extract_general_features(soup),
                'specifications': self._extract_general_specs(soup),
                'images': self._extract_images(soup)
            }
            
            # Cache the result
            self.manufacturer_cache[cache_key] = manufacturer_info
            
            time.sleep(1)  # Be respectful to manufacturer websites
            return manufacturer_info
            
        except Exception as e:
            logging.error(f"Error scraping manufacturer website {manufacturer_website}: {e}")
            return {'website': manufacturer_website, 'error': str(e)}
    
    def analyze_style_patterns(self, products: List[Dict]) -> Dict:
        """Analyze title and description patterns from similar products"""
        
        patterns = {
            'title_patterns': {},
            'description_patterns': {},
            'technical_spec_patterns': {},
            'manufacturer_patterns': {},
            'avg_description_length': 0
        }
        
        if not products:
            return patterns
        
        # Analyze titles
        titles = [p.get('title', '') for p in products if p.get('title')]
        patterns['title_patterns'] = self._analyze_title_patterns(titles)
        
        # Analyze descriptions
        descriptions = [p.get('description', '') for p in products if p.get('description')]
        if descriptions:
            patterns['description_patterns'] = self._analyze_description_patterns(descriptions)
            patterns['avg_description_length'] = sum(len(d.split()) for d in descriptions) // len(descriptions)
        
        # Analyze technical specs
        tech_specs = [p.get('technical_specs', {}) for p in products if p.get('technical_specs')]
        patterns['technical_spec_patterns'] = self._analyze_technical_patterns(tech_specs)
        
        # Analyze manufacturer patterns
        manufacturers = [p.get('manufacturer_website', '') for p in products if p.get('manufacturer_website')]
        patterns['manufacturer_patterns'] = {'common_manufacturers': list(set(manufacturers))}
        
        return patterns
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names in the DataFrame"""
        
        # Column mapping for different possible names
        column_mapping = {
            'stock_no': 'stock_number',
            'stock_code': 'stock_number',
            'product_code': 'stock_number',
            'sku': 'stock_number',
            'product_name': 'title',
            'name': 'title',
            'item_name': 'title',
            'product_title': 'title',
            'desc': 'description',
            'product_description': 'description',
            'details': 'description',
            'make': 'brand',
            'manufacturer': 'brand',
            'product_category': 'category',
            'type': 'category',
            'cat': 'category',
            'manufacturer_url': 'manufacturer_website',
            'brand_website': 'manufacturer_website',
            'website': 'manufacturer_website',
            'power': 'power_output',
            'specifications': 'technical_specs',
            'specs': 'technical_specs',
            'tech_specs': 'technical_specs'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Ensure required columns exist
        required_columns = [
            'stock_number', 'title', 'description', 'brand', 'model', 
            'category', 'manufacturer_website', 'power_type', 'power_output'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''
        
        return df
    
    def _parse_technical_specs(self, row: pd.Series) -> Dict:
        """Parse technical specifications from row data"""
        
        specs = {}
        
        # Look for specification columns
        spec_columns = [col for col in row.index if any(keyword in col.lower() for keyword in ['spec', 'technical', 'dimension', 'weight', 'power'])]
        
        for col in spec_columns:
            if pd.notna(row[col]) and str(row[col]).strip():
                specs[col.replace('_', ' ').title()] = str(row[col])
        
        # Add standard specs
        specs.update({
            'Brand': row.get('brand', ''),
            'Model': row.get('model', ''),
            'Category': row.get('category', ''),
            'Power Type': row.get('power_type', ''),
            'Power Output': row.get('power_output', '')
        })
        
        # Remove empty specs
        specs = {k: v for k, v in specs.items() if v}
        
        return specs
    
    def _extract_company_name(self, soup: BeautifulSoup) -> str:
        """Extract company name from manufacturer website"""
        
        # Look for company name in various places
        selectors = [
            'title',
            '.company-name',
            '.brand-name',
            '.logo-text',
            'h1',
            '.site-title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text and len(text) < 100:  # Reasonable company name length
                    return text
        
        return ""
    
    def _find_product_info(self, soup: BeautifulSoup, product_name: str) -> Dict:
        """Find specific product information on manufacturer website"""
        
        product_info = {}
        
        if not product_name:
            return product_info
        
        # Search for product-specific information
        # This is a basic implementation - could be enhanced
        text_content = soup.get_text().lower()
        product_name_lower = product_name.lower()
        
        if product_name_lower in text_content:
            product_info['found_on_site'] = True
            # Could extract specific product details here
        else:
            product_info['found_on_site'] = False
        
        return product_info
    
    def _extract_general_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract general product features from manufacturer website"""
        
        features = []
        
        # Look for feature lists
        feature_selectors = [
            '.features li',
            '.benefits li',
            '.advantages li',
            'ul li'
        ]
        
        for selector in feature_selectors:
            elements = soup.select(selector)
            for element in elements[:10]:  # Limit to first 10
                text = element.get_text(strip=True)
                if text and len(text) > 10 and len(text) < 200:
                    features.append(text)
        
        return features[:5]  # Return top 5 features
    
    def _extract_general_specs(self, soup: BeautifulSoup) -> Dict:
        """Extract general specifications from manufacturer website"""
        
        specs = {}
        
        # Look for specification tables
        spec_tables = soup.select('table')
        for table in spec_tables[:3]:  # Check first 3 tables
            rows = table.select('tr')
            for row in rows:
                cells = row.select('td, th')
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value and len(key) < 50 and len(value) < 100:
                        specs[key] = value
        
        return specs
    
    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract product images from manufacturer website"""
        
        images = []
        
        img_elements = soup.select('img')
        for img in img_elements[:5]:  # Limit to first 5 images
            src = img.get('src')
            if src and any(keyword in src.lower() for keyword in ['product', 'equipment', 'tool']):
                images.append(src)
        
        return images
    
    def _analyze_title_patterns(self, titles: List[str]) -> Dict:
        """Analyze patterns in product titles"""
        
        patterns = {
            'common_words': [],
            'average_length': 0,
            'common_structure': []
        }
        
        if not titles:
            return patterns
        
        # Calculate average length
        lengths = [len(title.split()) for title in titles]
        patterns['average_length'] = sum(lengths) // len(lengths) if lengths else 0
        
        # Find common words
        all_words = []
        for title in titles:
            words = [word.lower() for word in title.split()]
            all_words.extend(words)
        
        word_counts = {}
        for word in all_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get most common words (excluding common articles)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', '-'}
        common_words = [
            word for word, count in sorted(word_counts.items(), key=lambda x: x[1], reverse=True) 
            if count > 1 and word not in stop_words and len(word) > 2
        ]
        
        patterns['common_words'] = common_words[:15]
        
        return patterns
    
    def _analyze_description_patterns(self, descriptions: List[str]) -> Dict:
        """Analyze patterns in product descriptions"""
        
        patterns = {
            'common_phrases': [],
            'sentence_starters': [],
            'average_length': 0
        }
        
        if not descriptions:
            return patterns
        
        # Calculate average length
        lengths = [len(desc.split()) for desc in descriptions]
        patterns['average_length'] = sum(lengths) // len(lengths) if lengths else 0
        
        # Find common sentence starters
        starters = []
        for desc in descriptions:
            sentences = desc.split('.')
            for sentence in sentences[:3]:  # First 3 sentences
                sentence = sentence.strip()
                if sentence:
                    words = sentence.split()[:4]  # First 4 words
                    if len(words) >= 2:
                        starters.append(' '.join(words))
        
        starter_counts = {}
        for starter in starters:
            starter_counts[starter] = starter_counts.get(starter, 0) + 1
        
        patterns['sentence_starters'] = [
            starter for starter, count in sorted(starter_counts.items(), key=lambda x: x[1], reverse=True) 
            if count > 1
        ][:10]
        
        return patterns
    
    def _analyze_technical_patterns(self, tech_specs: List[Dict]) -> Dict:
        """Analyze patterns in technical specifications"""
        
        patterns = {
            'common_fields': [],
            'field_frequency': {}
        }
        
        if not tech_specs:
            return patterns
        
        # Count field frequency
        field_counts = {}
        for specs in tech_specs:
            for field in specs.keys():
                field_counts[field] = field_counts.get(field, 0) + 1
        
        # Get most common fields
        patterns['common_fields'] = [
            field for field, count in sorted(field_counts.items(), key=lambda x: x[1], reverse=True) 
            if count > 1
        ]
        patterns['field_frequency'] = field_counts
        
        return patterns
    
    def _create_sample_product_data(self) -> pd.DataFrame:
        """Create sample product data for demonstration"""
        
        sample_data = {
            'stock_number': [
                '01/TEST001', '01/TEST002', '03/DRILL001', '03/DRILL002',
                '12/LAWN001', '12/LAWN002', '13/GEN001', '13/GEN002'
            ],
            'title': [
                'Honda HR194 Petrol Rotary Lawnmower - Self Propelled',
                'Bosch Professional Access Platform - Electric',
                'Hilti TE 2000-AVR Breaking Hammer - SDS Max',
                'Makita HR2470 Rotary Hammer Drill - SDS Plus',
                'Stihl MS250 Chainsaw - Petrol Professional',
                'Honda HRG466 Lawn Mower - Self Propelled Petrol',
                'Honda EU20i Generator - Super Silent Petrol',
                'Hyundai HY2000si Generator - Inverter Petrol'
            ],
            'description': [
                'The Honda HR194 is engineered for professional lawn care...',
                'Professional access platform delivering safe working at height...',
                'Heavy-duty breaking hammer for demolition and construction...',
                'Versatile rotary hammer drill for drilling and chiseling...',
                'Professional chainsaw for tree felling and maintenance...',
                'Reliable self-propelled mower for professional results...',
                'Super silent generator providing clean, stable power...',
                'Compact inverter generator perfect for sensitive equipment...'
            ],
            'brand': ['Honda', 'Bosch', 'Hilti', 'Makita', 'Stihl', 'Honda', 'Honda', 'Hyundai'],
            'model': ['HR194', 'Professional', 'TE 2000-AVR', 'HR2470', 'MS250', 'HRG466', 'EU20i', 'HY2000si'],
            'category': [
                'Garden Equipment', 'Access Equipment', 'Breaking & Drilling', 'Breaking & Drilling',
                'Garden Equipment', 'Garden Equipment', 'Generators', 'Generators'
            ],
            'manufacturer_website': [
                'https://www.honda.co.uk', 'https://www.bosch-professional.com',
                'https://www.hilti.co.uk', 'https://www.makita.co.uk',
                'https://www.stihl.co.uk', 'https://www.honda.co.uk',
                'https://www.honda.co.uk', 'https://www.hyundai.co.uk'
            ],
            'power_type': ['Petrol', 'Electric', 'Electric', 'Electric', 'Petrol', 'Petrol', 'Petrol', 'Petrol'],
            'power_output': ['160cc', '240V', '1900W', '780W', '45.4cc', '160cc', '2000W', '2000W']
        }
        
        return pd.DataFrame(sample_data)
    
    def export_template(self, filename: str = "product_data_template.xlsx"):
        """Export a template Excel file for product data"""
        
        template_data = {
            'stock_number': ['01/EXAMPLE001', '03/EXAMPLE002'],
            'title': ['Example Product Title - Professional Grade', 'Another Example - Heavy Duty'],
            'description': ['Professional description of the product...', 'Another professional description...'],
            'brand': ['Honda', 'Makita'],
            'model': ['Model123', 'Model456'],
            'category': ['Access Equipment', 'Breaking & Drilling'],
            'manufacturer_website': ['https://www.manufacturer.com', 'https://www.anothermanufacturer.com'],
            'power_type': ['Petrol', 'Electric'],
            'power_output': ['160cc', '1200W'],
            'technical_spec_1': ['Specification 1', 'Specification 1'],
            'technical_spec_2': ['Specification 2', 'Specification 2'],
            'notes': ['Additional notes', 'Additional notes']
        }
        
        df = pd.DataFrame(template_data)
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Template exported to {filename}")
        return filename