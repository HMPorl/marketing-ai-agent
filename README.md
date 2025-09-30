# Marketing AI Agent

A comprehensive marketing automation agent built with Streamlit for equipment hire businesses.

## Features

### Phase 1 - Core Functionality (Current)
- ✅ **Content Generator**: Product descriptions, e-shot campaigns, social media posts
- ✅ **Campaign Planner**: Seasonal and event-based campaign planning
- ✅ **Weather Insights**: Weather-based marketing recommendations for London
- ✅ **Competitor Monitor**: Basic competitor analysis framework
- ✅ **Memory System**: Conversation and campaign history tracking
- ✅ **Analytics Dashboard**: Performance metrics and insights

### Planned Features (Future Phases)
- 🔄 **Website Scraping**: Automatic product information extraction
- 🔄 **Excel Integration**: Stock data and seasonal information processing
- 🔄 **Social Media Posting**: Automated LinkedIn and Facebook posting
- 🔄 **Advanced AI Integration**: LLM-powered content generation
- 🔄 **Competitor Monitoring**: Automated competitor content analysis

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the project** to your desired location

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Open your browser** to the URL shown in the terminal (usually http://localhost:8501)

## Configuration

### API Keys (Optional)
- **Weather API**: Sign up at [OpenWeatherMap](https://openweathermap.org/api) for free weather data
- **OpenAI API**: For advanced AI content generation (optional)

### Data Files
Upload your business data through the Settings page:
- **Tone Guidelines**: Document with your brand voice and common phrases
- **Stock Data**: Excel file with product information, utilization rates, ROI data
- **Seasonal Data**: Information about seasonal product demand patterns

### Website Configuration
- Add your website URL and product page URLs in Settings
- The system will attempt to scrape product information automatically

## Usage

### Dashboard
- View quick stats and recent activity
- Access quick actions for common tasks
- Monitor campaign performance

### Content Generator
- **Product Descriptions**: Generate professional product descriptions
- **E-shot Campaigns**: Create email marketing campaigns
- **Social Media Posts**: Generate platform-specific social content

### Campaign Planner
- Plan seasonal campaigns
- Create weather-triggered campaigns
- Track campaign performance

### Weather Insights
- View current London weather conditions
- Get weather-based product recommendations
- Generate weather-alert campaigns

### Competitor Monitor
- Analyze competitor websites (Speedy Hire, HSS Hire, City Hire, National Tool Hire)
- Track competitor promotions and pricing
- Generate competitive analysis reports

### Social Media Manager
- Create LinkedIn and Facebook posts
- Schedule content (manual scheduling for now)
- Track social media performance

## File Structure

```
marketing_agent/
├── streamlit_app.py          # Main Streamlit application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── agents/
│   └── content_generator.py  # Content generation logic
├── tools/
│   ├── weather_api.py        # Weather data integration
│   ├── web_scraper.py        # Website scraping tools
│   └── excel_handler.py      # Excel file processing
├── memory/
│   └── memory_system.py      # Conversation and campaign memory
└── data/
    ├── product_info/         # Product information storage
    ├── tone_guidelines/      # Brand voice documents
    ├── seasonal_data/        # Seasonal product data
    └── stock_data/          # Stock and ROI information
```

## Zero-Cost Setup

This application is designed to work without paid services:

1. **Local AI Models**: Uses free/open-source models where possible
2. **Free APIs**: Weather data from free tier of OpenWeatherMap
3. **Local Storage**: All data stored locally, no cloud costs
4. **Open Source Tools**: Built entirely with open-source Python libraries

## Development Roadmap

### Phase 2: Enhanced Data Integration
- Advanced Excel processing
- Website scraping automation
- Competitor monitoring automation

### Phase 3: AI Enhancement
- Local LLM integration (Ollama)
- Advanced content generation
- Automated campaign optimization

### Phase 4: Automation & Posting
- Direct social media posting
- Automated campaign execution
- Performance tracking and optimization

### Phase 5: Advanced Analytics
- ROI tracking and analysis
- Predictive campaign performance
- Advanced competitor intelligence

## Troubleshooting

### Common Issues

1. **Module Import Errors**: Ensure all requirements are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Streamlit Not Found**: Install Streamlit globally
   ```bash
   pip install streamlit
   ```

3. **Port Already in Use**: Change the port
   ```bash
   streamlit run streamlit_app.py --server.port 8502
   ```

4. **Excel File Errors**: Ensure Excel files are in .xlsx format

### Getting Help

1. Check the Settings page for configuration issues
2. Review the console output for error messages
3. Ensure all required files are in the correct directories

## Contributing

This is a business-specific application, but suggestions and improvements are welcome:

1. Create feature requests through issues
2. Test the application thoroughly
3. Report bugs with detailed information
4. Suggest new competitor monitoring sources

## License

Internal business use. Not for redistribution.

## Support

For support and questions:
- Check the troubleshooting section
- Review the Settings page for configuration
- Test with sample data first

---

**Next Steps**: Run the application and explore the different features. Start with the Dashboard to get an overview, then try generating some content to see the system in action!