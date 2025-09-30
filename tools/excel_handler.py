import pandas as pd
import openpyxl
import os
from datetime import datetime, timedelta
import logging

class ExcelHandler:
    def __init__(self, data_folder="./data"):
        self.data_folder = data_folder
        self.stock_file = None
        self.seasonal_file = None
        self.tone_file = None
    
    def load_stock_data(self, file_path=None):
        """Load stock/inventory data from Excel file"""
        if file_path:
            self.stock_file = file_path
        elif not self.stock_file:
            # Look for stock files in data folder
            stock_files = self._find_files_by_pattern(['stock', 'inventory', 'products'])
            if stock_files:
                self.stock_file = stock_files[0]
        
        if not self.stock_file or not os.path.exists(self.stock_file):
            return self._create_sample_stock_data()
        
        try:
            # Try reading Excel file
            df = pd.read_excel(self.stock_file, engine='openpyxl')
            return self._process_stock_data(df)
        except Exception as e:
            logging.error(f"Error loading stock data: {e}")
            return self._create_sample_stock_data()
    
    def load_seasonal_data(self, file_path=None):
        """Load seasonal product information"""
        if file_path:
            self.seasonal_file = file_path
        elif not self.seasonal_file:
            seasonal_files = self._find_files_by_pattern(['seasonal', 'season', 'calendar'])
            if seasonal_files:
                self.seasonal_file = seasonal_files[0]
        
        if not self.seasonal_file or not os.path.exists(self.seasonal_file):
            return self._create_sample_seasonal_data()
        
        try:
            df = pd.read_excel(self.seasonal_file, engine='openpyxl')
            return self._process_seasonal_data(df)
        except Exception as e:
            logging.error(f"Error loading seasonal data: {e}")
            return self._create_sample_seasonal_data()
    
    def get_product_insights(self, stock_data):
        """Analyze stock data for marketing insights"""
        insights = []
        
        # High utilization products
        high_util = stock_data[stock_data['utilization_rate'] > 80]
        if not high_util.empty:
            insights.append({
                'type': 'High Demand',
                'products': high_util['product_name'].tolist(),
                'message': 'These products have high utilization - consider promoting alternatives or increasing stock',
                'action': 'Promote similar products or pre-book campaigns'
            })
        
        # Low utilization products
        low_util = stock_data[stock_data['utilization_rate'] < 30]
        if not low_util.empty:
            insights.append({
                'type': 'Low Demand',
                'products': low_util['product_name'].tolist(),
                'message': 'These products have low utilization - good candidates for promotion',
                'action': 'Create targeted marketing campaigns'
            })
        
        # High ROI products
        high_roi = stock_data[stock_data['roi_percentage'] > 15]
        if not high_roi.empty:
            insights.append({
                'type': 'High ROI',
                'products': high_roi['product_name'].tolist(),
                'message': 'These products generate high ROI - prioritize in marketing',
                'action': 'Feature prominently in campaigns'
            })
        
        # Seasonal opportunities
        current_month = datetime.now().month
        seasonal_data = self.load_seasonal_data()
        current_season_products = []
        
        for product in seasonal_data:
            if current_month in product['peak_months']:
                current_season_products.append(product['product_name'])
        
        if current_season_products:
            insights.append({
                'type': 'Seasonal Opportunity',
                'products': current_season_products,
                'message': 'These products are in peak season',
                'action': 'Create seasonal marketing campaigns'
            })
        
        return insights
    
    def get_roi_analysis(self, stock_data):
        """Get ROI analysis for marketing decisions"""
        roi_analysis = {
            'top_performers': stock_data.nlargest(5, 'roi_percentage')[['product_name', 'roi_percentage']].to_dict('records'),
            'underperformers': stock_data.nsmallest(5, 'roi_percentage')[['product_name', 'roi_percentage']].to_dict('records'),
            'category_performance': stock_data.groupby('category')['roi_percentage'].mean().to_dict(),
            'utilization_vs_roi': stock_data[['product_name', 'utilization_rate', 'roi_percentage']].to_dict('records')
        }
        
        return roi_analysis
    
    def get_seasonal_recommendations(self, month=None):
        """Get seasonal marketing recommendations"""
        if month is None:
            month = datetime.now().month
        
        seasonal_data = self.load_seasonal_data()
        recommendations = []
        
        for product in seasonal_data:
            if month in product['peak_months']:
                recommendations.append({
                    'product': product['product_name'],
                    'category': product['category'],
                    'reason': product['seasonal_reason'],
                    'urgency': 'High' if month in product['peak_months'][:2] else 'Medium',
                    'suggested_campaign': self._suggest_campaign_type(product, month)
                })
        
        return recommendations
    
    def save_campaign_results(self, campaign_data, filename=None):
        """Save campaign results to Excel for tracking"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.data_folder}/campaign_results_{timestamp}.xlsx"
        
        try:
            df = pd.DataFrame(campaign_data)
            df.to_excel(filename, index=False, engine='openpyxl')
            return filename
        except Exception as e:
            logging.error(f"Error saving campaign results: {e}")
            return None
    
    def _find_files_by_pattern(self, patterns):
        """Find files matching patterns in data folder"""
        files = []
        if os.path.exists(self.data_folder):
            for file in os.listdir(self.data_folder):
                for pattern in patterns:
                    if pattern.lower() in file.lower() and file.endswith(('.xlsx', '.xls', '.csv')):
                        files.append(os.path.join(self.data_folder, file))
        return files
    
    def _process_stock_data(self, df):
        """Process and standardize stock data"""
        # Standardize column names
        column_mapping = {
            'product': 'product_name',
            'name': 'product_name',
            'item': 'product_name',
            'stock_number': 'stock_id',
            'sku': 'stock_id',
            'utilization': 'utilization_rate',
            'usage': 'utilization_rate',
            'roi': 'roi_percentage',
            'return': 'roi_percentage',
            'category': 'category',
            'type': 'category'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Ensure required columns exist
        required_columns = ['product_name', 'stock_id', 'utilization_rate', 'roi_percentage', 'category']
        for col in required_columns:
            if col not in df.columns:
                df[col] = 0 if col in ['utilization_rate', 'roi_percentage'] else 'Unknown'
        
        return df
    
    def _process_seasonal_data(self, df):
        """Process seasonal data into usable format"""
        seasonal_products = []
        
        for _, row in df.iterrows():
            # Extract peak months (assuming they're in format like "Jan,Feb,Mar" or "1,2,3")
            peak_months = []
            if 'peak_months' in row and pd.notna(row['peak_months']):
                months_str = str(row['peak_months'])
                # Convert month names to numbers
                month_mapping = {
                    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                }
                
                for month in months_str.lower().split(','):
                    month = month.strip()
                    if month in month_mapping:
                        peak_months.append(month_mapping[month])
                    elif month.isdigit():
                        peak_months.append(int(month))
            
            product_data = {
                'product_name': row.get('product_name', row.get('product', 'Unknown')),
                'category': row.get('category', 'Unknown'),
                'peak_months': peak_months,
                'seasonal_reason': row.get('reason', row.get('seasonal_reason', 'Seasonal demand')),
                'weather_dependent': row.get('weather_dependent', False)
            }
            
            seasonal_products.append(product_data)
        
        return seasonal_products
    
    def _suggest_campaign_type(self, product, month):
        """Suggest campaign type based on product and month"""
        if product['weather_dependent']:
            return 'Weather-based Campaign'
        elif month in [11, 12, 1]:  # Winter months
            return 'Winter Promotion'
        elif month in [6, 7, 8]:  # Summer months
            return 'Summer Special'
        elif month in [3, 4, 5]:  # Spring months
            return 'Spring Refresh'
        else:  # Autumn months
            return 'Autumn Preparation'
    
    def _create_sample_stock_data(self):
        """Create sample stock data for demonstration"""
        sample_data = {
            'product_name': [
                'Water Pump - Submersible 2"',
                'Dehumidifier - Industrial 50L',
                'Generator - Diesel 10kVA',
                'Pressure Washer - Hot Water',
                'Mini Excavator - 1.5 Tonne',
                'Floor Sander - Belt Type',
                'Scaffold Tower - Mobile',
                'Concrete Mixer - 350L',
                'Plate Compactor - Diesel',
                'Garden Shredder - Petrol'
            ],
            'stock_id': ['WP001', 'DH002', 'GE003', 'PW004', 'EX005', 'FS006', 'SC007', 'CM008', 'PC009', 'GS010'],
            'category': [
                'Water Management', 'Climate Control', 'Power Generation', 'Cleaning Equipment',
                'Construction Equipment', 'Surface Preparation', 'Access Equipment', 
                'Concrete Equipment', 'Compaction Equipment', 'Garden Equipment'
            ],
            'utilization_rate': [85, 45, 70, 60, 90, 35, 75, 80, 65, 25],
            'roi_percentage': [18.5, 12.3, 22.1, 15.7, 25.8, 8.9, 16.4, 19.2, 14.6, 6.5],
            'daily_rate': [45, 35, 85, 55, 120, 25, 40, 65, 50, 30]
        }
        
        return pd.DataFrame(sample_data)
    
    def _create_sample_seasonal_data(self):
        """Create sample seasonal data for demonstration"""
        return [
            {
                'product_name': 'Water Pump - Submersible 2"',
                'category': 'Water Management',
                'peak_months': [10, 11, 12, 1, 2],  # Oct-Feb (wet season)
                'seasonal_reason': 'High demand during wet weather months',
                'weather_dependent': True
            },
            {
                'product_name': 'Dehumidifier - Industrial 50L',
                'category': 'Climate Control',
                'peak_months': [11, 12, 1, 2],  # Winter months
                'seasonal_reason': 'High humidity in winter months',
                'weather_dependent': True
            },
            {
                'product_name': 'Garden Shredder - Petrol',
                'category': 'Garden Equipment',
                'peak_months': [9, 10, 11],  # Autumn months
                'seasonal_reason': 'Autumn leaf clearance season',
                'weather_dependent': False
            },
            {
                'product_name': 'Generator - Diesel 10kVA',
                'category': 'Power Generation',
                'peak_months': [11, 12, 1, 2],  # Winter months
                'seasonal_reason': 'Winter events and heating backup',
                'weather_dependent': False
            },
            {
                'product_name': 'Concrete Mixer - 350L',
                'category': 'Concrete Equipment',
                'peak_months': [3, 4, 5, 6, 7, 8],  # Spring/Summer
                'seasonal_reason': 'Construction season peak',
                'weather_dependent': True
            }
        ]