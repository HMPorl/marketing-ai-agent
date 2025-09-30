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
    def __init__(self, data_folder_path: str = "./data/product_data"):
        self.data_folder_path = data_folder_path
        self.csv_file_path = None
        self.product_data = None
        self.manufacturer_cache = {}
        
        # Automatically find CSV file in data folder
        self._find_csv_file()
        
        # Auto-load data if CSV file is found
        if self.csv_file_path:
            try:
                self.load_product_data()
            except Exception as e:
                print(f"Warning: Could not auto-load product data: {e}")
    
    @property
    def has_data(self) -> bool:
        """Check if product data is loaded"""
        return self.product_data is not None and len(self.product_data) > 0
    
    @property
    def data_summary(self) -> str:
        """Get a summary of loaded data"""
        if not self.has_data:
            return "No product data loaded"
        return f"{len(self.product_data)} products loaded from {os.path.basename(self.csv_file_path) if self.csv_file_path else 'unknown file'}"
        
    def _find_csv_file(self):
        """Automatically find CSV file in the data folder"""
        
        if not os.path.exists(self.data_folder_path):
            os.makedirs(self.data_folder_path, exist_ok=True)
            return
        
        # Look for CSV files in the data folder
        csv_files = [f for f in os.listdir(self.data_folder_path) if f.endswith('.csv')]
        
        if csv_files:
            # Use the first CSV file found (or most recent)
            csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.data_folder_path, x)), reverse=True)
            self.csv_file_path = os.path.join(self.data_folder_path, csv_files[0])
            print(f"Found product CSV file: {csv_files[0]}")
        else:
            print(f"No CSV file found in {self.data_folder_path}. Please add your WordPress export file.")
            self.csv_file_path = None
        
    def load_product_data(self, file_path: str = None) -> pd.DataFrame:
        """Load product data from CSV file"""
        
        if file_path:
            self.csv_file_path = file_path
        elif not self.csv_file_path:
            self._find_csv_file()
        
        if not self.csv_file_path or not os.path.exists(self.csv_file_path):
            print("No CSV file found. Using sample data.")
            return self._create_sample_product_data()
        
        try:
            print(f"Loading product data from: {self.csv_file_path}")
            
            # Read CSV file with WordPress export format
            df = pd.read_csv(self.csv_file_path, encoding='utf-8')
            
            # Handle duplicate columns (common in WordPress exports)
            if df.columns.duplicated().any():
                print("Removing duplicate columns...")
                df = df.loc[:, ~df.columns.duplicated()]
            
            # Handle WordPress CSV format
            self.product_data = self._process_wordpress_csv(df)
            
            print(f"Loaded {len(self.product_data)} products from CSV")
            return self.product_data
            
        except Exception as e:
            logging.error(f"Error loading CSV file: {e}")
            print(f"Error loading CSV: {e}")
            return self._create_sample_product_data()
    
    def get_product_by_code(self, product_code: str) -> Dict:
        """Get specific product by its code"""
        
        if self.product_data is None:
            self.product_data = self.load_product_data()
        
        # Find product with matching stock number
        matching_products = self.product_data[
            self.product_data['stock_number'].str.upper() == product_code.upper()
        ]
        
        if len(matching_products) > 0:
            row = matching_products.iloc[0]
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
                'power_output': row.get('power_output', ''),
                'found': True
            }
            return product
        else:
            # Return empty product with category analysis
            category_info = self.analyze_product_code(product_code)
            return {
                'stock_number': product_code,
                'title': '',
                'description': '',
                'technical_specs': {},
                'brand': '',
                'model': '',
                'category': category_info.get('category', ''),
                'manufacturer_website': '',
                'power_type': '',
                'power_output': '',
                'found': False
            }
    
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
            # Filter out NaN/float values before analysis
            valid_descriptions = [d for d in descriptions if d and isinstance(d, str) and len(d.strip()) > 10]
            if valid_descriptions:
                patterns['description_patterns'] = self._analyze_description_patterns(valid_descriptions)
                patterns['avg_description_length'] = sum(len(d.split()) for d in valid_descriptions) // len(valid_descriptions)
            else:
                patterns['description_patterns'] = {}
                patterns['avg_description_length'] = 0
        else:
            patterns['description_patterns'] = {}
            patterns['avg_description_length'] = 0
        
        # Analyze technical specs
        tech_specs = [p.get('technical_specs', {}) for p in products if p.get('technical_specs')]
        patterns['technical_spec_patterns'] = self._analyze_technical_patterns(tech_specs)
        
        # Analyze manufacturer patterns
        manufacturers = [p.get('manufacturer_website', '') for p in products if p.get('manufacturer_website')]
        patterns['manufacturer_patterns'] = {'common_manufacturers': list(set(manufacturers))}
        
        return patterns
    
    def _process_wordpress_csv(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process WordPress CSV export to standard format"""
        
        print("Processing WordPress CSV format...")
        
        # Handle any remaining duplicate columns more thoroughly
        if df.columns.duplicated().any():
            print("Handling duplicate columns...")
            # Make column names unique by adding suffixes
            cols = pd.Series(df.columns)
            for dup in cols[cols.duplicated()].unique():
                cols[cols[cols == dup].index.values.tolist()] = [dup if i == 0 else f'{dup}_{i}' for i in range(sum(cols == dup))]
            df.columns = cols
        
        # WordPress CSV typically has these columns:
        # - SKU (stock number)
        # - Name/Title 
        # - Description
        # - Meta: technical_specification
        # - Other meta fields
        
        # Map WordPress columns to our standard format
        wordpress_mapping = {
            'SKU': 'stock_number',
            'sku': 'stock_number', 
            'Name': 'title',
            'name': 'title',
            'Title': 'title',
            'Post title': 'title',
            'Description': 'description',
            'description': 'description',
            'Short description': 'description',
            'Content': 'description',
            'Meta: technical_specification': 'technical_specs_raw',
            'meta: technical_specification': 'technical_specs_raw',
            'Technical Specification': 'technical_specs_raw',
            'technical_specification': 'technical_specs_raw',
            'Meta: _technical_specification': 'technical_specs_raw',
            'meta: _technical_specification': 'technical_specs_raw'
        }
        
        # Rename columns based on mapping - but only if they exist and don't create duplicates
        new_df = df.copy()
        for wp_col, standard_col in wordpress_mapping.items():
            if wp_col in new_df.columns and standard_col not in new_df.columns:
                new_df = new_df.rename(columns={wp_col: standard_col})
        
        # Extract additional info from product names/descriptions
        new_df = self._extract_product_details(new_df)
        
        # Process technical specifications
        if 'technical_specs_raw' in new_df.columns:
            new_df['technical_specs'] = new_df['technical_specs_raw'].apply(self._parse_wordpress_tech_specs)
        
        # Ensure required columns exist
        required_columns = [
            'stock_number', 'title', 'description', 'brand', 'model', 
            'category', 'manufacturer_website', 'power_type', 'power_output'
        ]
        
        for col in required_columns:
            if col not in new_df.columns:
                new_df[col] = ''
        
        # Clean and filter data
        new_df = new_df.dropna(subset=['stock_number', 'title'])  # Remove rows without essential data
        new_df = new_df[new_df['stock_number'].astype(str).str.strip() != '']  # Remove empty stock numbers
        
        return new_df
    
    def _extract_product_details(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract brand, model, category from product titles and descriptions"""
        
        # Extract category from stock number (if follows 01/, 03/ format)
        df['category'] = df['stock_number'].apply(self._extract_category_from_sku)
        
        # Extract brand from title (common brands)
        common_brands = [
            'Honda', 'Stihl', 'Makita', 'Bosch', 'Husqvarna', 'DeWalt', 'Hilti', 
            'Karcher', 'JCB', 'Kubota', 'Yanmar', 'Bomag', 'Weber', 'Belle',
            'Wacker', 'Mikasa', 'Altrad', 'Evolution', 'Festool', 'Metabo'
        ]
        
        def extract_brand(title):
            if pd.isna(title):
                return ''
            title_upper = str(title).upper()
            for brand in common_brands:
                if brand.upper() in title_upper:
                    return brand
            return ''
        
        df['brand'] = df['title'].apply(extract_brand)
        
        # Extract model (typically alphanumeric after brand)
        def extract_model(title, brand):
            if pd.isna(title) or not brand:
                return ''
            try:
                title_str = str(title)
                # Look for alphanumeric patterns after brand name
                import re
                pattern = rf'{brand}\s+([A-Z0-9\-]+)'
                match = re.search(pattern, title_str, re.IGNORECASE)
                if match:
                    return match.group(1)
            except:
                pass
            return ''
        
        df['model'] = df.apply(lambda row: extract_model(row.get('title', ''), row.get('brand', '')), axis=1)
        
        # Extract power type from title/description
        def extract_power_type(text):
            if pd.isna(text):
                return ''
            text_lower = str(text).lower()
            if any(word in text_lower for word in ['petrol', 'gasoline', 'gas']):
                return 'Petrol'
            elif any(word in text_lower for word in ['electric', '240v', '110v', 'mains']):
                return 'Electric'
            elif any(word in text_lower for word in ['diesel']):
                return 'Diesel'
            elif any(word in text_lower for word in ['battery', 'cordless']):
                return 'Battery'
            elif any(word in text_lower for word in ['hydraulic']):
                return 'Hydraulic'
            elif any(word in text_lower for word in ['pneumatic', 'air']):
                return 'Pneumatic'
            return ''
        
        df['power_type'] = (df['title'].fillna('') + ' ' + df['description'].fillna('')).apply(extract_power_type)
        
        return df
    
    def _extract_category_from_sku(self, sku):
        """Extract category from SKU using prefix mapping"""
        
        if pd.isna(sku):
            return ''
        
        sku_str = str(sku)
        
        # Category mapping based on codes
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
        
        # Extract prefix (e.g., "01" from "01/ABC123" or "01-ABC123")
        import re
        prefix_match = re.match(r'^(\d{2})[/\-]', sku_str)
        
        if prefix_match:
            prefix = prefix_match.group(1)
            return category_mapping.get(prefix, 'Equipment')
        
        return 'Equipment'
    
    def _parse_wordpress_tech_specs(self, tech_specs_raw):
        """Parse WordPress technical specifications field"""
        
        if pd.isna(tech_specs_raw):
            return {}
        
        specs = {}
        
        try:
            tech_str = str(tech_specs_raw)
            
            # WordPress often stores specs as HTML or delimited text
            # Try to parse different formats
            
            # Format 1: HTML-like format
            if '<' in tech_str and '>' in tech_str:
                # Remove HTML tags and parse
                import re
                tech_str = re.sub(r'<[^>]+>', '\n', tech_str)
            
            # Format 2: Key-value pairs separated by various delimiters
            lines = tech_str.replace('\r', '\n').split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Try different separators
                for separator in [':', '=', '-', '|']:
                    if separator in line:
                        parts = line.split(separator, 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            if key and value and len(key) < 50:  # Reasonable key length
                                specs[key] = value
                        break
        
        except Exception as e:
            logging.error(f"Error parsing tech specs: {e}")
        
        return specs
    
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
        
        # Filter out NaN and empty descriptions
        valid_descriptions = []
        for desc in descriptions:
            if desc and isinstance(desc, str) and len(desc.strip()) > 10:
                valid_descriptions.append(desc.strip())
        
        if not valid_descriptions:
            return patterns
        
        # Calculate average length
        lengths = [len(desc.split()) for desc in valid_descriptions]
        patterns['average_length'] = sum(lengths) // len(lengths) if lengths else 0
        
        # Find common sentence starters
        starters = []
        for desc in valid_descriptions:
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
    
    def get_csv_info(self) -> Dict:
        """Get information about the loaded CSV file"""
        
        from datetime import datetime
        
        info = {
            'csv_file_path': self.csv_file_path,
            'file_exists': False,
            'file_size': 0,
            'last_modified': None,
            'total_products': 0,
            'sample_columns': []
        }
        
        if self.csv_file_path and os.path.exists(self.csv_file_path):
            info['file_exists'] = True
            info['file_size'] = os.path.getsize(self.csv_file_path)
            info['last_modified'] = datetime.fromtimestamp(os.path.getmtime(self.csv_file_path))
            
            if self.product_data is not None:
                info['total_products'] = len(self.product_data)
                info['sample_columns'] = list(self.product_data.columns)[:10]  # First 10 columns
        
        return info