import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timedelta
from typing import Dict

# Handle imports gracefully for deployment
try:
    from tools.weather_api import WeatherTool
    from tools.excel_handler import ExcelHandler
    from tools.excel_product_handler import ExcelProductHandler
    from tools.hireman_scraper import HiremanScraper
    from agents.content_generator import ContentGenerator
    from agents.product_description_generator import ProductDescriptionGenerator
    from memory.memory_system import MemorySystem
    TOOLS_AVAILABLE = True
except ImportError as e:
    TOOLS_AVAILABLE = False
    st.warning(f"Some tools not available: {e}. Running in basic mode.")

# Set page config
st.set_page_config(
    page_title="Marketing AI Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'campaigns' not in st.session_state:
    st.session_state.campaigns = []

# Initialize tools if available
if TOOLS_AVAILABLE:
    try:
        if 'weather_tool' not in st.session_state:
            st.session_state.weather_tool = WeatherTool("")  # Empty API key for demo
        if 'excel_handler' not in st.session_state:
            st.session_state.excel_handler = ExcelHandler()
        if 'excel_product_handler' not in st.session_state:
            st.session_state.excel_product_handler = ExcelProductHandler()
        if 'content_generator' not in st.session_state:
            st.session_state.content_generator = ContentGenerator()
        if 'hireman_scraper' not in st.session_state:
            st.session_state.hireman_scraper = HiremanScraper()
        if 'product_generator' not in st.session_state:
            st.session_state.product_generator = ProductDescriptionGenerator(st.session_state.excel_product_handler)
        if 'memory_system' not in st.session_state:
            st.session_state.memory_system = MemorySystem()
    except Exception as e:
        st.error(f"Error initializing tools: {e}")
        TOOLS_AVAILABLE = False

def main():
    st.title("🎯 Marketing AI Agent")
    st.subheader("Your Intelligent Marketing Assistant")
    
    # Sidebar navigation
    st.sidebar.title("🚀 Navigation")
    page = st.sidebar.selectbox(
        "Choose a function:",
        [
            "Dashboard",
            "New Product Description",
            "Content Generator", 
            "Campaign Planner",
            "Weather Insights",
            "Competitor Monitor",
            "Social Media",
            "Analytics",
            "Settings"
        ]
    )
    
    # Main content based on selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "New Product Description":
        show_new_product_description()
    elif page == "Content Generator":
        show_content_generator()
    elif page == "Campaign Planner":
        show_campaign_planner()
    elif page == "Weather Insights":
        show_weather_insights()
    elif page == "Competitor Monitor":
        show_competitor_monitor()
    elif page == "Social Media":
        show_social_media()
    elif page == "Analytics":
        show_analytics()
    elif page == "Settings":
        show_settings()

def show_dashboard():
    st.header("📊 Dashboard")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Active Campaigns",
            value=len(st.session_state.campaigns),
            delta="2 this week"
        )
    
    with col2:
        st.metric(
            label="Content Generated",
            value="24",
            delta="+8 this month"
        )
    
    with col3:
        st.metric(
            label="Weather Alerts",
            value="3",
            delta="Current week"
        )
    
    with col4:
        st.metric(
            label="ROI Insights",
            value="15%",
            delta="+3% vs last month"
        )
    
    # Recent activity
    st.subheader("📝 Recent Activity")
    if st.session_state.chat_history:
        for i, message in enumerate(st.session_state.chat_history[-5:]):
            with st.expander(f"Activity {i+1} - {message.get('timestamp', 'Unknown time')}"):
                st.write(message.get('content', 'No content'))
    else:
        st.info("No recent activity. Start by generating some content!")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 Generate E-shot", use_container_width=True):
            st.switch_page("Content Generator")
    
    with col2:
        if st.button("🌤️ Check Weather Impact", use_container_width=True):
            st.switch_page("Weather Insights")
    
    with col3:
        if st.button("📱 Create Social Post", use_container_width=True):
            st.switch_page("Social Media")

def show_new_product_description():
    st.header("📝 New Product Description Generator")
    st.subheader("Generate professional product content for thehireman.co.uk")
    
    # CSV file status and information
    st.subheader("📊 WordPress Product Data")
    
    if TOOLS_AVAILABLE and 'excel_product_handler' in st.session_state:
        # Get CSV file information
        csv_info = st.session_state.excel_product_handler.get_csv_info()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if csv_info['file_exists']:
                st.success(f"✅ **CSV File Found**")
                st.write(f"📁 **File:** `{os.path.basename(csv_info['csv_file_path'])}`")
                st.write(f"📊 **Products:** {csv_info['total_products']:,}")
                if csv_info['last_modified']:
                    st.write(f"🕒 **Modified:** {csv_info['last_modified'].strftime('%Y-%m-%d %H:%M')}")
                
                # Show refresh button
                if st.button("🔄 Reload CSV Data"):
                    df = st.session_state.excel_product_handler.load_product_data()
                    st.rerun()
                    
            else:
                st.warning("⚠️ **No CSV File Found**")
                st.write("Please add your WordPress export CSV to:")
                st.code("./data/product_data/")
                st.info("**To export from WordPress:**\n1. Go to Products → All Products\n2. Select products to export\n3. Choose 'Export' from Bulk Actions\n4. Download CSV and place in data folder")
        
        with col2:
            st.info("**CSV Format Expected:**\n- **SKU** - Product stock number\n- **Name/Title** - Product title\n- **Description** - Product description\n- **Meta: technical_specification** - Technical specs")
            
            if csv_info['file_exists'] and csv_info['sample_columns']:
                with st.expander("📋 Available Columns"):
                    for col in csv_info['sample_columns']:
                        st.write(f"• {col}")
    
    st.divider()
    
    # Product code input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        product_code = st.text_input(
            "Product Code", 
            placeholder="e.g., 01/ABC123, 03/XYZ789",
            help="Enter the product code. The prefix (01/, 03/, etc.) determines the category."
        )
    
    with col2:
        st.info("**Code Prefixes:**\n01/ = Access\n03/ = Breaking & Drilling\n12/ = Garden\n13/ = Generators")
    
    # Optional basic information
    st.subheader("📋 Optional Product Information")
    st.write("*Provide any known details to improve generation quality*")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        brand = st.text_input("Brand", placeholder="e.g., Honda, Stihl")
        model = st.text_input("Model", placeholder="e.g., HR194, MS250")
        product_name = st.text_input("Product Name", placeholder="e.g., Rotary Lawnmower")
    
    with col2:
        product_type = st.text_input("Type", placeholder="e.g., Lawnmower, Chainsaw")
        differentiator = st.text_input("Differentiator", placeholder="e.g., Self Propelled, Professional")
        manufacturer_website = st.text_input("Manufacturer Website", placeholder="e.g., https://www.honda.co.uk")
    
    with col3:
        power_type = st.text_input("Power Type", placeholder="e.g., Petrol, Electric")
        power_output = st.text_input("Power/Size", placeholder="e.g., 160cc, 2kW")
    
    # Generate button
    if st.button("🚀 Generate Product Content", type="primary", use_container_width=True):
        if not product_code:
            st.error("Please enter a product code")
            return
        
        # Prepare basic info
        basic_info = {}
        if brand: basic_info['brand'] = brand
        if model: basic_info['model'] = model
        if product_name: basic_info['name'] = product_name
        if product_type: basic_info['type'] = product_type
        if differentiator: basic_info['differentiator'] = differentiator
        if power_type: basic_info['power_type'] = power_type
        if power_output: basic_info['power'] = power_output
        if manufacturer_website: basic_info['manufacturer_website'] = manufacturer_website
        
        # Show progress
        progress_text = "🔍 Analyzing product data"
        if manufacturer_website:
            progress_text += " and manufacturer website"
        progress_text += "..."
        
        with st.spinner(progress_text):
            try:
                if TOOLS_AVAILABLE and 'product_generator' in st.session_state:
                    # Generate content using the real system
                    generated_content = st.session_state.product_generator.generate_product_content(product_code)
                else:
                    # Fallback generation
                    generated_content = generate_mock_product_content(product_code, basic_info)
                
                # Display results
                st.success("✅ WordPress-ready product content generated successfully!")
                
                # Show research summary
                research_sources = generated_content.get('research_sources', {})
                st.info(f"""
                **Research Summary:**
                - Similar products analyzed: {research_sources.get('similar_products_analyzed', 0)}
                - Manufacturer website: {'✅' if research_sources.get('manufacturer_website') else '❌'}
                - Web research completed: {research_sources.get('web_research_completed', 0)} sources
                - Style patterns found: {research_sources.get('style_patterns_found', 0)}
                """)
                
                # Show confidence level
                confidence = generated_content.get('style_confidence', 0.5)
                confidence_percentage = int(confidence * 100)
                
                if confidence >= 0.8:
                    confidence_color = "🟢"
                    confidence_text = "High"
                elif confidence >= 0.6:
                    confidence_color = "🟡"
                    confidence_text = "Medium"
                else:
                    confidence_color = "🔴"
                    confidence_text = "Low"
                
                st.info(f"{confidence_color} **Style Confidence:** {confidence_text} ({confidence_percentage}%)")
                
                # Get WordPress content
                wp_content = generated_content.get('wordpress_content', {})
                
                # WordPress Title
                st.subheader("🏷️ WordPress Title")
                wp_title = wp_content.get('suggested_title', 'Title generation failed')
                st.code(wp_title, language=None)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📋 Copy Title", key="copy_title"):
                        st.success("Title copied!")
                
                # WordPress Description with Key Features
                st.subheader("📄 WordPress Description & Key Features")
                st.write("*Ready to paste directly into WordPress post content:*")
                
                description_with_features = wp_content.get('description_and_features', 'Description generation failed')
                
                # Show formatted version
                with st.expander("👁️ Preview Formatted Description"):
                    st.markdown(description_with_features, unsafe_allow_html=True)
                
                # Show raw HTML for copying
                st.text_area(
                    "Description HTML (copy to WordPress):", 
                    description_with_features, 
                    height=300, 
                    key="wordpress_description"
                )
                
                with col2:
                    if st.button("📋 Copy Description", key="copy_description"):
                        st.success("Description copied!")
                
                # Technical Specifications HTML
                st.subheader("⚙️ Technical Specifications HTML")
                st.write("*Ready to paste directly into WordPress:*")
                
                tech_specs_html = wp_content.get('technical_specifications_html', 'Technical specs generation failed')
                
                # Show formatted version
                with st.expander("👁️ Preview Technical Specifications"):
                    st.markdown(tech_specs_html, unsafe_allow_html=True)
                
                # Show raw HTML for copying
                st.text_area(
                    "Technical Specifications HTML (copy to WordPress):", 
                    tech_specs_html, 
                    height=200, 
                    key="wordpress_tech_specs"
                )
                
                if st.button("📋 Copy Technical Specs", key="copy_tech_specs"):
                    st.success("Technical specifications copied!")
                
                # SEO Meta Description
                st.subheader("🔍 SEO Meta Description")
                meta_desc = wp_content.get('meta_description', 'Meta description generation failed')
                st.code(meta_desc, language=None)
                
                if st.button("📋 Copy Meta Description", key="copy_meta"):
                    st.success("Meta description copied!")
                
                # Key Features List (for reference)
                with st.expander("📋 Key Features List (for reference)"):
                    key_features = wp_content.get('key_features_list', [])
                    for i, feature in enumerate(key_features, 1):
                        st.write(f"{i}. {feature}")
                
                # Usage Instructions
                st.subheader("📝 WordPress Usage Instructions")
                st.info("""
                **How to use this content in WordPress:**
                
                1. **Title:** Copy the suggested title for your post/product title
                2. **Description:** Copy the description HTML directly into your WordPress content editor
                3. **Technical Specs:** Add the technical specifications HTML to your product details section
                4. **Meta Description:** Use for your SEO meta description in Yoast or similar plugins
                
                The HTML is formatted to work with WordPress and will display properly on your website.
                """)
                
                # Export option
                if st.button("💾 Export All Content as JSON", key="export_json"):
                    st.download_button(
                        label="⬇️ Download WordPress Content",
                        data=json.dumps(generated_content, indent=2),
                        file_name=f"wordpress_content_{product_code.replace('/', '_')}.json",
                        mime="application/json"
                    )
                
                st.subheader("🔧 Generated Technical Specifications")
                tech_specs = generated_content.get('technical_specs', {})
                
                if tech_specs:
                    # Display as a formatted table
                    specs_df = pd.DataFrame(list(tech_specs.items()), columns=['Specification', 'Value'])
                    st.dataframe(specs_df, use_container_width=True, hide_index=True)
                    
                    # Also show as copyable text
                    with st.expander("📋 Copyable Specifications Table"):
                        specs_text = "\n".join([f"{key}: {value}" for key, value in tech_specs.items()])
                        st.text_area("Specifications:", specs_text, height=150, key="generated_specs")
                
                # Show manufacturer information if available
                manufacturer_info = generated_content.get('manufacturer_info', {})
                manufacturer_website_link = generated_content.get('manufacturer_website', '')
                
                if manufacturer_info or manufacturer_website_link:
                    st.subheader("🏭 Manufacturer Information")
                    
                    if manufacturer_website_link:
                        st.write(f"**Website:** [{manufacturer_website_link}]({manufacturer_website_link})")
                    
                    if manufacturer_info.get('company_name'):
                        st.write(f"**Company:** {manufacturer_info['company_name']}")
                    
                    if manufacturer_info.get('features'):
                        st.write("**Key Features from Manufacturer:**")
                        for feature in manufacturer_info['features'][:5]:
                            st.write(f"• {feature}")
                    
                    if manufacturer_info.get('error'):
                        st.warning(f"⚠️ Could not fully scrape manufacturer website: {manufacturer_info['error']}")
                
                # Save to memory
                if TOOLS_AVAILABLE and 'memory_system' in st.session_state:
                    st.session_state.memory_system.store_generated_content(
                        'product_description',
                        json.dumps(generated_content),
                        {'product_code': product_code, 'category': generated_content.get('category')}
                    )
                
                # Add to chat history
                st.session_state.chat_history.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'type': 'Product Description Generated',
                    'content': f"Generated WordPress-ready content for {product_code}"
                })
                
            except Exception as e:
                st.error(f"Error generating content: {str(e)}")
                st.write("Please check the product code format and try again.")
                # Show detailed error for debugging
                import traceback
                st.text(traceback.format_exc())
    
    # Show recent generations
    if st.session_state.chat_history:
        recent_products = [item for item in st.session_state.chat_history if item.get('type') == 'Product Description Generated']
        if recent_products:
            st.subheader("📋 Recent Product Descriptions")
            for item in recent_products[-3:]:  # Show last 3
                with st.expander(f"🕒 {item['timestamp']} - {item['content']}"):
                    st.write("Click to view details of previously generated content")

def generate_mock_product_content(product_code: str, basic_info: Dict) -> Dict:
    """Generate mock product content when tools aren't available"""
    
    # Simple category mapping
    category_map = {
        '01': 'Access Equipment',
        '03': 'Breaking & Drilling', 
        '12': 'Garden Equipment',
        '13': 'Generators'
    }
    
    prefix = product_code.split('/')[0] if '/' in product_code else '01'
    category = category_map.get(prefix, 'Equipment')
    
    # Generate mock content
    brand = basic_info.get('brand', 'Professional')
    model = basic_info.get('model', 'Model')
    product_type = basic_info.get('type', category)
    
    title = f"{brand} {model} {product_type}"
    if basic_info.get('differentiator'):
        title += f" - {basic_info['differentiator']}"
    if basic_info.get('power_type'):
        title += f" {basic_info['power_type']}"
    
    description = f"""The {title} is engineered for professional performance and reliability. Built to The Hireman's exacting standards, this {category.lower()} delivers exceptional results for demanding applications.

Designed for both professional contractors and DIY enthusiasts, this equipment combines advanced engineering with user-friendly operation. Whether you're working on construction projects, maintenance tasks, or specialized applications, this {category.lower()} provides the performance and reliability you need.

Available for same-day hire with delivery across London. Our experienced team provides expert advice and support to ensure you get the right equipment for your specific requirements. Contact us today for availability and competitive hire rates."""
    
    tech_specs = {
        'Category': category,
        'Product Code': product_code,
        'Power': basic_info.get('power', 'Professional Grade'),
        'Operation': 'Professional Grade',
        'Availability': 'Same Day Hire',
        'Delivery': 'Available across London',
        'Support': 'Expert advice included'
    }
    
    return {
        'product_code': product_code,
        'category': category,
        'title': title,
        'description': description,
        'technical_specs': tech_specs,
        'style_confidence': 0.7,
        'generated_at': datetime.now().isoformat()
    }

def show_content_generator():
    st.header("✍️ Content Generator")
    
    content_type = st.selectbox(
        "What would you like to create?",
        ["Product Description", "E-shot Campaign", "Social Media Post", "Blog Article"]
    )
    
    if content_type == "Product Description":
        st.subheader("📦 Product Description Generator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("Product Name")
            product_category = st.selectbox(
                "Category",
                ["Construction Equipment", "Garden Tools", "Cleaning Equipment", "Safety Equipment", "Other"]
            )
            key_features = st.text_area("Key Features (one per line)")
        
        with col2:
            target_audience = st.selectbox(
                "Target Audience",
                ["Construction Professionals", "DIY Enthusiasts", "Commercial Cleaners", "General Public"]
            )
            tone = st.selectbox(
                "Tone",
                ["Professional", "Friendly", "Technical", "Promotional"]
            )
            word_count = st.slider("Word Count", 50, 500, 150)
        
        if st.button("Generate Product Description"):
            with st.spinner("Generating product description..."):
                # Placeholder for AI generation
                generated_content = f"""
**{product_name}** - Professional Grade {product_category}

{product_name} represents the pinnacle of {product_category.lower()} technology, designed specifically for {target_audience.lower()}. 

Key Features:
{key_features}

This equipment delivers exceptional performance and reliability, making it the ideal choice for both professional and personal use. Our commitment to quality ensures that every piece of equipment meets the highest industry standards.

Perfect for projects requiring precision and efficiency, {product_name} combines innovative design with practical functionality.
                """
                
                st.success("Product description generated!")
                st.text_area("Generated Content:", generated_content, height=300)
                
                # Add to history
                st.session_state.chat_history.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'type': 'Product Description',
                    'content': generated_content
                })

def show_campaign_planner():
    st.header("📅 Campaign Planner")
    
    st.subheader("Plan Your Marketing Campaigns")
    
    # Campaign type selection
    campaign_type = st.selectbox(
        "Campaign Type",
        ["Seasonal Campaign", "Weather-Based Campaign", "Product Launch", "Promotional Campaign"]
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        campaign_name = st.text_input("Campaign Name")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
    
    with col2:
        target_products = st.multiselect(
            "Target Products",
            ["Water Pumps", "Dehumidifiers", "Heaters", "Garden Equipment", "Construction Tools"]
        )
        budget = st.number_input("Budget (£)", min_value=0, value=1000)
    
    if st.button("Create Campaign Plan"):
        campaign = {
            'name': campaign_name,
            'type': campaign_type,
            'start_date': start_date.strftime("%Y-%m-%d"),
            'end_date': end_date.strftime("%Y-%m-%d"),
            'products': target_products,
            'budget': budget,
            'status': 'Planning'
        }
        
        st.session_state.campaigns.append(campaign)
        st.success(f"Campaign '{campaign_name}' created successfully!")
    
    # Show existing campaigns
    if st.session_state.campaigns:
        st.subheader("📋 Existing Campaigns")
        campaigns_df = pd.DataFrame(st.session_state.campaigns)
        st.dataframe(campaigns_df, use_container_width=True)

def show_weather_insights():
    st.header("🌤️ Weather Insights")
    
    st.info("Weather-based marketing recommendations for London")
    
    # Placeholder weather data
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Temperature", "15°C", "↓2°C")
    with col2:
        st.metric("Humidity", "78%", "↑5%")
    with col3:
        st.metric("Rain Probability", "85%", "↑20%")
    
    st.subheader("📊 Marketing Recommendations")
    
    # Weather-based recommendations
    recommendations = [
        {
            "condition": "Heavy Rain Expected",
            "products": ["Water Pumps", "Dehumidifiers", "Wet Vacuum Cleaners"],
            "action": "Create urgent e-shot campaign",
            "priority": "High"
        },
        {
            "condition": "Cold Weather Coming",
            "products": ["Heaters", "Thermal Equipment", "Insulation Tools"],
            "action": "Plan heating equipment promotion",
            "priority": "Medium"
        }
    ]
    
    for rec in recommendations:
        with st.expander(f"🎯 {rec['condition']} - {rec['priority']} Priority"):
            st.write(f"**Recommended Products:** {', '.join(rec['products'])}")
            st.write(f"**Suggested Action:** {rec['action']}")
            if st.button(f"Generate Campaign for {rec['condition']}", key=rec['condition']):
                st.success("Campaign generated! Check Content Generator.")

def show_competitor_monitor():
    st.header("🔍 Competitor Monitor")
    
    competitors = [
        "Speedy Hire",
        "HSS Hire", 
        "City Hire",
        "National Tool Hire"
    ]
    
    selected_competitor = st.selectbox("Select Competitor", competitors)
    
    if st.button("Analyze Competitor Activity"):
        with st.spinner(f"Analyzing {selected_competitor}..."):
            # Placeholder analysis
            st.success(f"Analysis complete for {selected_competitor}")
            
            analysis_data = {
                "Recent Promotions": ["20% off power tools", "Free delivery promotion"],
                "Popular Products": ["Mini excavators", "Pressure washers", "Generators"],
                "Social Media Activity": "High engagement on LinkedIn posts",
                "Pricing Strategy": "Competitive pricing on weekend rentals"
            }
            
            for category, details in analysis_data.items():
                with st.expander(category):
                    if isinstance(details, list):
                        for detail in details:
                            st.write(f"• {detail}")
                    else:
                        st.write(details)

def show_social_media():
    st.header("📱 Social Media Manager")
    
    platform = st.selectbox("Platform", ["LinkedIn", "Facebook", "Both"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        post_type = st.selectbox(
            "Post Type",
            ["Product Showcase", "Weather Alert", "Promotional", "Educational", "Behind the Scenes"]
        )
        
        product_focus = st.multiselect(
            "Featured Products",
            ["Water Pumps", "Dehumidifiers", "Construction Equipment", "Garden Tools", "Safety Equipment"]
        )
    
    with col2:
        hashtags = st.text_area("Hashtags", "#toolhire #construction #london")
        schedule_time = st.time_input("Schedule for")
    
    post_content = st.text_area("Post Content", height=150, placeholder="AI will generate content based on your selections...")
    
    if st.button("Generate Post"):
        with st.spinner("Generating social media post..."):
            generated_post = f"""
🔧 Looking for reliable {', '.join(product_focus) if product_focus else 'equipment'} hire in London?

Our professional-grade equipment ensures your projects run smoothly, whatever the weather! 

✅ Competitive rates
✅ Same-day availability  
✅ Expert advice included
✅ Delivery across London

Get in touch today! 

{hashtags}
            """
            
            st.success("Post generated!")
            st.text_area("Generated Post:", generated_post, height=200)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Draft"):
                    st.success("Draft saved!")
            with col2:
                if st.button("Schedule Post"):
                    st.success(f"Post scheduled for {schedule_time} on {platform}!")

def show_analytics():
    st.header("📈 Analytics & Performance")
    
    # Placeholder analytics data
    st.subheader("📊 Campaign Performance")
    
    # Sample data for demonstration
    campaign_data = {
        'Campaign': ['Water Pump Promo', 'Winter Heating', 'Spring Garden'],
        'Clicks': [150, 89, 234],
        'Conversions': [12, 8, 19],
        'ROI (%)': [15.2, 12.8, 18.5]
    }
    
    df = pd.DataFrame(campaign_data)
    st.dataframe(df, use_container_width=True)
    
    # Chart
    st.subheader("📈 Performance Trends")
    st.line_chart(df.set_index('Campaign')[['Clicks', 'Conversions']])

def show_settings():
    st.header("⚙️ Settings")
    
    st.subheader("🔧 Configuration")
    
    # API Settings
    with st.expander("API Configuration"):
        weather_api_key = st.text_input("Weather API Key", type="password")
        openai_api_key = st.text_input("OpenAI API Key (Optional)", type="password")
        
        if st.button("Save API Keys"):
            st.success("API keys saved!")
    
    # File Upload Settings
    with st.expander("Data Files"):
        st.write("Upload your business data files:")
        
        tone_file = st.file_uploader("Tone Guidelines Document", type=['txt', 'docx', 'pdf'])
        stock_file = st.file_uploader("Stock Data Spreadsheet", type=['xlsx', 'csv'])
        seasonal_file = st.file_uploader("Seasonal Information", type=['xlsx', 'csv'])
        
        if st.button("Upload Files"):
            st.success("Files uploaded successfully!")
    
    # Website Settings
    with st.expander("Website Configuration"):
        website_url = st.text_input("Your Website URL")
        product_pages = st.text_area("Product Page URLs (one per line)")
        
        if st.button("Save Website Settings"):
            st.success("Website settings saved!")

if __name__ == "__main__":
    main()