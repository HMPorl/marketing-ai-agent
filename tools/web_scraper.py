import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin, urlparse
import logging

class WebScraper:
    def __init__(self, delay=1):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_website_products(self, base_url, product_pages=None):
        """Scrape product information from website"""
        products = []
        
        if product_pages:
            # Scrape specific product pages
            for page_url in product_pages:
                try:
                    product_data = self._scrape_product_page(page_url)
                    if product_data:
                        products.append(product_data)
                    time.sleep(self.delay)
                except Exception as e:
                    logging.error(f"Error scraping {page_url}: {e}")
        else:
            # Discover and scrape product pages
            products = self._discover_and_scrape_products(base_url)
        
        return products
    
    def scrape_competitor_info(self, competitor_urls):
        """Scrape competitor information"""
        competitor_data = {}
        
        for name, url in competitor_urls.items():
            try:
                print(f"Scraping {name}...")
                data = self._scrape_competitor_site(url)
                competitor_data[name] = data
                time.sleep(self.delay * 2)  # Be respectful to competitors
            except Exception as e:
                logging.error(f"Error scraping {name}: {e}")
                competitor_data[name] = {"error": str(e)}
        
        return competitor_data
    
    def _scrape_product_page(self, url):
        """Scrape individual product page"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Generic product extraction (adjust selectors for your website)
            product_data = {
                'url': url,
                'title': self._extract_text(soup, ['h1', '.product-title', '.title']),
                'description': self._extract_text(soup, ['.product-description', '.description', 'p']),
                'price': self._extract_text(soup, ['.price', '.cost', '.rate']),
                'features': self._extract_list(soup, ['.features li', '.specs li', 'ul li']),
                'images': self._extract_images(soup),
                'category': self._extract_text(soup, ['.category', '.breadcrumb']),
                'scraped_at': time.time()
            }
            
            return product_data
            
        except Exception as e:
            logging.error(f"Error scraping product page {url}: {e}")
            return None
    
    def _scrape_competitor_site(self, url):
        """Scrape competitor website for insights"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract general information
            data = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'promotions': self._find_promotions(soup),
                'featured_products': self._find_featured_products(soup),
                'contact_info': self._find_contact_info(soup),
                'social_links': self._find_social_links(soup),
                'scraped_at': time.time()
            }
            
            return data
            
        except Exception as e:
            logging.error(f"Error scraping competitor {url}: {e}")
            return {"error": str(e)}
    
    def _discover_and_scrape_products(self, base_url):
        """Discover product pages and scrape them"""
        products = []
        
        try:
            response = self.session.get(base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product links (adjust selectors for your website)
            product_links = []
            for selector in ['.product-link', '.item-link', 'a[href*="product"]', 'a[href*="hire"]']:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(base_url, href)
                        product_links.append(full_url)
            
            # Remove duplicates
            product_links = list(set(product_links))
            
            # Scrape each product page
            for link in product_links[:20]:  # Limit to first 20 products
                product_data = self._scrape_product_page(link)
                if product_data:
                    products.append(product_data)
                time.sleep(self.delay)
            
        except Exception as e:
            logging.error(f"Error discovering products from {base_url}: {e}")
        
        return products
    
    def _extract_text(self, soup, selectors):
        """Extract text using multiple possible selectors"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return ""
    
    def _extract_list(self, soup, selectors):
        """Extract list items using multiple possible selectors"""
        items = []
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and text not in items:
                    items.append(text)
        return items
    
    def _extract_images(self, soup):
        """Extract product images"""
        images = []
        for img in soup.select('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                images.append(src)
        return images[:5]  # Limit to first 5 images
    
    def _find_promotions(self, soup):
        """Find promotional content"""
        promotions = []
        
        # Look for promotion indicators
        promo_selectors = [
            '.promotion', '.offer', '.deal', '.sale',
            '[class*="promo"]', '[class*="offer"]',
            'text()[contains(., "%")]', 'text()[contains(., "sale")]'
        ]
        
        for selector in promo_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and len(text) < 200:  # Reasonable length
                    promotions.append(text)
        
        return promotions[:10]  # Limit results
    
    def _find_featured_products(self, soup):
        """Find featured or popular products"""
        products = []
        
        # Look for featured product sections
        feature_selectors = [
            '.featured-product', '.popular-product', '.highlight',
            '[class*="featured"]', '[class*="popular"]'
        ]
        
        for selector in feature_selectors:
            elements = soup.select(selector)
            for element in elements:
                title = element.select_one('h1, h2, h3, h4, .title')
                if title:
                    products.append(title.get_text(strip=True))
        
        return products[:10]
    
    def _find_contact_info(self, soup):
        """Extract contact information"""
        contact = {}
        
        # Look for phone numbers
        phone_patterns = soup.find_all(text=lambda text: text and any(char.isdigit() for char in text) and ('phone' in text.lower() or 'tel' in text.lower()))
        if phone_patterns:
            contact['phone'] = phone_patterns[0].strip()
        
        # Look for email
        email_links = soup.select('a[href^="mailto:"]')
        if email_links:
            contact['email'] = email_links[0].get('href').replace('mailto:', '')
        
        return contact
    
    def _find_social_links(self, soup):
        """Find social media links"""
        social_links = {}
        
        social_platforms = {
            'facebook': 'facebook.com',
            'twitter': 'twitter.com',
            'linkedin': 'linkedin.com',
            'instagram': 'instagram.com'
        }
        
        for platform, domain in social_platforms.items():
            links = soup.select(f'a[href*="{domain}"]')
            if links:
                social_links[platform] = links[0].get('href')
        
        return social_links
    
    def save_scraped_data(self, data, filename):
        """Save scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            print(f"Data saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving data: {e}")
    
    def load_scraped_data(self, filename):
        """Load previously scraped data"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            return None