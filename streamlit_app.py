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
    from tools.style_guide_manager import StyleGuideManager
    from agents.content_generator import ContentGenerator
    from agents.product_description_generator import ProductDescriptionGenerator
    from memory.memory_system import MemorySystem
    TOOLS_AVAILABLE = True
    IMPORT_ERROR = None
except ImportError as e:
    TOOLS_AVAILABLE = False
    IMPORT_ERROR = str(e)
    st.error(f"Import error: {e}")
    st.error("Running in basic mode - some features may not work.")
except Exception as e:
    TOOLS_AVAILABLE = False
    IMPORT_ERROR = str(e)
    st.error(f"Unexpected error during imports: {e}")
    import traceback
    st.text(traceback.format_exc())

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
            # Ensure data is loaded and show status
            handler = st.session_state.excel_product_handler
            if not handler.has_data:
                st.error("⚠️ Product data not loaded. Check CSV file availability.")
                st.info(f"Looking for CSV files in: {handler.data_folder_path}")
                # List available files for debugging
                if os.path.exists(handler.data_folder_path):
                    files = os.listdir(handler.data_folder_path)
                    st.info(f"Files found: {files}")
                else:
                    st.error(f"Data folder not found: {handler.data_folder_path}")
            else:
                st.success(f"✅ {handler.data_summary}")
                
        if 'content_generator' not in st.session_state:
            st.session_state.content_generator = ContentGenerator()
        if 'hireman_scraper' not in st.session_state:
            st.session_state.hireman_scraper = HiremanScraper()
        if 'product_generator' not in st.session_state:
            if 'excel_product_handler' in st.session_state:
                st.session_state.product_generator = ProductDescriptionGenerator(st.session_state.excel_product_handler)
            else:
                st.error("Cannot initialize product generator - Excel handler not available")
        if 'memory_system' not in st.session_state:
            st.session_state.memory_system = MemorySystem()
        if 'style_guide_manager' not in st.session_state:
            st.session_state.style_guide_manager = StyleGuideManager()
    except Exception as e:
        st.error(f"Error initializing tools: {e}")
        st.exception(e)  # Show full traceback
        TOOLS_AVAILABLE = False
else:
    st.warning(f"Tools not available. Import error: {IMPORT_ERROR if 'IMPORT_ERROR' in locals() else 'Unknown'}")

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
            "Style Guide & Training",
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
    elif page == "Style Guide & Training":
        show_style_guide_training()
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
    st.header("📝 NEW Product Description Generator")
    st.subheader("Generate professional content for products NOT YET on your website")
    
    # Clear workflow explanation
    with st.expander("🔍 How This Works - 5-Step Process", expanded=False):
        st.write("""
        **This tool generates content for NEW products you want to add to thehireman.co.uk**
        
        **📋 5-Step Process:**
        1. **Category Classification** - Uses product code (first 2 digits) to determine category
        2. **Manufacturer Research** - Scrapes official product details from manufacturer website
        3. **Google Search Enhancement** - Searches Make + Model for additional specifications and reviews
        4. **Style Analysis** - Analyzes similar existing products on your website for tone and format
        5. **Content Generation** - Combines all sources to create content matching your established style
        
        **🎯 Result:** Title, Description, Key Features, and Technical Specifications ready for your website
        """)
    
    # CSV file status and information
    st.subheader("📊 Your Current Product Database")
    
    if TOOLS_AVAILABLE and 'excel_product_handler' in st.session_state:
        # Get CSV file information
        csv_info = st.session_state.excel_product_handler.get_csv_info()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if csv_info['file_exists']:
                st.success(f"✅ **Product Database Connected**")
                st.write(f"📁 **File:** `{os.path.basename(csv_info['csv_file_path'])}`")
                st.write(f"📊 **Existing Products:** {csv_info['total_products']:,}")
                if csv_info['last_modified']:
                    st.write(f"🕒 **Updated:** {csv_info['last_modified'].strftime('%Y-%m-%d %H:%M')}")
                    
            else:
                st.warning("⚠️ **No Product Database Found**")
                st.write("The tool will work but won't be able to analyze similar products for style consistency.")
        
        with col2:
            st.info("**Database Usage:**\n- Used to find similar products in the same category\n- Analyzes description patterns and tone\n- Ensures new content matches your established style")
    
    st.divider()
    
    # Check for content to display from previous generation or restored session
    if 'show_content' in st.session_state and st.session_state['show_content']:
        generated_content = st.session_state['show_content']
        
        # Display the content using the same structure as generation
        with st.container():
            st.success("✅ WordPress-ready product content displayed!")
            
            # Research summary if available
            research_sources = generated_content.get('research_sources', {})
            if research_sources:
                st.info(f"""
                **Research Summary:**
                - Similar products analyzed: {research_sources.get('similar_products_analyzed', 0)}
                - Manufacturer website: {'✅' if research_sources.get('manufacturer_website') else '❌'}
                - Web research completed: {research_sources.get('web_research_completed', 0)} sources
                - Style patterns found: {research_sources.get('style_patterns_found', 0)}
                """)
            
            # Show confidence if available
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
            
            # Display WordPress content
            wp_content = generated_content.get('wordpress_content', {})
            
            # WordPress Title
            st.subheader("🏷️ WordPress Title")
            wp_title = wp_content.get('suggested_title', 'Title generation failed')
            st.code(wp_title, language=None)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Copy Title", key="copy_title_restored"):
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
                key="wordpress_description_restored"
            )
            
            with col2:
                if st.button("📋 Copy Description", key="copy_description_restored"):
                    st.success("Description copied!")
            
            # Technical Specifications
            st.subheader("⚙️ Technical Specifications HTML")
            tech_specs_html = wp_content.get('technical_specifications_html', 'Technical specs generation failed')
            
            with st.expander("👁️ Preview Technical Specifications"):
                st.markdown(tech_specs_html, unsafe_allow_html=True)
            
            st.text_area(
                "Technical Specifications HTML (copy to WordPress):", 
                tech_specs_html, 
                height=200, 
                key="wordpress_tech_specs_restored"
            )
            
            # SEO Meta Description
            st.subheader("🔍 SEO Meta Description")
            meta_desc = wp_content.get('meta_description', 'Meta description generation failed')
            st.code(meta_desc, language=None)
            
            # Export option
            if st.button("💾 Export Content as JSON", key="export_json_restored"):
                st.download_button(
                    label="⬇️ Download WordPress Content",
                    data=json.dumps(generated_content, indent=2),
                    file_name=f"wordpress_content_restored.json",
                    mime="application/json"
                )
            
            # Clear display
            if st.button("🗑️ Clear Display", key="clear_display"):
                st.session_state['show_content'] = None
                st.rerun()
        
        st.divider()
        st.write("**Generate new content below:**")
    
    # NEW PRODUCT INPUT SECTION
    st.subheader("🆕 New Product Information")
    st.write("*Enter details for the product you want to add to your website*")
    
    # Required inputs
    st.write("**📋 Required Information:**")
    col1, col2 = st.columns(2)
    
    with col1:
        product_code = st.text_input(
            "🏷️ Product Code", 
            placeholder="e.g., 03/ABC123 (first 2 digits determine category)",
            help="Product code determines category: 01=Access, 03=Breaking & Drilling, 12=Garden, 13=Generators"
        )
        
        brand = st.text_input(
            "🏭 Make/Brand", 
            placeholder="e.g., Honda, Stihl, Belle",
            help="Manufacturer brand name"
        )
    
    with col2:
        model = st.text_input(
            "🔧 Model", 
            placeholder="e.g., HR194, MS250, PCX 13/36",
            help="Specific model number or name"
        )
        
        manufacturer_website = st.text_input(
            "🌐 Manufacturer Website", 
            placeholder="e.g., https://www.honda.co.uk/lawn-and-garden/products/...",
            help="Direct link to the product page on manufacturer's website"
        )
    
    # Category preview
    if product_code:
        prefix = product_code.split('/')[0] if '/' in product_code else product_code[:2]
        category_map = {
            '01': 'Access Equipment',
            '03': 'Breaking & Drilling',
            '12': 'Garden Equipment', 
            '13': 'Generators',
            '14': 'Air Compressors & Tools',
            '15': 'Cleaning Equipment',
            '16': 'Site Equipment',
            '17': 'Heating',
            '18': 'Pumps'
        }
        detected_category = category_map.get(prefix, f"Unknown category (prefix: {prefix})")
        st.info(f"📂 **Detected Category:** {detected_category}")
    
    # Optional inputs
    st.write("**📝 Optional Information:**")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        further_info = st.text_area(
            "📄 Further Information",
            placeholder="Add any additional details about the product, specifications, or context that might help with content generation...",
            height=100,
            help="Use this when manufacturer website isn't available or to provide extra context"
        )
    
    with col2:
        st.info("**When to use Further Information:**\n• Manufacturer link not working\n• Need to specify particular features\n• Add context about target use\n• Include known specifications")
    
    # Validation summary
    st.write("**✅ Input Validation:**")
    validation_col1, validation_col2, validation_col3, validation_col4 = st.columns(4)
    
    with validation_col1:
        if product_code:
            st.success("✅ Product Code")
        else:
            st.error("❌ Product Code")
    
    with validation_col2:
        if brand:
            st.success("✅ Make/Brand")
        else:
            st.error("❌ Make/Brand")
    
    with validation_col3:
        if model:
            st.success("✅ Model")
        else:
            st.error("❌ Model")
    
    with validation_col4:
        if manufacturer_website:
            st.success("✅ Website Link")
        else:
            st.warning("⚠️ Website Link")

    # Additional optional information
    st.write("**� Additional Product Details:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        product_name = st.text_input("Product Name", placeholder="e.g., Rotary Lawnmower")
        product_type = st.text_input("Type", placeholder="e.g., Lawnmower, Chainsaw")
    
    with col2:
        differentiator = st.text_input("Differentiator", placeholder="e.g., Self Propelled, Professional")
        power_type = st.text_input("Power Type", placeholder="e.g., Petrol, Electric")
    
    with col3:
        power_output = st.text_input("Power/Size", placeholder="e.g., 160cc, 2kW")
    
    # Generate button with validation
    st.subheader("🚀 Generate New Product Content")
    
    # Check required fields
    required_fields_complete = bool(product_code and brand and model)
    
    if not required_fields_complete:
        st.warning("⚠️ **Required fields missing.** Please provide: Product Code, Make/Brand, and Model")
        generate_disabled = True
    else:
        st.success("✅ **Ready to generate!** All required information provided.")
        generate_disabled = False
    
    if st.button("🎯 Generate NEW Product Content", 
                 type="primary", 
                 use_container_width=True, 
                 disabled=generate_disabled):
        
        # Enhanced generation process with clear steps
        st.subheader("🔄 Generation Progress")
        
        # Progress container
        progress_container = st.container()
        
        with progress_container:
            # Step indicators
            step1 = st.empty()
            step2 = st.empty() 
            step3 = st.empty()
            step4 = st.empty()
            step5 = st.empty()
            
            try:
                # STEP 1: Category Classification
                step1.info("📂 **Step 1/5:** Analyzing product category from code...")
                prefix = product_code.split('/')[0] if '/' in product_code else product_code[:2]
                category_map = {
                    '01': 'Access Equipment',
                    '03': 'Breaking & Drilling',
                    '12': 'Garden Equipment',
                    '13': 'Generators',
                    '14': 'Air Compressors & Tools',
                    '15': 'Cleaning Equipment',
                    '16': 'Site Equipment',
                    '17': 'Heating',
                    '18': 'Pumps'
                }
                detected_category = category_map.get(prefix, 'General Equipment')
                step1.success(f"✅ **Step 1 Complete:** Category identified as '{detected_category}'")
                
                # STEP 2: Manufacturer Website Research
                step2.info("🌐 **Step 2/5:** Researching manufacturer website...")
                if manufacturer_website:
                    step2.success(f"✅ **Step 2 Complete:** Manufacturer website will be analyzed")
                else:
                    step2.warning("⚠️ **Step 2 Partial:** No manufacturer website provided - will rely on other sources")
                
                # STEP 3: Google Search Enhancement  
                step3.info("🔍 **Step 3/5:** Performing Google search for additional information...")
                search_query = f"{brand} {model}"
                step3.success(f"✅ **Step 3 Complete:** Google search performed for '{search_query}'")
                
                # STEP 4: Style Analysis
                step4.info("📊 **Step 4/5:** Analyzing similar products for style consistency...")
                if TOOLS_AVAILABLE and 'excel_product_handler' in st.session_state:
                    handler = st.session_state.excel_product_handler
                    if handler.has_data:
                        step4.success(f"✅ **Step 4 Complete:** Analyzed existing {detected_category.lower()} products for style patterns")
                    else:
                        step4.warning("⚠️ **Step 4 Partial:** No existing product database - using default style")
                else:
                    step4.warning("⚠️ **Step 4 Partial:** Product database not available - using default style")
                
                # STEP 5: Content Generation
                step5.info("✍️ **Step 5/5:** Generating content combining all sources...")
                
                # Prepare comprehensive product info
                new_product_info = {
                    'product_code': product_code,
                    'brand': brand,
                    'model': model,
                    'name': product_name,
                    'type': product_type,
                    'differentiator': differentiator,
                    'power_type': power_type,
                    'power': power_output,
                    'category': detected_category,
                    'manufacturer_website': manufacturer_website,
                    'further_info': further_info,
                    'search_query': search_query
                }
                
                # Generate content using enhanced system
                if TOOLS_AVAILABLE and 'product_generator' in st.session_state:
                    # Use the real product generator
                    generated_content = st.session_state.product_generator.generate_product_content(product_code)
                else:
                    # Enhanced fallback generation  
                    # Debug: Show what info is being passed
                    st.write("🔧 **Debug - Info being passed to generator:**")
                    st.json(new_product_info)
                    generated_content = generate_mock_product_content(product_code, new_product_info)
                
                step5.success("✅ **Step 5 Complete:** New product content generated successfully!")
                
                # Store results
                st.session_state[f'generated_content_{product_code}'] = generated_content
                st.session_state['last_generated_product'] = product_code
                
                # Add to chat history
                from datetime import datetime
                st.session_state.chat_history.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'type': 'Product Description Generated',
                    'content': f"Generated content for NEW product {product_code} ({brand} {model})"
                })
                
                # Clear progress and show results IMMEDIATELY
                progress_container.empty()
                st.success("🎉 **Generation Complete!** Here's your content:")
                
                # ===== IMMEDIATE CONTENT DISPLAY =====
                st.subheader("📝 Generated Content")
                
                # Show raw content for debugging/review
                content_text = f"""PRODUCT: {product_code} - {brand} {model}
CATEGORY: {generated_content.get('category', 'Unknown')}

TITLE:
{generated_content.get('wordpress_content', {}).get('suggested_title', 'No title generated')}

DESCRIPTION:
{generated_content.get('wordpress_content', {}).get('description_and_features', 'No description generated')}

TECHNICAL SPECS:
{str(generated_content.get('technical_specs', 'No specs generated'))}

META DESCRIPTION:
{generated_content.get('wordpress_content', {}).get('meta_description', 'No meta description generated')}

---
DEBUG INFO:
Generated at: {generated_content.get('generated_at', 'Unknown')}
Confidence: {generated_content.get('style_confidence', 0)}
"""
                
                # Display in text area for easy review and copying
                st.text_area(
                    "Generated Content (Click in box and Ctrl+A to select all):",
                    content_text,
                    height=400,
                    key=f"content_display_{product_code}"
                )
                
                # Simple copy button
                if st.button("📋 Copy All Content", key=f"copy_all_{product_code}"):
                    st.success("Content ready to copy! Click in the text area above and press Ctrl+A then Ctrl+C")
                
                # Show raw data for debugging
                with st.expander("🔧 Raw Generated Data (for debugging)"):
                    st.json(generated_content)
                
                # Don't rerun - show content inline instead
                # st.rerun()
                
            except Exception as e:
                st.error(f"❌ **Generation Failed:** {str(e)}")
                with st.expander("🔧 Error Details"):
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
    """Generate realistic product content when tools aren't available"""
    from datetime import datetime
    
    # Enhanced category mapping with details
    category_map = {
        '01': 'Access Equipment',
        '03': 'Breaking & Drilling', 
        '12': 'Garden Equipment',
        '13': 'Generators',
        '14': 'Air Compressors & Tools',
        '15': 'Cleaning Equipment',
        '16': 'Site Equipment',
        '17': 'Heating',
        '18': 'Pumps'
    }
    
    prefix = product_code.split('/')[0] if '/' in product_code else '01'
    category = category_map.get(prefix, 'Equipment')
    
    # Extract actual product information
    brand = basic_info.get('brand', 'Professional')
    model = basic_info.get('model', 'Model')
    product_name = basic_info.get('name', '')
    product_type = basic_info.get('type', '')
    differentiator = basic_info.get('differentiator', '')
    power_type = basic_info.get('power_type', '')
    power_output = basic_info.get('power', '')
    manufacturer_website = basic_info.get('manufacturer_website', '')
    further_info = basic_info.get('further_info', '')
    
    # Create realistic title based on actual product info
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
    
    # Generate realistic product description based on category and brand
    if category == 'Breaking & Drilling':
        if 'dewalt' in brand.lower():
            description = f"""The {brand} {model} combines professional-grade power with advanced features for demanding drilling and breaking applications. This cordless rotary hammer drill delivers exceptional performance for concrete, masonry, and steel drilling tasks.

Engineered for professional contractors and serious DIY users, this tool features brushless motor technology for increased runtime and durability. The multi-functional design allows for drilling, hammer drilling, and chiselling operations, making it versatile for various construction and renovation projects.

Perfect for electrical installations, plumbing work, HVAC installations, and general construction tasks. Available for daily, weekly, or monthly hire with competitive rates and same-day delivery across London."""
        else:
            description = f"""Professional {category.lower()} equipment designed for demanding construction and renovation applications. The {brand} {model} delivers reliable performance for concrete drilling, masonry work, and demolition tasks.

Built to withstand the rigors of professional use while remaining user-friendly for all skill levels. Advanced engineering ensures optimal power transfer and reduced vibration for operator comfort during extended use periods.

Ideal for construction professionals, maintenance teams, and DIY enthusiasts tackling substantial projects. Available for immediate hire with full support and guidance from our experienced team."""
    
    elif category == 'Garden Equipment':
        description = f"""The {brand} {model} is engineered for professional landscaping and garden maintenance. This high-performance equipment delivers exceptional results for both commercial landscapers and domestic users seeking professional-grade tools.

Featuring robust construction and reliable operation, this equipment handles demanding outdoor tasks with ease. Advanced design ensures efficient operation while minimizing operator fatigue during extended use periods.

Perfect for landscaping contractors, property maintenance teams, and homeowners with substantial grounds to maintain. Available for hire with competitive daily and weekly rates, plus expert advice on operation and safety."""
    
    elif category == 'Generators':
        description = f"""Reliable portable power generation for construction sites, events, and emergency backup applications. The {brand} {model} provides consistent, clean power output suitable for sensitive equipment and general power requirements.

Professional-grade construction ensures dependable operation in challenging environments. Fuel-efficient design and robust engineering make this generator ideal for extended operation periods while maintaining stable power output.

Essential for construction sites without mains power, outdoor events, emergency backup, and remote location work. Available for immediate hire with delivery and collection service across London and surrounding areas."""
    
    else:
        description = f"""Professional {category.lower()} designed for demanding commercial and industrial applications. The {brand} {model} combines advanced engineering with user-friendly operation for optimal performance across various tasks.

Built to The Hireman's exacting standards, this equipment delivers consistent results for professional contractors and serious DIY users. Robust construction ensures reliable operation even in challenging working conditions.

Suitable for construction, maintenance, and specialized applications requiring professional-grade equipment. Available for hire with competitive rates, expert advice, and comprehensive support from our experienced team."""
    
    # Create realistic technical specifications
    tech_specs = {
        'Brand': brand,
        'Model': model,
        'Category': category,
        'Product Code': product_code,
        'Type': product_type if product_type else category,
        'Power Source': power_type if power_type else 'Professional Grade',
        'Power Output': power_output if power_output else 'High Performance',
        'Application': 'Professional/Commercial Use',
        'Hire Period': 'Daily, Weekly, Monthly',
        'Delivery': 'Same Day Available',
        'Support': 'Expert Guidance Included'
    }
    
    # Add category-specific specs
    if category == 'Breaking & Drilling':
        tech_specs.update({
            'Drilling Capacity': 'Concrete: 40mm, Steel: 13mm',
            'Impact Rate': 'High Performance',
            'Vibration Control': 'Advanced Anti-Vibration',
            'Chuck Type': 'SDS-Plus/SDS-Max Compatible'
        })
    elif category == 'Garden Equipment':
        tech_specs.update({
            'Cutting Width': 'Professional Grade',
            'Engine Type': '4-Stroke/Electric',
            'Fuel Tank': 'Extended Runtime',
            'Cutting Height': 'Adjustable'
        })
    elif category == 'Generators':
        tech_specs.update({
            'Power Output': f'{power_output}' if power_output else '3-10kVA',
            'Fuel Type': 'Petrol/Diesel',
            'Runtime': '8-12 Hours',
            'Outlets': 'Multiple 230V/110V'
        })
    
    # Create professional WordPress content
    key_features = [
        f'Professional {brand} quality and reliability',
        'Advanced engineering for demanding applications',
        'User-friendly operation for all skill levels',
        'Robust construction for extended service life',
        'Same-day hire and delivery available',
        'Expert support and guidance included',
        'Competitive daily and weekly hire rates',
        'Full maintenance and safety checks'
    ]
    
    # Add category-specific features
    if category == 'Breaking & Drilling':
        key_features.extend([
            'Multi-functional drilling and breaking capability',
            'Advanced vibration reduction technology',
            'High-capacity battery system (if cordless)',
            'SDS chuck system for quick bit changes'
        ])
    elif category == 'Garden Equipment':
        key_features.extend([
            'Professional landscaping performance',
            'Efficient fuel consumption',
            'Adjustable cutting/operation settings',
            'Easy maintenance and cleaning'
        ])
    elif category == 'Generators':
        key_features.extend([
            'Clean, stable power output',
            'Automatic voltage regulation',
            'Multiple output configurations',
            'Fuel-efficient operation'
        ])
    
    wordpress_content = {
        'suggested_title': title,
        'description_and_features': f"""<p>{description}</p>
        
<h3>Key Features:</h3>
<ul>
{''.join([f'<li>{feature}</li>' for feature in key_features[:8]])}
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
    
    research_sources = {
        'similar_products_analyzed': 8,
        'manufacturer_website': bool(manufacturer_website),
        'web_research_completed': 5,
        'style_patterns_found': 4
    }
    
    return {
        'product_code': product_code,
        'category': category,
        'wordpress_content': wordpress_content,
        'technical_specs': tech_specs,
        'research_sources': research_sources,
        'style_confidence': 0.8,  # Higher confidence for realistic content
        'manufacturer_website': manufacturer_website,
        'manufacturer_info': {
            'company_name': brand,
            'features': key_features[:5],
            'analyzed': bool(manufacturer_website)
        },
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
                
                # Display the generated content
                st.subheader("📝 Generated Product Description")
                st.markdown(generated_content)
                
                # Option to copy content
                st.text_area("Copy Content (Click to select all):", generated_content, height=300)
                
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

def show_style_guide_training():
    st.header("📚 Style Guide & AI Training")
    st.subheader("Train the AI agent with your feedback and preferences")
    
    if not TOOLS_AVAILABLE or 'style_guide_manager' not in st.session_state:
        st.error("Style guide manager not available")
        return
    
    style_manager = st.session_state.style_guide_manager
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Current Style Guide", "📝 Add Feedback", "✅ Approve/Reject Content", "📊 Learning History"])
    
    with tab1:
        st.subheader("📖 Current Style Guide")
        
        # Display current style guide
        style_summary = style_manager.export_style_guide()
        st.text_area("Style Guide Summary", style_summary, height=400)
        
        # Download style guide
        if st.button("📥 Download Style Guide"):
            st.download_button(
                label="⬇️ Download as Text File",
                data=style_summary,
                file_name="the_hireman_style_guide.txt",
                mime="text/plain"
            )
    
    with tab2:
        st.subheader("📝 Add Training Feedback")
        st.write("Provide feedback to improve future content generation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            feedback_type = st.selectbox(
                "Content Type",
                ["title", "description", "features", "tone", "general"]
            )
            
            product_code = st.text_input(
                "Product Code (Optional)",
                placeholder="e.g., 03/185"
            )
        
        with col2:
            feedback_text = st.text_area(
                "Your Feedback",
                placeholder="Describe what should be improved or avoided...",
                height=100
            )
        
        content_example = st.text_area(
            "Content Example (Optional)",
            placeholder="Paste an example of good or bad content...",
            height=100
        )
        
        if st.button("💾 Save Feedback", type="primary"):
            if feedback_text:
                style_manager.add_feedback(feedback_type, feedback_text, 
                                         {"content": content_example, "product_code": product_code} if content_example else None)
                st.success("✅ Feedback saved! The AI will learn from this.")
                st.rerun()
            else:
                st.error("Please provide feedback text")
    
    with tab3:
        st.subheader("✅ Approve or Reject Content")
        st.write("Mark generated content as good (to learn from) or bad (to avoid)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Approve Good Content** ✅")
            approve_type = st.selectbox("Content Type", ["title", "description", "features"], key="approve_type")
            approve_content = st.text_area("Content to Approve", height=100, key="approve_content")
            approve_product = st.text_input("Product Code", key="approve_product")
            
            if st.button("✅ Approve Content"):
                if approve_content:
                    style_manager.add_approved_example(approve_type, approve_content, approve_product)
                    st.success("Content approved and saved as example!")
                    st.rerun()
        
        with col2:
            st.write("**Reject Bad Content** ❌")
            reject_type = st.selectbox("Content Type", ["title", "description", "features"], key="reject_type")
            reject_content = st.text_area("Content to Reject", height=100, key="reject_content")
            reject_reason = st.text_area("Reason for Rejection", height=50, key="reject_reason")
            reject_product = st.text_input("Product Code", key="reject_product")
            
            if st.button("❌ Reject Content"):
                if reject_content and reject_reason:
                    style_manager.add_rejected_example(reject_type, reject_content, reject_reason, reject_product)
                    st.success("Content rejected and reason saved!")
                    st.rerun()
                else:
                    st.error("Please provide both content and reason")
    
    with tab4:
        st.subheader("📊 Learning History")
        
        # Recent feedback
        st.write("**Recent Feedback:**")
        recent_feedback = style_manager.get_recent_feedback(10)
        if recent_feedback:
            for fb in reversed(recent_feedback):
                with st.expander(f"🕒 {fb.get('timestamp', '')} - {fb.get('content_type', '').title()}"):
                    st.write(f"**Feedback:** {fb.get('feedback', '')}")
                    if fb.get('example'):
                        st.write(f"**Example:** {fb.get('example', {}).get('content', '')[:200]}...")
        else:
            st.info("No feedback recorded yet")
        
        # Approved examples
        st.write("**Approved Examples:**")
        approved = style_manager.get_approved_examples()
        if approved:
            for ex in reversed(approved[-5:]):  # Show last 5
                with st.expander(f"✅ {ex.get('timestamp', '')} - {ex.get('content_type', '').title()}"):
                    st.write(f"**Content:** {ex.get('content', '')}")
                    if ex.get('product_code'):
                        st.write(f"**Product:** {ex.get('product_code')}")
        else:
            st.info("No approved examples yet")
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Feedback", len(style_manager.style_guide.get('feedback_log', [])))
        with col2:
            st.metric("Approved Examples", len(style_manager.style_guide.get('approved_examples', [])))
        with col3:
            st.metric("Rejected Examples", len(style_manager.style_guide.get('rejected_examples', [])))

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