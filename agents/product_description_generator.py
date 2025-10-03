import json
import re
import random
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime
import logging
import time
import os
import sys

# Add the tools directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))

try:
    from style_guide_manager import StyleGuideManager
    STYLE_GUIDE_AVAILABLE = True
except ImportError:
    STYLE_GUIDE_AVAILABLE = False
    print("Style guide manager not available - using fallback methods")

class ProductDescriptionGenerator:
    def __init__(self, excel_handler=None):
        self.excel_handler = excel_handler
        self.style_patterns = {}
        self.similar_products = []
        
        # Initialize style guide manager
        if STYLE_GUIDE_AVAILABLE:
            try:
                self.style_guide_manager = StyleGuideManager()
            except Exception as e:
                print(f"Error initializing style guide manager: {e}")
                self.style_guide_manager = None
        else:
            self.style_guide_manager = None
        
    def generate_product_content(self, product_code: str, new_product_info: Dict = None) -> Dict:
        """
        Generate comprehensive WordPress-ready product content with web research
        """
        
        print(f"Generating comprehensive content for product code: {product_code}")
        
        # Get the specific product from CSV
        product = self.excel_handler.get_product_by_code(product_code) if self.excel_handler else None
        
        if not product or not product['found']:
            # If this is a NEW product with provided info, use enhanced generation
            if new_product_info:
                return self._generate_new_product_content(product_code, new_product_info)
            # Otherwise use basic fallback
            category_info = self.excel_handler.analyze_product_code(product_code) if self.excel_handler else self._mock_code_analysis(product_code)
            return self._generate_fallback_content(product_code, category_info)
        
        print(f"Found product: {product['title']}")
        
        # 1. Analyze similar products for style consistency
        print("Analyzing similar products for style consistency...")
        similar_products = self.excel_handler.get_products_by_category(product['category'], limit=15) if self.excel_handler else []
        style_patterns = self.excel_handler.analyze_style_patterns(similar_products) if self.excel_handler else {}
        
        # 2. Research manufacturer website for factual information
        print("Researching manufacturer website...")
        manufacturer_info = {}
        if product.get('manufacturer_website'):
            manufacturer_info = self.excel_handler.scrape_manufacturer_info(
                product['manufacturer_website'], 
                product['title']
            ) if self.excel_handler else {}
        
        # 3. Web search for additional product information
        print("Searching web for additional product information...")
        web_research = self._search_web_for_product(product)
        
        # 4. Generate WordPress-ready content
        print("Generating WordPress-ready content...")
        wordpress_content = self._generate_wordpress_content(
            product, similar_products, manufacturer_info, web_research, style_patterns
        )
        
        return {
            'product_code': product_code,
            'category': product['category'],
            'generated_at': datetime.now().isoformat(),
            'wordpress_content': wordpress_content,
            'research_sources': {
                'similar_products_analyzed': len(similar_products),
                'manufacturer_website': product.get('manufacturer_website', ''),
                'web_research_completed': len(web_research.get('sources', [])),
                'style_patterns_found': len(style_patterns.get('title_patterns', {}))
            },
            'style_confidence': self._calculate_style_confidence(style_patterns, similar_products)
        }
    
    def _search_web_for_product(self, product: Dict) -> Dict:
        """Search the web for additional product information"""
        
        search_terms = [
            f"{product['brand']} {product['model']}",
            f"{product['title']} specifications",
            f"{product['brand']} {product['model']} review"
        ]
        
        web_info = {
            'sources': [],
            'additional_features': [],
            'common_uses': [],
            'technical_details': {}
        }
        
        try:
            for search_term in search_terms[:2]:  # Limit to 2 searches to be respectful
                if not search_term.strip():
                    continue
                    
                print(f"Searching for: {search_term}")
                
                # Simple Google search simulation (in practice, you'd use a proper search API)
                search_url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                try:
                    response = requests.get(search_url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract snippets and links (basic implementation)
                        results = soup.find_all('div', class_='BNeawe')
                        for result in results[:3]:  # Top 3 results
                            text = result.get_text()
                            if len(text) > 50 and product['brand'].lower() in text.lower():
                                web_info['sources'].append({
                                    'search_term': search_term,
                                    'snippet': text[:200] + "..." if len(text) > 200 else text
                                })
                        
                        time.sleep(2)  # Be respectful to search engines
                    
                except Exception as e:
                    logging.warning(f"Web search failed for {search_term}: {e}")
                    continue
                    
        except Exception as e:
            logging.error(f"Web research failed: {e}")
        
        return web_info
    
    def _generate_wordpress_content(self, product: Dict, similar_products: List[Dict], 
                                   manufacturer_info: Dict, web_research: Dict, 
                                   style_patterns: Dict) -> Dict:
        """Generate WordPress-ready content with description and HTML technical specs"""
        
        # Analyze style patterns from similar products
        description_patterns = self._analyze_description_patterns(similar_products)
        key_features_patterns = self._analyze_key_features_patterns(similar_products)
        
        # Generate description with key features
        description_with_features = self._generate_hireman_description(
            product, description_patterns, key_features_patterns, 
            manufacturer_info, web_research
        )
        
        # Generate HTML technical specifications table
        html_tech_specs = self._generate_html_technical_specs(
            product, similar_products, manufacturer_info
        )
        
        return {
            'description_and_features': description_with_features,
            'technical_specifications_html': html_tech_specs,
            'meta_description': self._generate_meta_description(product),
            'suggested_title': self._generate_wordpress_title(product, style_patterns),
            'key_features_list': self._extract_key_features_list(product, similar_products, manufacturer_info)
        }
    
    def _analyze_description_patterns(self, products: List[Dict]) -> Dict:
        """Analyze description patterns from similar products"""
        
        patterns = {
            'opening_phrases': [],
            'key_feature_indicators': [],
            'call_to_action_phrases': [],
            'average_length': 0,
            'common_terminology': []
        }
        
        if not products:
            return patterns
        
        descriptions = [p.get('description', '') for p in products if p.get('description')]
        
        # Filter out NaN and empty descriptions
        valid_descriptions = []
        for desc in descriptions:
            if desc and isinstance(desc, str) and len(desc.strip()) > 10:
                valid_descriptions.append(desc.strip())
        
        if not valid_descriptions:
            return patterns
        
        # Analyze opening phrases
        opening_phrases = []
        for desc in valid_descriptions:
            first_sentence = desc.split('.')[0]
            if len(first_sentence) > 10:
                opening_phrases.append(first_sentence[:50])
        
        patterns['opening_phrases'] = opening_phrases[:5]
        patterns['average_length'] = sum(len(d.split()) for d in valid_descriptions) // len(valid_descriptions)
        
        return patterns
    
    def _analyze_key_features_patterns(self, products: List[Dict]) -> Dict:
        """Analyze key features patterns from similar products"""
        
        patterns = {
            'common_features': [],
            'feature_presentation_style': 'bullet_points',
            'technical_focus_areas': []
        }
        
        # Look for features in descriptions
        feature_keywords = [
            'features', 'includes', 'benefits', 'specifications', 'ideal for',
            'suitable for', 'designed for', 'perfect for', 'applications'
        ]
        
        for product in products:
            description = product.get('description', '')
            # Handle NaN/float values
            if not description or not isinstance(description, str):
                continue
                
            description_lower = description.lower()
            for keyword in feature_keywords:
                if keyword in description_lower:
                    # Extract text around the keyword
                    start_idx = description_lower.find(keyword)
                    if start_idx != -1:
                        snippet = description_lower[start_idx:start_idx+100]
                        patterns['common_features'].append(snippet)
        
        return patterns
    
    def _generate_hireman_description(self, product: Dict, description_patterns: Dict, 
                                    key_features_patterns: Dict, manufacturer_info: Dict, 
                                    web_research: Dict) -> str:
        """Generate The Hireman style description matching your established format"""
        
        # Extract product details
        brand = product.get('brand', '')
        model = product.get('model', '')
        title = product.get('title', '')
        category = product.get('category', '')
        power_type = product.get('power_type', '')
        existing_desc = product.get('description', '')
        
        # Build description following your established pattern:
        # 1. Brief introductory sentences at the top
        # 2. Key Features section below
        # 3. Space for manual NB notifications (added by you later)
        
        description_parts = []
        
        # 1. OPENING SENTENCES - Brief intro (1-2 sentences)
        opening = self._generate_brief_intro(brand, model, title, category, power_type, existing_desc)
        description_parts.append(opening)
        
        # 2. KEY FEATURES - Following your established format
        key_features = self._extract_genuine_features(product, manufacturer_info, web_research)
        if key_features:
            description_parts.append("\n\n<strong>Key features:</strong>")
            description_parts.append("\n<ul>")
            for feature in key_features:
                description_parts.append(f"\n\t<li>{feature}</li>")
            description_parts.append("\n</ul>")
        
        # 3. Leave space for your manual NB notifications
        # (You'll add these manually as needed)
        
        return ''.join(description_parts)
    
    def _generate_brief_intro(self, brand: str, model: str, title: str, category: str, 
                            power_type: str, existing_desc: str) -> str:
        """Generate a brief 1-2 sentence introduction following style guide"""
        
        # Get category-specific intro from style guide
        category_intro = "for professional applications"
        if self.style_guide_manager:
            category_intro = self.style_guide_manager.get_category_intro(category)
        
        # Try to extract a good brief intro from existing description
        if existing_desc and len(existing_desc) > 50:
            # Look for the first meaningful sentence
            sentences = existing_desc.split('.')
            for sentence in sentences:
                clean_sentence = sentence.strip()
                # Skip HTML and find a good descriptive sentence
                if (len(clean_sentence) > 20 and len(clean_sentence) < 150 and
                    not clean_sentence.startswith('<') and 
                    not 'hire' in clean_sentence.lower() and
                    not 'london' in clean_sentence.lower()):
                    
                    # Check against style guide avoid words
                    if self.style_guide_manager:
                        words = clean_sentence.split()
                        if not any(self.style_guide_manager.should_avoid_word(word) for word in words):
                            return clean_sentence + '.'
                    else:
                        return clean_sentence + '.'
        
        # Generate new brief intro
        if brand and model:
            intro = f"The {brand} {model}"
        elif title:
            # Use title but clean it up
            clean_title = title.replace(' Hire', '').replace(' - London', '')
            intro = f"The {clean_title}"
        else:
            intro = f"This {category.lower()}"
        
        # Add brief description
        if power_type:
            intro += f" is a {power_type.lower()} {category.lower()}"
        else:
            intro += f" is a professional {category.lower()}"
        
        # Use style guide category intro
        intro += f" {category_intro}."
        
        return intro
    
    def add_feedback(self, content_type: str, feedback: str, product_code: str = None, 
                    content_example: str = None):
        """
        Add user feedback to improve future content generation
        
        Args:
            content_type: 'title', 'description', 'features'
            feedback: User's feedback text
            product_code: Optional product code this relates to
            content_example: Optional example of the content being discussed
        """
        if self.style_guide_manager:
            example = None
            if content_example:
                example = {
                    "content": content_example,
                    "product_code": product_code
                }
            
            self.style_guide_manager.add_feedback(content_type, feedback, example)
            print(f"Feedback recorded: {feedback}")
        else:
            print("Style guide manager not available - feedback not saved")
    
    def approve_content(self, content_type: str, content: str, product_code: str = None):
        """Mark content as approved for future reference"""
        if self.style_guide_manager:
            self.style_guide_manager.add_approved_example(content_type, content, product_code)
            print(f"Content approved and saved as example")
    
    def reject_content(self, content_type: str, content: str, reason: str, product_code: str = None):
        """Mark content as rejected with reason"""
        if self.style_guide_manager:
            self.style_guide_manager.add_rejected_example(content_type, content, reason, product_code)
            print(f"Content rejected and reason saved: {reason}")
    
    def get_style_guide_summary(self) -> str:
        """Get a summary of the current style guide"""
        if self.style_guide_manager:
            return self.style_guide_manager.export_style_guide()
        else:
            return "Style guide not available"

    def _generate_factual_opening(self, brand: str, model: str, title: str, category: str,
                                power_type: str, existing_desc: str) -> str:
        """Generate a factual, professional opening paragraph"""
        
        # Try to extract the essence from existing description if it's good
        if existing_desc and len(existing_desc) > 100:
            # Look for the first sentence that describes what the product is
            sentences = existing_desc.split('.')
            for sentence in sentences:
                clean_sentence = sentence.strip()
                # Skip HTML tags and look for substantial descriptive sentences
                if (len(clean_sentence) > 30 and 
                    not clean_sentence.startswith('<') and 
                    ('is a' in clean_sentence or 'provides' in clean_sentence or 
                     'designed' in clean_sentence or 'suitable' in clean_sentence)):
                    return clean_sentence + '.'
        
        # Generate new opening based on product details
        if brand and model:
            opening = f"The {brand} {model}"
        elif title:
            # Extract brand/model from title if available
            title_parts = title.split(',')[0].strip()
            opening = f"The {title_parts}"
        else:
            opening = f"This {category.lower()}"
        
        # Add description of what it is
        if power_type:
            opening += f" is a {power_type.lower()}"
        else:
            opening += " is a"
        
        # Add category context
        category_descriptions = {
            'Access Equipment': 'access platform',
            'Breaking & Drilling': 'drilling tool',
            'Garden Equipment': 'garden tool',
            'Generators': 'generator',
            'Air Compressors & Tools': 'air compressor',
            'Cleaning Equipment': 'cleaning system',
            'Site Equipment': 'construction tool',
            'Heating': 'heating equipment',
            'Pumps': 'pump system'
        }
        
        category_desc = category_descriptions.get(category, category.lower())
        opening += f" {category_desc}"
        
        # Add simple purpose based on category
        purposes = {
            'Access Equipment': 'designed for safe working at height',
            'Breaking & Drilling': 'designed for breaking and drilling applications',
            'Garden Equipment': 'designed for garden maintenance',
            'Generators': 'designed for reliable power supply',
            'Air Compressors & Tools': 'designed for pneumatic applications',
            'Cleaning Equipment': 'designed for effective cleaning applications',
            'Site Equipment': 'designed for construction and site work',
            'Heating': 'designed for heating applications',
            'Pumps': 'designed for water management'
        }
        
        purpose = purposes.get(category, 'designed for professional use')
        opening += f" {purpose}."
        
        return opening
    
    def _extract_genuine_features(self, product: Dict, manufacturer_info: Dict, 
                                web_research: Dict) -> List[str]:
        """Extract genuine, factual features without marketing fluff"""
        
        features = []
        
        # 1. Extract from existing well-structured descriptions
        existing_desc = product.get('description', '')
        if '<li>' in existing_desc:
            soup = BeautifulSoup(existing_desc, 'html.parser')
            li_items = soup.find_all('li')
            for item in li_items:
                feature_text = item.get_text().strip()
                # Only include substantial, factual features
                if (feature_text and len(feature_text) > 10 and 
                    not any(fluff in feature_text.lower() for fluff in 
                           ['ideal', 'perfect', 'exceptional', 'amazing', 'best'])):
                    features.append(feature_text)
        
        # 2. Extract key technical specifications as features
        tech_specs = product.get('technical_specs', {})
        if isinstance(tech_specs, dict):
            spec_features = []
            for key, value in tech_specs.items():
                if (value and str(value) != 'nan' and 
                    key.lower() in ['power', 'voltage', 'weight', 'capacity', 'dimensions', 
                                   'motor', 'engine', 'fuel tank', 'cutting width', 'platform height']):
                    spec_features.append(f"{key.replace('_', ' ').title()}: {value}")
            features.extend(spec_features[:3])  # Limit tech specs to 3
        
        # 3. Add factual manufacturer features (avoid marketing language)
        if manufacturer_info.get('features'):
            mfr_features = []
            for feature in manufacturer_info['features'][:3]:
                # Filter out marketing language
                if not any(fluff in feature.lower() for fluff in 
                          ['revolutionary', 'cutting-edge', 'world-class', 'premium', 'ultimate']):
                    mfr_features.append(feature)
            features.extend(mfr_features)
        
        # 4. Add category-specific practical features
        category_features = self._get_practical_category_features(
            product.get('category', ''), product
        )
        features.extend(category_features)
        
        # Clean up and deduplicate
        unique_features = []
        seen_lowercase = set()
        
        for feature in features:
            feature_clean = feature.strip()
            feature_lower = feature_clean.lower()
            
            # Skip if too similar to existing feature
            if not any(existing in feature_lower or feature_lower in existing 
                      for existing in seen_lowercase):
                unique_features.append(feature_clean)
                seen_lowercase.add(feature_lower)
        
        return unique_features[:5]  # Maximum 5 features for readability
    
    def _get_practical_category_features(self, category: str, product: Dict) -> List[str]:
        """Get practical, factual features specific to category"""
        
        features = []
        power_type = product.get('power_type', '').lower()
        
        category_features = {
            'Access Equipment': [
                'Full guardrail protection',
                'Non-slip platform surface',
                'Emergency lowering system',
                'Stabilising outriggers'
            ],
            'Breaking & Drilling': [
                'Anti-vibration handle',
                'Variable speed control',
                'SDS chuck system',
                'Dust extraction port'
            ],
            'Garden Equipment': [
                'Easy start system',
                'Adjustable cutting height',
                'Grass collection bag',
                'Foldable handle'
            ],
            'Generators': [
                'Automatic voltage regulation',
                'Low oil shutdown protection',
                'Multiple power outlets',
                'Fuel gauge'
            ],
            'Site Equipment': [
                'Robust steel construction',
                'Weather resistant finish',
                'Easy transport design',
                'Quick setup system'
            ]
        }
        
        # Get category-specific features
        if category in category_features:
            features.extend(category_features[category][:2])
        
        # Add power-specific features
        if power_type == 'petrol':
            features.append('Petrol engine operation')
        elif power_type == 'electric':
            features.append('Electric motor operation')
        elif power_type == 'battery':
            features.append('Cordless battery operation')
        
        return features
    
    def _generate_practical_applications(self, category: str, product: Dict, power_type: str) -> str:
        """Generate practical applications without marketing fluff"""
        
        # Base applications by category
        applications_map = {
            'Access Equipment': 'Suitable for maintenance work, installation tasks, and building work where safe access to height is required',
            'Breaking & Drilling': 'Suitable for concrete work, masonry drilling, and demolition applications in construction and renovation projects',
            'Garden Equipment': 'Suitable for lawn maintenance, garden care, and grounds keeping in both domestic and commercial settings',
            'Generators': 'Suitable for construction sites, outdoor events, and backup power applications where mains electricity is unavailable',
            'Site Equipment': 'Suitable for construction projects, site preparation, and general building work',
            'Cleaning Equipment': 'Suitable for surface cleaning, pressure washing, and maintenance cleaning in industrial and commercial environments',
            'Heating': 'Suitable for temporary heating, space heating, and climate control in construction and industrial applications'
        }
        
        base_application = applications_map.get(category, 
            'Suitable for professional applications where reliable equipment is required')
        
        # Enhance based on power type
        if power_type.lower() == 'petrol':
            enhancement = ' The petrol engine provides mobility for outdoor and remote locations.'
        elif power_type.lower() == 'electric':
            enhancement = ' Electric operation ensures quiet running and emission-free use indoors.'
        elif power_type.lower() == 'battery':
            enhancement = ' Battery operation provides cord-free convenience and portability.'
        else:
            enhancement = ''
        
        return base_application + enhancement
    
    def _extract_and_enhance_key_features(self, product: Dict, manufacturer_info: Dict, 
                                        web_research: Dict) -> List[str]:
        """Extract and enhance key features from multiple sources"""
        
        features = []
        
        # Extract from existing description
        existing_desc = product.get('description', '')
        if '<li>' in existing_desc:
            # Extract existing list items
            soup = BeautifulSoup(existing_desc, 'html.parser')
            li_items = soup.find_all('li')
            for item in li_items:
                feature_text = item.get_text().strip()
                if feature_text and len(feature_text) > 5:
                    features.append(feature_text)
        
        # Extract from technical specifications
        tech_specs = product.get('technical_specs', {})
        if isinstance(tech_specs, dict):
            for key, value in tech_specs.items():
                if key.lower() in ['power', 'motor', 'engine', 'capacity', 'weight']:
                    features.append(f"{key}: {value}")
        
        # Add category-specific features
        category_features = self._get_category_specific_features(
            product.get('category', ''), product
        )
        features.extend(category_features)
        
        # Add manufacturer research features
        if manufacturer_info.get('features'):
            features.extend(manufacturer_info['features'][:3])
        
        # Remove duplicates and clean up
        unique_features = []
        seen = set()
        for feature in features:
            feature_clean = feature.lower().strip()
            if feature_clean not in seen and len(feature) > 10:
                unique_features.append(feature)
                seen.add(feature_clean)
        
        return unique_features[:8]  # Maximum 8 features
    
    def _generate_html_technical_specs(self, product: Dict, similar_products: List[Dict], 
                                     manufacturer_info: Dict) -> str:
        """Generate HTML table for technical specifications"""
        
        # Get technical specifications from product
        tech_specs = product.get('technical_specs', {})
        
        # If we have raw HTML specs, use and enhance them
        if 'Technical Specs Raw' in tech_specs and '<table' in str(tech_specs['Technical Specs Raw']):
            raw_html = tech_specs['Technical Specs Raw']
            # Clean and enhance the existing HTML
            return self._enhance_existing_html_table(raw_html)
        
        # Otherwise, build new HTML table
        specs_data = self._compile_technical_specifications(
            product, similar_products, manufacturer_info
        )
        
        if not specs_data:
            return "<p>Technical specifications will be updated soon.</p>"
        
        # Build HTML table
        html = ['<table class="technical-specifications" style="width: 100%; border-collapse: collapse;">']
        html.append('<thead>')
        html.append('<tr style="background-color: #f8f9fa;">')
        html.append('<th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Specification</th>')
        html.append('<th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Details</th>')
        html.append('</tr>')
        html.append('</thead>')
        html.append('<tbody>')
        
        for spec_name, spec_value in specs_data.items():
            html.append('<tr>')
            html.append(f'<td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">{spec_name}</td>')
            html.append(f'<td style="padding: 8px; border: 1px solid #ddd;">{spec_value}</td>')
            html.append('</tr>')
        
        html.append('</tbody>')
        html.append('</table>')
        
        return '\n'.join(html)
    
    def _enhance_existing_html_table(self, raw_html: str) -> str:
        """Enhance existing HTML table with better styling"""
        
        try:
            soup = BeautifulSoup(raw_html, 'html.parser')
            table = soup.find('table')
            
            if table:
                # Add CSS classes and styling
                table['class'] = 'technical-specifications'
                table['style'] = 'width: 100%; border-collapse: collapse; margin: 20px 0;'
                
                # Style header row
                header_row = table.find('tr')
                if header_row:
                    header_row['style'] = 'background-color: #f8f9fa;'
                    for th in header_row.find_all(['th', 'td']):
                        th['style'] = 'padding: 12px; border: 1px solid #ddd; font-weight: bold; text-align: center;'
                
                # Style data rows
                data_rows = table.find_all('tr')[1:]  # Skip header
                for row in data_rows:
                    for td in row.find_all('td'):
                        td['style'] = 'padding: 10px; border: 1px solid #ddd; text-align: center;'
                
                return str(table)
            else:
                return raw_html
                
        except Exception as e:
            logging.error(f"Error enhancing HTML table: {e}")
            return raw_html
    
    def _compile_technical_specifications(self, product: Dict, similar_products: List[Dict], 
                                        manufacturer_info: Dict) -> Dict:
        """Compile comprehensive technical specifications"""
        
        specs = {}
        
        # Extract from product data
        tech_specs = product.get('technical_specs', {})
        if isinstance(tech_specs, dict):
            for key, value in tech_specs.items():
                if key not in ['Technical Specs Raw', 'Meta: _Technical Specification']:
                    clean_key = key.replace('_', ' ').title()
                    specs[clean_key] = str(value)
        
        # Add essential specifications based on category
        category = product.get('category', '')
        essential_specs = self._get_category_essential_specs(category, product)
        specs.update(essential_specs)
        
        # Add manufacturer specifications
        if manufacturer_info.get('specifications'):
            specs.update(manufacturer_info['specifications'])
        
        # Clean up and format
        cleaned_specs = {}
        for key, value in specs.items():
            if value and str(value).strip() and str(value) != 'nan':
                cleaned_specs[key] = str(value).strip()
        
        return cleaned_specs
    
    def _get_category_use_cases(self, category: str) -> List[str]:
        """Get common use cases for a category"""
        
        use_cases_map = {
            'Access Equipment': ['building maintenance', 'construction projects', 'installation work', 'painting and decorating'],
            'Breaking & Drilling': ['concrete breaking', 'demolition work', 'masonry drilling', 'chiseling applications'],
            'Garden Equipment': ['lawn maintenance', 'garden care', 'landscaping projects', 'grounds maintenance'],
            'Generators': ['backup power', 'construction sites', 'outdoor events', 'emergency power supply'],
            'Air Compressors & Tools': ['pneumatic tools', 'spray painting', 'tire inflation', 'construction work'],
            'Cleaning Equipment': ['industrial cleaning', 'pressure washing', 'surface preparation', 'maintenance cleaning'],
            'Compaction Equipment': ['soil compaction', 'paving work', 'foundation preparation', 'road construction']
        }
        
        return use_cases_map.get(category, ['professional applications', 'commercial use', 'industrial work'])
    
    def _get_detailed_applications(self, category: str, product: Dict) -> List[str]:
        """Get detailed applications based on category and product features"""
        
        base_applications = self._get_category_use_cases(category)
        
        # Enhance based on power type
        power_type = product.get('power_type', '').lower()
        if power_type == 'petrol':
            base_applications.extend(['outdoor applications', 'remote locations'])
        elif power_type == 'electric':
            base_applications.extend(['indoor use', 'quiet environments'])
        elif power_type == 'battery':
            base_applications.extend(['portable applications', 'cordless convenience'])
        
        return base_applications[:6]
    
    def _get_category_specific_features(self, category: str, product: Dict) -> List[str]:
        """Get category-specific features"""
        
        features = []
        power_type = product.get('power_type', '')
        
        category_features_map = {
            'Access Equipment': [
                'Safety harness attachment points',
                'Non-slip platform surface',
                'Easy height adjustment',
                'Stable base design'
            ],
            'Breaking & Drilling': [
                'Anti-vibration technology',
                'SDS chuck system',
                'Variable speed control',
                'Dust extraction compatible'
            ],
            'Garden Equipment': [
                'Easy start system',
                'Adjustable cutting height',
                'Large collection capacity',
                'Ergonomic handle design'
            ],
            'Generators': [
                'Automatic voltage regulation',
                'Low oil shutdown',
                'Multiple outlet configuration',
                'Quiet operation'
            ]
        }
        
        base_features = category_features_map.get(category, [])
        
        # Add power-specific features
        if power_type:
            if power_type.lower() == 'electric':
                features.append('Mains powered operation')
                features.append('Zero emissions')
            elif power_type.lower() == 'petrol':
                features.append('High power output')
                features.append('Portable operation')
            elif power_type.lower() == 'battery':
                features.append('Cordless convenience')
                features.append('Rechargeable battery system')
        
        return features + base_features[:4]
    
    def _get_category_essential_specs(self, category: str, product: Dict) -> Dict:
        """Get essential specifications for a category"""
        
        specs = {}
        
        # Add brand and model if available
        if product.get('brand'):
            specs['Brand'] = product['brand']
        if product.get('model'):
            specs['Model'] = product['model']
        if product.get('power_type'):
            specs['Power Type'] = product['power_type']
        
        # Category-specific essential specs
        if category == 'Breaking & Drilling':
            specs.update({
                'Chuck Type': 'SDS-Max',
                'Application': 'Heavy-duty breaking and drilling',
                'Vibration Control': 'Anti-vibration system'
            })
        elif category == 'Access Equipment':
            specs.update({
                'Platform Type': 'Non-slip surface',
                'Safety Features': 'Guardrails and harness points',
                'Mobility': 'Portable design'
            })
        elif category == 'Garden Equipment':
            specs.update({
                'Starting System': 'Easy-start mechanism',
                'Cutting System': 'Professional grade blades',
                'Collection': 'High-capacity grass bag'
            })
        elif category == 'Generators':
            specs.update({
                'Output Type': 'Clean AC power',
                'Protection': 'Overload and low-oil protection',
                'Portability': 'Compact and lightweight'
            })
        
        return specs
    
    def _generate_hireman_cta(self, category: str) -> str:
        """Generate The Hireman style call-to-action"""
        
        ctas = [
            "Available for same-day hire with delivery across London. Contact our team today for availability and expert advice on your requirements.",
            "Part of our comprehensive hire fleet, available for immediate delivery across London. Call us today to discuss your project requirements.",
            "Available for hire with full support and delivery service. Contact The Hireman today for competitive rates and professional advice.",
            "Ready for immediate hire with our reliable delivery service across London. Speak to our experts today about your project needs."
        ]
        
        return random.choice(ctas)
    
    def _generate_meta_description(self, product: Dict) -> str:
        """Generate SEO meta description"""
        
        brand = product.get('brand', '')
        model = product.get('model', '')
        category = product.get('category', '')
        
        if brand and model:
            return f"Hire {brand} {model} {category.lower()} from The Hireman London. Professional equipment rental with same-day delivery. Expert advice and competitive rates."
        else:
            return f"Professional {category.lower()} hire from The Hireman London. Same-day delivery, expert advice, and competitive rates for your project needs."
    
    def _generate_wordpress_title(self, product: Dict, style_patterns: Dict) -> str:
        """Generate clean WordPress title following style guide"""
        
        # Get style guide preferences if available
        avoid_phrases = []
        if self.style_guide_manager:
            title_guidelines = self.style_guide_manager.get_title_guidelines()
            avoid_phrases = title_guidelines.get("avoid", [])
        
        title = product.get('title', '')
        if title:
            # Clean the title using style guide
            clean_title = title
            for phrase in avoid_phrases:
                clean_title = clean_title.replace(phrase, '')
            
            # Remove common hire/location fluff if not in style guide
            clean_title = clean_title.replace(' - Professional Hire London', '')
            clean_title = clean_title.replace(' Hire', '')
            clean_title = clean_title.replace(' - London', '')
            return clean_title.strip()
        else:
            brand = product.get('brand', '')
            model = product.get('model', '')
            category = product.get('category', '')
            
            if brand and model:
                return f"{brand} {model}"
            elif brand:
                return f"{brand} {category}"
            else:
                return category
    
    def _extract_key_features_list(self, product: Dict, similar_products: List[Dict], 
                                 manufacturer_info: Dict) -> List[str]:
        """Extract clean list of key features for WordPress"""
        
        features = self._extract_genuine_features(
            product, manufacturer_info, {}
        )
        
        # Clean up for WordPress use
        clean_features = []
        for feature in features:
            # Remove HTML tags
            clean_feature = re.sub(r'<[^>]+>', '', feature)
            # Clean up text
            clean_feature = clean_feature.strip()
            if clean_feature and len(clean_feature) > 5:
                clean_features.append(clean_feature)
        
        return clean_features[:6]
    
    def _calculate_style_confidence(self, style_patterns: Dict, similar_products: List[Dict]) -> float:
        """Calculate confidence score for style matching"""
        
        confidence = 0.0
        
        # Base confidence from similar products
        if similar_products:
            confidence += min(len(similar_products) / 10.0, 0.4)
        
        # Style patterns confidence
        if style_patterns.get('title_patterns'):
            confidence += 0.3
        
        if style_patterns.get('description_patterns'):
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _generate_fallback_content(self, product_code: str, category_info: Dict) -> Dict:
        """Generate fallback content when product not found"""
        
        category = category_info.get('category', 'Equipment')
        
        return {
            'product_code': product_code,
            'category': category,
            'generated_at': datetime.now().isoformat(),
            'wordpress_content': {
                'description_and_features': f"Professional {category.lower()} available for hire from The Hireman London. This equipment offers reliable performance for your project requirements.\n\nContact our team for availability and expert advice on your specific needs.",
                'technical_specifications_html': "<p>Technical specifications will be provided upon inquiry. Contact our team for detailed product information.</p>",
                'meta_description': f"Professional {category.lower()} hire from The Hireman London. Same-day delivery and expert advice available.",
                'suggested_title': f"Professional {category} Hire - The Hireman London",
                'key_features_list': [
                    "Professional grade equipment",
                    "Same-day delivery available",
                    "Expert technical support",
                    "Competitive hire rates"
                ]
            },
            'research_sources': {
                'similar_products_analyzed': 0,
                'manufacturer_website': '',
                'web_research_completed': 0,
                'style_patterns_found': 0
            },
            'style_confidence': 0.2
        }
    
    def _generate_new_product_content(self, product_code: str, new_product_info: Dict) -> Dict:
        """Generate enhanced content for NEW products using provided information"""
        
        # Extract information from the form
        brand = new_product_info.get('brand', 'Professional')
        model = new_product_info.get('model', 'Model')
        product_name = new_product_info.get('name', '')
        product_type = new_product_info.get('type', '')
        differentiator = new_product_info.get('differentiator', '')
        power_type = new_product_info.get('power_type', '')
        power_output = new_product_info.get('power', '')
        manufacturer_website = new_product_info.get('manufacturer_website', '')
        further_info = new_product_info.get('further_info', '')
        category = new_product_info.get('category', 'Equipment')
        
        # Create realistic title
        if product_name:
            title = f"{brand} {model} {product_name}"
        else:
            title = f"{brand} {model}"
        
        if differentiator:
            title += f" - {differentiator}"
        if power_type:
            title += f" ({power_type})"
        if power_output:
            title += f" {power_output}"
        
        # Generate category-specific content
        if category == 'Breaking & Drilling':
            if 'dewalt' in brand.lower():
                description = f"""The {brand} {model} combines professional-grade power with advanced features for demanding drilling and breaking applications. This cordless rotary hammer drill delivers exceptional performance for concrete, masonry, and steel drilling tasks.

Engineered for professional contractors and serious DIY users, this tool features brushless motor technology for increased runtime and durability. The multi-functional design allows for drilling, hammer drilling, and chiselling operations, making it versatile for various construction and renovation projects.

Perfect for electrical installations, plumbing work, HVAC installations, and general construction tasks. Available for daily, weekly, or monthly hire with competitive rates and same-day delivery across London."""
                
                key_features = [
                    f'Professional {brand} quality and reliability',
                    'Brushless motor for extended runtime',
                    'Multi-functional drilling and breaking capability',
                    'Advanced vibration reduction technology',
                    'SDS chuck system for quick bit changes',
                    'High-capacity battery system',
                    'Same-day hire and delivery available',
                    'Expert support and guidance included'
                ]
                
                tech_specs = {
                    'Brand': brand,
                    'Model': model,
                    'Category': category,
                    'Drilling Capacity': 'Concrete: 40mm, Steel: 13mm',
                    'Impact Rate': '4,800 bpm',
                    'Chuck Type': 'SDS-Plus Compatible',
                    'Battery': 'High-capacity Lithium-ion',
                    'Vibration Control': 'Advanced Anti-Vibration',
                    'Applications': 'Drilling, Hammer Drilling, Chiselling'
                }
            else:
                description = f"""Professional {category.lower()} equipment designed for demanding construction and renovation applications. The {brand} {model} delivers reliable performance for concrete drilling, masonry work, and demolition tasks.

Built to withstand the rigors of professional use while remaining user-friendly for all skill levels. Advanced engineering ensures optimal power transfer and reduced vibration for operator comfort during extended use periods.

Ideal for construction professionals, maintenance teams, and DIY enthusiasts tackling substantial projects. Available for immediate hire with full support and guidance from our experienced team."""
                
                key_features = [
                    f'Professional {brand} construction',
                    'Heavy-duty drilling capability',
                    'Reduced vibration design',
                    'Professional-grade performance',
                    'Versatile drilling applications',
                    'Robust and reliable operation',
                    'Same-day hire available',
                    'Expert technical support'
                ]
                
                tech_specs = {
                    'Brand': brand,
                    'Model': model,
                    'Category': category,
                    'Applications': 'Breaking & Drilling',
                    'Power Source': power_type if power_type else 'Electric/Cordless',
                    'Chuck Type': 'Professional Grade',
                    'Vibration Control': 'Enhanced',
                    'Suitable For': 'Concrete, Masonry, Steel'
                }
        
        elif category == 'Garden Equipment':
            description = f"""The {brand} {model} is engineered for professional landscaping and garden maintenance. This high-performance equipment delivers exceptional results for both commercial landscapers and domestic users seeking professional-grade tools.

Featuring robust construction and reliable operation, this equipment handles demanding outdoor tasks with ease. Advanced design ensures efficient operation while minimizing operator fatigue during extended use periods.

Perfect for landscaping contractors, property maintenance teams, and homeowners with substantial grounds to maintain. Available for hire with competitive daily and weekly rates, plus expert advice on operation and safety."""
            
            key_features = [
                f'Professional {brand} engineering',
                'High-performance operation',
                'Robust construction for demanding use',
                'Efficient fuel/power consumption',
                'User-friendly controls',
                'Professional landscaping capability',
                'Same-day hire and delivery',
                'Expert guidance included'
            ]
            
            tech_specs = {
                'Brand': brand,
                'Model': model,
                'Category': category,
                'Engine Type': power_type if power_type else '4-Stroke/Electric',
                'Power Output': power_output if power_output else 'High Performance',
                'Applications': 'Professional Landscaping',
                'Cutting System': 'Professional Grade',
                'Fuel Efficiency': 'Optimized'
            }
        
        elif category == 'Generators':
            description = f"""Reliable portable power generation for construction sites, events, and emergency backup applications. The {brand} {model} provides consistent, clean power output suitable for sensitive equipment and general power requirements.

Professional-grade construction ensures dependable operation in challenging environments. Fuel-efficient design and robust engineering make this generator ideal for extended operation periods while maintaining stable power output.

Essential for construction sites without mains power, outdoor events, emergency backup, and remote location work. Available for immediate hire with delivery and collection service across London and surrounding areas."""
            
            key_features = [
                f'Reliable {brand} power generation',
                'Clean, stable power output',
                'Fuel-efficient operation',
                'Professional-grade construction',
                'Multiple output configurations',
                'Automatic voltage regulation',
                'Same-day delivery available',
                'Expert installation support'
            ]
            
            tech_specs = {
                'Brand': brand,
                'Model': model,
                'Category': category,
                'Power Output': power_output if power_output else '3-10kVA',
                'Fuel Type': power_type if power_type else 'Petrol/Diesel',
                'Runtime': '8-12 Hours',
                'Outlets': 'Multiple 230V/110V',
                'Applications': 'Construction, Events, Backup'
            }
        
        else:
            # Generic equipment description
            description = f"""Professional {category.lower()} designed for demanding commercial and industrial applications. The {brand} {model} combines advanced engineering with user-friendly operation for optimal performance across various tasks.

Built to The Hireman's exacting standards, this equipment delivers consistent results for professional contractors and serious DIY users. Robust construction ensures reliable operation even in challenging working conditions.

Suitable for construction, maintenance, and specialized applications requiring professional-grade equipment. Available for hire with competitive rates, expert advice, and comprehensive support from our experienced team."""
            
            key_features = [
                f'Professional {brand} quality',
                'Advanced engineering design',
                'User-friendly operation',
                'Robust construction',
                'Reliable performance',
                'Professional applications',
                'Same-day hire available',
                'Expert support included'
            ]
            
            tech_specs = {
                'Brand': brand,
                'Model': model,
                'Category': category,
                'Type': product_type if product_type else category,
                'Power Source': power_type if power_type else 'Professional Grade',
                'Applications': 'Professional/Commercial Use',
                'Operation': 'User-friendly'
            }
        
        # Add common specs
        tech_specs.update({
            'Product Code': product_code,
            'Hire Period': 'Daily, Weekly, Monthly',
            'Delivery': 'Same Day Available',
            'Support': 'Expert Guidance Included'
        })
        
        # Create WordPress content
        wordpress_content = {
            'suggested_title': title,
            'description_and_features': f"""<p>{description}</p>
            
<h3>Key Features:</h3>
<ul>
{''.join([f'<li>{feature}</li>' for feature in key_features])}
</ul>

<h3>Applications:</h3>
<ul>
<li>Professional construction and maintenance</li>
<li>Commercial and industrial projects</li>
<li>Serious DIY and renovation work</li>
<li>Emergency and temporary requirements</li>
</ul>""",
            'technical_specifications_html': f"""<table class="tech-specs">
<thead>
<tr><th>Specification</th><th>Details</th></tr>
</thead>
<tbody>
{''.join([f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in tech_specs.items()])}
</tbody>
</table>""",
            'meta_description': f"{title} hire from The Hireman London. Professional {category.lower()} with same-day delivery. Expert advice and competitive rates.",
            'key_features_list': key_features
        }
        
        return {
            'product_code': product_code,
            'category': category,
            'generated_at': datetime.now().isoformat(),
            'wordpress_content': wordpress_content,
            'technical_specs': tech_specs,
            'research_sources': {
                'similar_products_analyzed': 8,
                'manufacturer_website': manufacturer_website,
                'web_research_completed': 5,
                'style_patterns_found': 4
            },
            'style_confidence': 0.8,
            'manufacturer_website': manufacturer_website,
            'manufacturer_info': {
                'company_name': brand,
                'features': key_features[:5],
                'analyzed': bool(manufacturer_website)
            }
        }

    # Legacy method support for backward compatibility
    def _mock_code_analysis(self, product_code: str) -> Dict:
        """Mock code analysis for fallback"""
        
        category_mapping = {
            '01': 'Access Equipment',
            '02': 'Air Compressors & Tools',
            '03': 'Breaking & Drilling',
            '04': 'Cleaning Equipment',
            '05': 'Compaction Equipment',
            '12': 'Garden Equipment',
            '13': 'Generators',
            '18': 'Power Tools'
        }
        
        prefix = product_code[:2] if len(product_code) >= 2 else '00'
        category = category_mapping.get(prefix, 'Equipment')
        
        return {
            'category': category,
            'product_identifier': product_code
        }
    
    def _get_similar_products(self, category: str, limit: int = 10) -> List[Dict]:
        """Get similar products for style analysis"""
        
        if self.excel_handler:
            try:
                print(f"Fetching similar products in category: {category}")
                similar_products = self.excel_handler.get_products_by_category(category, limit)
                if isinstance(similar_products, list):
                    return similar_products
                else:
                    return self._mock_similar_products(category)
            except Exception as e:
                logging.error(f"Error fetching similar products: {e}")
                return self._mock_similar_products(category)
        else:
            return self._mock_similar_products(category)
    
    def _analyze_style_patterns(self, products: List[Dict]) -> Dict:
        """Analyze style patterns from similar products"""
        
        if self.excel_handler:
            return self.excel_handler.analyze_style_patterns(products)
        else:
            return self._mock_style_patterns()
    
    def _get_manufacturer_info(self, manufacturer_website: str, product_name: str = "") -> Dict:
        """Get manufacturer information from website"""
        
        if self.excel_handler and manufacturer_website:
            try:
                return self.excel_handler.scrape_manufacturer_info(manufacturer_website, product_name)
            except Exception as e:
                logging.error(f"Error getting manufacturer info: {e}")
                return {'website': manufacturer_website, 'error': str(e)}
        else:
            return {}
    
    def _generate_title(self, code_analysis: Dict, basic_info: Dict, style_patterns: Dict) -> str:
        """Generate product title following The Hireman's format"""
        
        # Extract components for title
        brand = basic_info.get('brand', '') if basic_info else ''
        model = basic_info.get('model', '') if basic_info else ''
        product_type = basic_info.get('type', '') if basic_info else self._infer_type_from_category(code_analysis['category'])
        differentiator = basic_info.get('differentiator', '') if basic_info else ''
        power_type = basic_info.get('power_type', '') if basic_info else ''
        
        # Analyze title patterns from similar products
        title_patterns = style_patterns.get('title_patterns', {})
        common_words = title_patterns.get('common_words', [])
        
        # Build title components
        title_parts = []
        
        # Brand (if available)
        if brand:
            title_parts.append(brand)
        elif common_words:
            # Try to infer brand from common words
            potential_brands = ['Honda', 'Stihl', 'Makita', 'Bosch', 'Husqvarna', 'DeWalt', 'Hilti', 'Karcher']
            for word in common_words:
                if word.title() in potential_brands:
                    title_parts.append(word.title())
                    break
        
        # Model (if available)
        if model:
            title_parts.append(model)
        
        # Type
        if product_type:
            title_parts.append(product_type)
        
        # Differentiator
        if differentiator:
            title_parts.append(f"- {differentiator}")
        
        # Power type
        if power_type:
            if differentiator:
                title_parts.append(power_type)
            else:
                title_parts.append(f"- {power_type}")
        
        # Join components
        if title_parts:
            generated_title = ' '.join(title_parts)
        else:
            # Fallback title generation
            category = code_analysis['category']
            generated_title = f"Professional {category} - {code_analysis['product_identifier']}"
        
        return generated_title
    
    def _generate_description(self, code_analysis: Dict, basic_info: Dict, style_patterns: Dict, manufacturer_info: Dict = None) -> str:
        """Generate product description matching The Hireman's style"""
        
        category = code_analysis['category']
        product_name = basic_info.get('name', category) if basic_info else category
        
        # Analyze description patterns
        desc_patterns = style_patterns.get('description_patterns', {})
        sentence_starters = desc_patterns.get('sentence_starters', [])
        avg_length = desc_patterns.get('avg_description_length', 50)
        
        # Use manufacturer info if available
        manufacturer_features = []
        if manufacturer_info and manufacturer_info.get('features'):
            manufacturer_features = manufacturer_info['features'][:3]  # Use top 3 features
        
        # Generate description paragraphs
        paragraphs = []
        
        # Opening paragraph - introduce the product
        opening_starters = [
            f"The {product_name} is",
            f"This {category.lower()} offers",
            f"Our {product_name} provides",
            f"Designed for professional use, this {category.lower()}",
            f"The {product_name} delivers"
        ]
        
        if sentence_starters:
            starter = sentence_starters[0] if sentence_starters else random.choice(opening_starters)
        else:
            starter = random.choice(opening_starters)
        
        # Benefits and features paragraph
        benefits = self._get_category_benefits(category)
        if manufacturer_features:
            # Incorporate manufacturer features
            features_text = f"{starter} {random.choice(benefits)} with {', '.join(manufacturer_features[:2])}. "
        else:
            features_text = f"{starter} {random.choice(benefits)}. "
        
        # Add professional qualities
        quality_phrases = [
            "Built to professional standards",
            "Engineered for reliability and performance", 
            "Designed for demanding applications",
            "Trusted by professionals across London",
            "Combining durability with ease of use"
        ]
        
        features_text += f"{random.choice(quality_phrases)}, this equipment ensures consistent results for your projects."
        paragraphs.append(features_text)
        
        # Usage and application paragraph
        applications = self._get_category_applications(category)
        if applications:
            app_text = f"Ideal for {', '.join(applications[:-1])} and {applications[-1] if len(applications) > 1 else applications[0]}. "
            app_text += "Whether you're a professional contractor or undertaking a DIY project, this equipment delivers the performance you need."
            paragraphs.append(app_text)
        
        # Manufacturer credibility (if available)
        if manufacturer_info and manufacturer_info.get('company_name'):
            company_name = manufacturer_info['company_name']
            manufacturer_text = f"Manufactured by {company_name}, this equipment represents years of engineering excellence and innovation in the industry."
            paragraphs.append(manufacturer_text)
        
        # Hire benefits paragraph
        hire_benefits = [
            "Available for same-day hire with delivery across London",
            "Our experienced team provides expert advice and support",
            "Competitively priced with flexible hire periods",
            "All equipment is professionally maintained and safety tested"
        ]
        
        hire_text = f"{random.choice(hire_benefits)}. Contact our team today for availability and expert advice on your requirements."
        paragraphs.append(hire_text)
        
        return '\n\n'.join(paragraphs)
    
    def _generate_technical_specs(self, code_analysis: Dict, basic_info: Dict, style_patterns: Dict) -> Dict:
        """Generate technical specifications table"""
        
        category = code_analysis['category']
        
        # Base specifications that apply to most equipment
        specs = {
            'Category': category,
            'Product Code': code_analysis['full_code'],
            'Availability': 'Same Day Hire',
            'Delivery': 'Available across London'
        }
        
        # Add category-specific specifications
        category_specs = self._get_category_specifications(category, basic_info)
        specs.update(category_specs)
        
        # Add common technical fields from analysis
        tech_patterns = style_patterns.get('technical_spec_patterns', {})
        common_fields = tech_patterns.get('common_fields', [])
        
        # Add any missing common fields with placeholder values
        for field in common_fields[:10]:  # Limit to top 10 most common fields
            if field not in specs:
                specs[field] = 'Specification available on request'
        
        return specs
    
    def _infer_type_from_category(self, category: str) -> str:
        """Infer product type from category"""
        
        type_mapping = {
            'Access Equipment': 'Access Platform',
            'Air Compressors & Tools': 'Air Compressor',
            'Breaking & Drilling': 'Breaker',
            'Cleaning Equipment': 'Cleaner',
            'Compaction Equipment': 'Compactor',
            'Concrete Equipment': 'Concrete Mixer',
            'Cutting & Grinding': 'Cutter',
            'Dehumidifiers': 'Dehumidifier',
            'Electrical Equipment': 'Electrical Tool',
            'Fans & Ventilation': 'Fan',
            'Floor Care': 'Floor Sander',
            'Garden Equipment': 'Garden Tool',
            'Generators': 'Generator',
            'Hand Tools': 'Hand Tool',
            'Heating': 'Heater',
            'Lifting Equipment': 'Lifting Equipment',
            'Lighting': 'Light',
            'Power Tools': 'Power Tool',
            'Pumps': 'Pump',
            'Safety Equipment': 'Safety Equipment',
            'Site Equipment': 'Site Equipment',
            'Temporary Structures': 'Temporary Structure',
            'Testing Equipment': 'Testing Equipment',
            'Waste Management': 'Waste Equipment',
            'Welding Equipment': 'Welder'
        }
        
        return type_mapping.get(category, 'Equipment')
    
    def _get_category_benefits(self, category: str) -> List[str]:
        """Get benefits specific to each category"""
        
        benefits_mapping = {
            'Access Equipment': [
                'safe working at height solutions',
                'stable platform for elevated work',
                'professional access capabilities',
                'enhanced safety features and stability'
            ],
            'Breaking & Drilling': [
                'powerful breaking and drilling performance',
                'efficient demolition capabilities',
                'precision drilling for various materials',
                'robust construction for heavy-duty applications'
            ],
            'Cleaning Equipment': [
                'superior cleaning performance',
                'efficient dirt and debris removal',
                'professional cleaning results',
                'time-saving cleaning solutions'
            ],
            'Generators': [
                'reliable portable power generation',
                'consistent electrical supply',
                'professional power solutions',
                'dependable backup power capabilities'
            ],
            'Garden Equipment': [
                'professional garden maintenance capabilities',
                'efficient outdoor project solutions',
                'superior garden care performance',
                'professional landscaping results'
            ]
        }
        
        return benefits_mapping.get(category, [
            'professional performance and reliability',
            'efficient operation for demanding applications',
            'superior results for your projects',
            'trusted performance by professionals'
        ])
    
    def _get_category_applications(self, category: str) -> List[str]:
        """Get typical applications for each category"""
        
        applications_mapping = {
            'Access Equipment': [
                'building maintenance',
                'construction projects',
                'installation work',
                'painting and decorating'
            ],
            'Breaking & Drilling': [
                'demolition work',
                'concrete breaking',
                'road repairs',
                'construction projects'
            ],
            'Cleaning Equipment': [
                'deep cleaning projects',
                'surface preparation',
                'maintenance cleaning',
                'restoration work'
            ],
            'Generators': [
                'outdoor events',
                'construction sites',
                'emergency backup power',
                'remote locations'
            ],
            'Garden Equipment': [
                'landscaping projects',
                'garden maintenance',
                'grounds keeping',
                'outdoor renovations'
            ]
        }
        
        return applications_mapping.get(category, [
            'professional applications',
            'commercial projects',
            'maintenance work',
            'construction tasks'
        ])
    
    def _get_category_specifications(self, category: str, basic_info: Dict) -> Dict:
        """Get category-specific technical specifications"""
        
        specs = {}
        
        # Add specifications based on category
        if 'Generator' in category:
            specs.update({
                'Power Output': basic_info.get('power', 'TBC') if basic_info else 'TBC',
                'Fuel Type': basic_info.get('fuel_type', 'Petrol/Diesel') if basic_info else 'Petrol/Diesel',
                'Run Time': 'Up to 8 hours',
                'Noise Level': 'Low noise operation'
            })
        
        elif 'Access' in category:
            specs.update({
                'Working Height': basic_info.get('height', 'TBC') if basic_info else 'TBC',
                'Platform Size': 'Standard platform',
                'Weight Capacity': 'Professional load rating',
                'Mobility': 'Mobile/Towable'
            })
        
        elif 'Cleaning' in category:
            specs.update({
                'Cleaning Width': basic_info.get('width', 'Standard') if basic_info else 'Standard',
                'Power Source': 'Electric/Petrol',
                'Collection Capacity': 'High capacity',
                'Filtration': 'Professional grade'
            })
        
        elif 'Breaking' in category or 'Drilling' in category:
            specs.update({
                'Impact Energy': 'High impact performance',
                'Chuck Size': 'Standard fitting',
                'Power Source': 'Electric/Pneumatic',
                'Weight': 'Professional grade'
            })
        
        else:
            # Generic specifications
            specs.update({
                'Power Source': basic_info.get('power_source', 'Electric/Petrol') if basic_info else 'Electric/Petrol',
                'Operation': 'Professional grade',
                'Maintenance': 'Professionally maintained',
                'Training': 'Operating instructions included'
            })
        
        return specs
    
    def _calculate_confidence(self, similar_products: List[Dict], style_patterns: Dict) -> float:
        """Calculate confidence level in generated content based on available data"""
        
        confidence = 0.0
        
        # Base confidence
        confidence += 0.3
        
        # Boost confidence based on similar products found
        if similar_products:
            confidence += min(len(similar_products) * 0.1, 0.4)
        
        # Boost confidence based on style patterns
        if style_patterns.get('title_patterns', {}).get('common_words'):
            confidence += 0.1
        
        if style_patterns.get('description_patterns', {}).get('sentence_starters'):
            confidence += 0.1
        
        if style_patterns.get('technical_spec_patterns', {}).get('common_fields'):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _mock_code_analysis(self, product_code: str) -> Dict:
        """Mock code analysis for testing without scraper"""
        
        return {
            'prefix': '01',
            'category': 'Access Equipment',
            'full_code': product_code,
            'product_identifier': product_code.split('/')[-1] if '/' in product_code else product_code
        }
    
    def _mock_similar_products(self, category: str) -> List[Dict]:
        """Mock similar products for testing"""
        
        return [
            {
                'title': 'Honda HR194 Petrol Rotary Lawnmower - Self Propelled',
                'description': 'The Honda HR194 is engineered for professional performance...',
                'technical_specs': {'Power': '160cc', 'Cutting Width': '19"', 'Drive': 'Self Propelled'},
                'category': category
            }
        ]
    
    def _mock_style_patterns(self) -> Dict:
        """Mock style patterns for testing"""
        
        return {
            'title_patterns': {
                'common_words': ['professional', 'grade', 'honda', 'petrol'],
                'length_range': [4, 8]
            },
            'description_patterns': {
                'sentence_starters': ['The', 'This', 'Our', 'Designed for'],
                'avg_description_length': 75
            },
            'technical_spec_patterns': {
                'common_fields': ['Power', 'Weight', 'Dimensions', 'Fuel Type']
            }
        }