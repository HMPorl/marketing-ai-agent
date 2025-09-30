import json
import random
from datetime import datetime
from typing import Dict, List, Optional

class ContentGenerator:
    def __init__(self, tone_file_path=None):
        self.tone_guidelines = self._load_tone_guidelines(tone_file_path)
        self.product_templates = self._load_product_templates()
        self.campaign_templates = self._load_campaign_templates()
        self.social_templates = self._load_social_templates()
    
    def generate_product_description(self, product_info: Dict) -> str:
        """Generate product description based on product information"""
        
        # Extract product details
        name = product_info.get('name', 'Product')
        category = product_info.get('category', 'Equipment')
        features = product_info.get('features', [])
        target_audience = product_info.get('target_audience', 'professionals')
        tone = product_info.get('tone', 'professional')
        
        # Select appropriate template
        template = self._select_template(self.product_templates, category, tone)
        
        # Generate features text
        features_text = self._format_features(features)
        
        # Apply tone guidelines
        tone_words = self._get_tone_words(tone)
        
        # Generate description
        description = template.format(
            product_name=name,
            category=category.lower(),
            features=features_text,
            target_audience=target_audience,
            tone_adjective=random.choice(tone_words['adjectives']),
            benefit_phrase=random.choice(tone_words['benefits'])
        )
        
        return description.strip()
    
    def generate_eshot_campaign(self, campaign_info: Dict) -> Dict:
        """Generate e-shot campaign content"""
        
        products = campaign_info.get('products', [])
        campaign_type = campaign_info.get('type', 'promotional')
        weather_context = campaign_info.get('weather_context', '')
        urgency = campaign_info.get('urgency', 'medium')
        
        # Select campaign template
        template = self._select_template(self.campaign_templates, campaign_type, urgency)
        
        # Generate subject line
        subject_line = self._generate_subject_line(products, campaign_type, urgency)
        
        # Generate main content
        main_content = template['content'].format(
            products_list=self._format_products_list(products),
            weather_context=weather_context,
            call_to_action=template['cta'],
            urgency_phrase=self._get_urgency_phrase(urgency)
        )
        
        # Generate footer
        footer = self._generate_footer()
        
        return {
            'subject_line': subject_line,
            'content': main_content,
            'footer': footer,
            'campaign_type': campaign_type,
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_social_media_post(self, post_info: Dict) -> Dict:
        """Generate social media post content"""
        
        platform = post_info.get('platform', 'linkedin')
        post_type = post_info.get('type', 'product_showcase')
        products = post_info.get('products', [])
        hashtags = post_info.get('hashtags', [])
        weather_context = post_info.get('weather_context', '')
        
        # Select social template
        template = self._select_template(self.social_templates, platform, post_type)
        
        # Generate main post content
        main_content = template['content'].format(
            products=self._format_products_for_social(products),
            weather_context=weather_context,
            emoji=template.get('emoji', '🔧')
        )
        
        # Add hashtags
        hashtag_text = ' '.join([f'#{tag}' for tag in hashtags])
        
        # Generate call to action
        cta = template.get('cta', 'Get in touch today!')
        
        full_post = f"{main_content}\n\n{cta}\n\n{hashtag_text}"
        
        return {
            'content': full_post,
            'platform': platform,
            'post_type': post_type,
            'character_count': len(full_post),
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_campaign_calendar(self, year: int = None) -> List[Dict]:
        """Generate annual campaign calendar with seasonal and event-based campaigns"""
        
        if year is None:
            year = datetime.now().year
        
        campaigns = []
        
        # Seasonal campaigns
        seasonal_campaigns = [
            {'month': 1, 'name': 'New Year Construction Prep', 'type': 'seasonal', 'focus': 'construction equipment'},
            {'month': 2, 'name': 'Winter Heating Solutions', 'type': 'weather', 'focus': 'heating equipment'},
            {'month': 3, 'name': 'Spring Garden Ready', 'type': 'seasonal', 'focus': 'garden equipment'},
            {'month': 4, 'name': 'Easter DIY Projects', 'type': 'event', 'focus': 'diy tools'},
            {'month': 5, 'name': 'Summer Event Prep', 'type': 'seasonal', 'focus': 'event equipment'},
            {'month': 6, 'name': 'Wedding Season Specials', 'type': 'event', 'focus': 'event equipment'},
            {'month': 7, 'name': 'Summer Construction Peak', 'type': 'seasonal', 'focus': 'construction equipment'},
            {'month': 8, 'name': 'Festival Equipment Hire', 'type': 'event', 'focus': 'event equipment'},
            {'month': 9, 'name': 'Back to Business', 'type': 'seasonal', 'focus': 'commercial equipment'},
            {'month': 10, 'name': 'Autumn Maintenance', 'type': 'seasonal', 'focus': 'maintenance equipment'},
            {'month': 11, 'name': 'Winter Preparation', 'type': 'weather', 'focus': 'winter equipment'},
            {'month': 12, 'name': 'Christmas Event Solutions', 'type': 'event', 'focus': 'event equipment'}
        ]
        
        for campaign in seasonal_campaigns:
            campaigns.append({
                'id': f"{year}_{campaign['month']:02d}_{campaign['name'].replace(' ', '_').lower()}",
                'name': campaign['name'],
                'month': campaign['month'],
                'year': year,
                'type': campaign['type'],
                'focus_category': campaign['focus'],
                'suggested_start': f"{year}-{campaign['month']:02d}-01",
                'duration_weeks': 2,
                'priority': 'medium',
                'auto_generated': True
            })
        
        # Weather-dependent campaigns (to be triggered by weather conditions)
        weather_campaigns = [
            {'name': 'Heavy Rain Alert - Water Management', 'trigger': 'heavy_rain', 'products': ['water pumps', 'dehumidifiers']},
            {'name': 'Cold Snap Special - Heating Equipment', 'trigger': 'cold_weather', 'products': ['heaters', 'thermal equipment']},
            {'name': 'High Winds Warning - Safety Equipment', 'trigger': 'high_winds', 'products': ['safety barriers', 'secure storage']},
            {'name': 'Heatwave Solutions - Cooling Equipment', 'trigger': 'hot_weather', 'products': ['cooling fans', 'air conditioning']}
        ]
        
        for campaign in weather_campaigns:
            campaigns.append({
                'id': f"weather_{campaign['name'].replace(' ', '_').lower()}",
                'name': campaign['name'],
                'type': 'weather_triggered',
                'trigger_condition': campaign['trigger'],
                'target_products': campaign['products'],
                'priority': 'high',
                'auto_generated': True,
                'flexible_timing': True
            })
        
        return campaigns
    
    def _load_tone_guidelines(self, file_path: str) -> Dict:
        """Load tone guidelines from file or use defaults"""
        
        default_tone = {
            'professional': {
                'adjectives': ['reliable', 'professional', 'high-quality', 'efficient', 'proven'],
                'benefits': ['delivers exceptional results', 'ensures project success', 'maximizes efficiency'],
                'phrases': ['industry-leading', 'professional-grade', 'trusted by professionals']
            },
            'friendly': {
                'adjectives': ['friendly', 'helpful', 'easy-to-use', 'versatile', 'dependable'],
                'benefits': ['makes your job easier', 'gets the job done right', 'perfect for any project'],
                'phrases': ['we\'re here to help', 'great for DIY enthusiasts', 'simple and effective']
            },
            'technical': {
                'adjectives': ['precision-engineered', 'advanced', 'high-performance', 'technical', 'industrial-grade'],
                'benefits': ['meets technical specifications', 'delivers precise performance', 'engineered for demanding applications'],
                'phrases': ['technical excellence', 'engineered precision', 'professional specifications']
            },
            'promotional': {
                'adjectives': ['amazing', 'fantastic', 'unbeatable', 'special', 'limited-time'],
                'benefits': ['incredible savings', 'exceptional value', 'don\'t miss out'],
                'phrases': ['special offer', 'limited time only', 'amazing deals']
            }
        }
        
        # TODO: Load from actual file if provided
        return default_tone
    
    def _load_product_templates(self) -> List[Dict]:
        """Load product description templates"""
        
        return [
            {
                'category': 'general',
                'tone': 'professional',
                'template': """**{product_name}** - Professional Grade {category}

{product_name} represents {tone_adjective} {category} technology, designed for demanding professional applications. 

{features}

This equipment {benefit_phrase}, making it the ideal choice for contractors and professionals who demand reliability and performance. Our commitment to quality ensures that every piece of equipment meets the highest industry standards.

Perfect for projects requiring precision and efficiency, {product_name} combines innovative design with practical functionality."""
            },
            {
                'category': 'general',
                'tone': 'friendly',
                'template': """**{product_name}** - Your {tone_adjective} {category} Solution

Looking for {category} that {benefit_phrase}? {product_name} is here to help!

{features}

Whether you're a professional contractor or a DIY enthusiast, this {category} makes your projects easier and more efficient. We believe in providing equipment that's not only powerful but also user-friendly.

Get in touch today to hire {product_name} and see the difference quality equipment makes!"""
            }
        ]
    
    def _load_campaign_templates(self) -> List[Dict]:
        """Load campaign email templates"""
        
        return [
            {
                'type': 'weather',
                'urgency': 'high',
                'content': """⚠️ WEATHER ALERT ⚠️

{weather_context}

Don't let the weather catch you unprepared! We have the equipment you need:

{products_list}

{urgency_phrase}

{call_to_action}""",
                'cta': '📞 Call us now for immediate availability!'
            },
            {
                'type': 'promotional',
                'urgency': 'medium',
                'content': """🎯 SPECIAL OFFER - Equipment Hire

Take advantage of our latest promotions on quality equipment hire:

{products_list}

{urgency_phrase}

{call_to_action}""",
                'cta': '📧 Contact us today to secure your equipment!'
            },
            {
                'type': 'seasonal',
                'urgency': 'low',
                'content': """🌟 Seasonal Equipment Solutions

As the season changes, make sure you have the right equipment for your projects:

{products_list}

Our experienced team is ready to help you choose the perfect equipment for your needs.

{call_to_action}""",
                'cta': '💬 Get in touch for expert advice and competitive rates!'
            }
        ]
    
    def _load_social_templates(self) -> List[Dict]:
        """Load social media post templates"""
        
        return [
            {
                'platform': 'linkedin',
                'type': 'product_showcase',
                'content': """🔧 Professional Equipment Hire in London

{products} - delivering reliable solutions for your projects.

{weather_context}

✅ Competitive rates
✅ Expert advice included
✅ Same-day availability
✅ Delivery across London""",
                'cta': 'Get in touch today!',
                'emoji': '🔧'
            },
            {
                'platform': 'facebook',
                'type': 'promotional',
                'content': """🎉 Amazing deals on equipment hire!

{products} - perfect for your next project.

{weather_context}

Why choose us? Because we care about your success! 💪""",
                'cta': 'Message us for instant quotes!',
                'emoji': '🎉'
            },
            {
                'platform': 'linkedin',
                'type': 'weather_alert',
                'content': """🌧️ Weather Update for London

{weather_context}

Stay prepared with our {products}:

Be ready, not reactive! Our team is standing by to help.""",
                'cta': 'Contact us for immediate equipment availability!',
                'emoji': '🌧️'
            }
        ]
    
    def _select_template(self, templates: List[Dict], category: str, tone: str) -> Dict:
        """Select most appropriate template"""
        
        # First try exact match
        for template in templates:
            if template.get('category') == category and template.get('tone') == tone:
                return template
        
        # Then try category match
        for template in templates:
            if template.get('category') == category:
                return template
        
        # Finally use general template
        for template in templates:
            if template.get('category') == 'general':
                return template
        
        # Fallback to first template
        return templates[0] if templates else {}
    
    def _format_features(self, features: List[str]) -> str:
        """Format features list into readable text"""
        if not features:
            return "Key features include professional design and reliable performance."
        
        if len(features) == 1:
            return f"Key feature: {features[0]}"
        
        formatted = "Key Features:\n"
        for feature in features:
            formatted += f"• {feature}\n"
        
        return formatted.strip()
    
    def _format_products_list(self, products: List[str]) -> str:
        """Format products list for email campaigns"""
        if not products:
            return "• Quality equipment available"
        
        formatted = ""
        for product in products:
            formatted += f"• {product}\n"
        
        return formatted.strip()
    
    def _format_products_for_social(self, products: List[str]) -> str:
        """Format products list for social media"""
        if not products:
            return "Quality equipment"
        
        if len(products) == 1:
            return products[0]
        elif len(products) == 2:
            return f"{products[0]} and {products[1]}"
        else:
            return f"{', '.join(products[:-1])}, and {products[-1]}"
    
    def _get_tone_words(self, tone: str) -> Dict:
        """Get tone-specific words and phrases"""
        return self.tone_guidelines.get(tone, self.tone_guidelines['professional'])
    
    def _generate_subject_line(self, products: List[str], campaign_type: str, urgency: str) -> str:
        """Generate email subject line"""
        
        urgency_prefixes = {
            'high': ['URGENT:', 'ALERT:', 'IMMEDIATE:'],
            'medium': ['OFFER:', 'SPECIAL:', 'NOTICE:'],
            'low': ['UPDATE:', 'INFO:', '']
        }
        
        type_templates = {
            'weather': '{prefix} Weather Alert - {products} Available Now',
            'promotional': '{prefix} Special Offer on {products}',
            'seasonal': '{prefix} Seasonal Equipment - {products}'
        }
        
        prefix = random.choice(urgency_prefixes.get(urgency, ['']))
        template = type_templates.get(campaign_type, '{prefix} {products} - Equipment Hire')
        
        products_text = products[0] if products else 'Quality Equipment'
        
        return template.format(prefix=prefix, products=products_text).strip()
    
    def _get_urgency_phrase(self, urgency: str) -> str:
        """Get urgency-appropriate phrase"""
        
        phrases = {
            'high': 'Act now - limited availability!',
            'medium': 'Don\'t miss out on this opportunity!',
            'low': 'Contact us when you\'re ready.'
        }
        
        return phrases.get(urgency, phrases['medium'])
    
    def _generate_footer(self) -> str:
        """Generate email footer"""
        
        return """
---
Professional Equipment Hire
📞 Phone: [Your Phone Number]
📧 Email: [Your Email]
🌐 Website: [Your Website]
📍 Serving London and surrounding areas

Quality equipment • Expert advice • Competitive rates
"""