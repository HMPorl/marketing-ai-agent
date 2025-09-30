# Marketing AI Agent Configuration

# API Keys (will be set through Streamlit interface)
WEATHER_API_KEY=""
OPENAI_API_KEY=""

# Competitor URLs
COMPETITORS = {
    "Speedy Hire": "https://www.speedyhire.co.uk",
    "HSS Hire": "https://www.hss.com",
    "City Hire": "https://www.cityhire.co.uk", 
    "National Tool Hire": "https://www.nationaltoolhire.com"
}

# Weather location
WEATHER_LOCATION = "London,UK"

# Social Media Settings
SOCIAL_PLATFORMS = ["LinkedIn", "Facebook"]

# Default tone and style
DEFAULT_TONE = "professional_friendly"

# File paths
DATA_PATHS = {
    "tone_guidelines": "./data/tone_guidelines/",
    "stock_data": "./data/stock_data/",
    "seasonal_data": "./data/seasonal_data/",
    "product_info": "./data/product_info/"
}

# Product categories
PRODUCT_CATEGORIES = [
    "Construction Equipment",
    "Garden Tools", 
    "Cleaning Equipment",
    "Safety Equipment",
    "Power Tools",
    "Access Equipment",
    "Lifting Equipment",
    "Heating & Cooling",
    "Water Management",
    "Compaction Equipment"
]