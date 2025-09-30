import json
import re
import random
from typing import Dict, List, Optional
from datetime import datetime
import logging

class ProductDescriptionGenerator:
    def __init__(self, excel_handler=None):
        self.excel_handler = excel_handler
        self.style_patterns = {}
        self.similar_products = []
        
    def generate_product_content(self, product_code: str, basic_info: Dict = None) -> Dict:
        """
        Generate complete product content (title, description, technical specs)
        based on product code and optional basic information
        """
        
        print(f"Generating content for product code: {product_code}")
        
        # Analyze product code
        code_analysis = self.excel_handler.analyze_product_code(product_code) if self.excel_handler else self._mock_code_analysis(product_code)
        
        # Find similar products for style analysis
        similar_products = self._get_similar_products(code_analysis['category'])
        
        # Analyze style patterns
        style_patterns = self._analyze_style_patterns(similar_products)
        
        # Get manufacturer information if available
        manufacturer_info = {}
        if basic_info and basic_info.get('manufacturer_website'):
            manufacturer_info = self._get_manufacturer_info(
                basic_info.get('manufacturer_website'), 
                basic_info.get('name', '')
            )
        
        # Generate content components
        generated_content = {
            'product_code': product_code,
            'category': code_analysis['category'],
            'generated_at': datetime.now().isoformat(),
            'title': self._generate_title(code_analysis, basic_info, style_patterns),
            'description': self._generate_description(code_analysis, basic_info, style_patterns, manufacturer_info),
            'technical_specs': self._generate_technical_specs(code_analysis, basic_info, style_patterns),
            'manufacturer_info': manufacturer_info,
            'manufacturer_website': basic_info.get('manufacturer_website', '') if basic_info else '',
            'style_confidence': self._calculate_confidence(similar_products, style_patterns)
        }
        
        return generated_content
    
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