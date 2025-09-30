import requests
import json
from datetime import datetime, timedelta

class WeatherTool:
    def __init__(self, api_key, location="London,UK"):
        self.api_key = api_key
        self.location = location
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self):
        """Get current weather conditions"""
        if not self.api_key:
            return self._mock_weather_data()
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': self.location,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_weather_data(data)
            
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return self._mock_weather_data()
    
    def get_forecast(self, days=5):
        """Get weather forecast"""
        if not self.api_key:
            return self._mock_forecast_data(days)
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': self.location,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_forecast_data(data)
            
        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return self._mock_forecast_data(days)
    
    def get_marketing_recommendations(self):
        """Get marketing recommendations based on weather"""
        current = self.get_current_weather()
        forecast = self.get_forecast(3)
        
        recommendations = []
        
        # Check for rain
        if current['rain_probability'] > 70 or any(day['rain_probability'] > 70 for day in forecast):
            recommendations.append({
                'condition': 'Heavy Rain Expected',
                'products': ['Water Pumps', 'Dehumidifiers', 'Wet Vacuum Cleaners', 'Drainage Equipment'],
                'urgency': 'High',
                'message': 'Heavy rain expected - promote water management equipment',
                'campaign_type': 'Weather Alert'
            })
        
        # Check for cold weather
        if current['temperature'] < 5 or any(day['temperature'] < 5 for day in forecast):
            recommendations.append({
                'condition': 'Cold Weather Alert',
                'products': ['Heaters', 'Thermal Equipment', 'Insulation Tools', 'Hot Air Guns'],
                'urgency': 'Medium',
                'message': 'Cold weather approaching - heating equipment in demand',
                'campaign_type': 'Seasonal'
            })
        
        # Check for hot weather
        if current['temperature'] > 25 or any(day['temperature'] > 25 for day in forecast):
            recommendations.append({
                'condition': 'Hot Weather',
                'products': ['Cooling Fans', 'Air Conditioning Units', 'Shade Equipment'],
                'urgency': 'Medium',
                'message': 'Hot weather expected - cooling equipment recommended',
                'campaign_type': 'Seasonal'
            })
        
        # Check for high winds
        if current['wind_speed'] > 15 or any(day['wind_speed'] > 15 for day in forecast):
            recommendations.append({
                'condition': 'High Winds',
                'products': ['Safety Equipment', 'Weighted Barriers', 'Secure Storage'],
                'urgency': 'High',
                'message': 'High winds forecast - promote safety equipment',
                'campaign_type': 'Safety Alert'
            })
        
        return recommendations
    
    def _parse_weather_data(self, data):
        """Parse API weather data"""
        return {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'wind_speed': data['wind']['speed'],
            'rain_probability': data.get('rain', {}).get('1h', 0) * 10,  # Convert to percentage
            'timestamp': datetime.now()
        }
    
    def _parse_forecast_data(self, data):
        """Parse API forecast data"""
        forecast = []
        for item in data['list'][:24:8]:  # Take every 8th item (daily forecast)
            forecast.append({
                'date': datetime.fromtimestamp(item['dt']),
                'temperature': item['main']['temp'],
                'humidity': item['main']['humidity'],
                'description': item['weather'][0]['description'],
                'wind_speed': item['wind']['speed'],
                'rain_probability': item.get('rain', {}).get('3h', 0) * 3.33  # Convert to percentage
            })
        return forecast
    
    def _mock_weather_data(self):
        """Mock weather data for testing"""
        return {
            'temperature': 15.0,
            'humidity': 78,
            'description': 'light rain',
            'wind_speed': 8.5,
            'rain_probability': 85,
            'timestamp': datetime.now()
        }
    
    def _mock_forecast_data(self, days):
        """Mock forecast data for testing"""
        forecast = []
        for i in range(days):
            forecast.append({
                'date': datetime.now() + timedelta(days=i),
                'temperature': 15.0 + (i * 2),
                'humidity': 75 + (i * 3),
                'description': 'partly cloudy',
                'wind_speed': 10.0 + i,
                'rain_probability': 60 + (i * 5)
            })
        return forecast