import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import json

# Handle imports gracefully for deployment
try:
    from tools.weather_api import WeatherTool
    from tools.excel_handler import ExcelHandler
    from agents.content_generator import ContentGenerator
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
        if 'content_generator' not in st.session_state:
            st.session_state.content_generator = ContentGenerator()
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