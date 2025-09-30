import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

class MemorySystem:
    def __init__(self, memory_folder="./memory"):
        self.memory_folder = memory_folder
        self.conversations_file = os.path.join(memory_folder, "conversations.json")
        self.campaigns_file = os.path.join(memory_folder, "campaigns.json")
        self.content_history_file = os.path.join(memory_folder, "content_history.json")
        self.insights_file = os.path.join(memory_folder, "insights.json")
        
        # Ensure memory folder exists
        os.makedirs(memory_folder, exist_ok=True)
        
        # Initialize files if they don't exist
        self._initialize_memory_files()
    
    def store_conversation(self, user_input: str, agent_response: str, context: Dict = None):
        """Store conversation in memory"""
        
        conversations = self._load_conversations()
        
        conversation_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'agent_response': agent_response,
            'context': context or {},
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        conversations.append(conversation_entry)
        
        # Keep only last 1000 conversations to manage memory
        if len(conversations) > 1000:
            conversations = conversations[-1000:]
        
        self._save_conversations(conversations)
        return conversation_entry['id']
    
    def store_campaign(self, campaign_data: Dict):
        """Store campaign information"""
        
        campaigns = self._load_campaigns()
        
        campaign_entry = {
            'id': str(uuid.uuid4()),
            'created_at': datetime.now().isoformat(),
            'campaign_data': campaign_data,
            'status': campaign_data.get('status', 'planned'),
            'type': campaign_data.get('type', 'general'),
            'products': campaign_data.get('products', []),
            'performance': {}
        }
        
        campaigns.append(campaign_entry)
        self._save_campaigns(campaigns)
        return campaign_entry['id']
    
    def store_generated_content(self, content_type: str, content: str, metadata: Dict = None):
        """Store generated content for future reference"""
        
        content_history = self._load_content_history()
        
        content_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'content_type': content_type,
            'content': content,
            'metadata': metadata or {},
            'used_count': 0,
            'last_used': None
        }
        
        content_history.append(content_entry)
        
        # Keep only last 500 content pieces
        if len(content_history) > 500:
            content_history = content_history[-500:]
        
        self._save_content_history(content_history)
        return content_entry['id']
    
    def store_insight(self, insight_type: str, insight_data: Dict):
        """Store marketing insights and learnings"""
        
        insights = self._load_insights()
        
        insight_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'type': insight_type,
            'data': insight_data,
            'source': insight_data.get('source', 'system'),
            'confidence': insight_data.get('confidence', 0.5)
        }
        
        insights.append(insight_entry)
        
        # Keep only last 200 insights
        if len(insights) > 200:
            insights = insights[-200:]
        
        self._save_insights(insights)
        return insight_entry['id']
    
    def get_recent_conversations(self, days: int = 7) -> List[Dict]:
        """Get recent conversations within specified days"""
        
        conversations = self._load_conversations()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent = []
        for conv in conversations:
            conv_date = datetime.fromisoformat(conv['timestamp'])
            if conv_date >= cutoff_date:
                recent.append(conv)
        
        return sorted(recent, key=lambda x: x['timestamp'], reverse=True)
    
    def get_campaign_history(self, campaign_type: str = None, limit: int = 20) -> List[Dict]:
        """Get campaign history, optionally filtered by type"""
        
        campaigns = self._load_campaigns()
        
        if campaign_type:
            filtered_campaigns = [c for c in campaigns if c.get('type') == campaign_type]
        else:
            filtered_campaigns = campaigns
        
        # Sort by creation date, most recent first
        sorted_campaigns = sorted(filtered_campaigns, key=lambda x: x['created_at'], reverse=True)
        
        return sorted_campaigns[:limit]
    
    def get_content_by_type(self, content_type: str, limit: int = 10) -> List[Dict]:
        """Get previously generated content by type"""
        
        content_history = self._load_content_history()
        
        filtered_content = [c for c in content_history if c['content_type'] == content_type]
        sorted_content = sorted(filtered_content, key=lambda x: x['timestamp'], reverse=True)
        
        return sorted_content[:limit]
    
    def get_insights_by_type(self, insight_type: str = None, days: int = 30) -> List[Dict]:
        """Get insights, optionally filtered by type and time period"""
        
        insights = self._load_insights()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_insights = []
        for insight in insights:
            insight_date = datetime.fromisoformat(insight['timestamp'])
            if insight_date >= cutoff_date:
                if not insight_type or insight['type'] == insight_type:
                    filtered_insights.append(insight)
        
        return sorted(filtered_insights, key=lambda x: x['timestamp'], reverse=True)
    
    def get_conversation_context(self, limit: int = 5) -> str:
        """Get recent conversation context for AI"""
        
        recent_conversations = self.get_recent_conversations(days=1)[:limit]
        
        if not recent_conversations:
            return "No recent conversation history."
        
        context = "Recent conversation history:\n"
        for conv in recent_conversations:
            timestamp = datetime.fromisoformat(conv['timestamp']).strftime('%H:%M')
            context += f"[{timestamp}] User: {conv['user_input'][:100]}...\n"
            context += f"[{timestamp}] Agent: {conv['agent_response'][:100]}...\n\n"
        
        return context
    
    def get_campaign_performance_summary(self) -> Dict:
        """Get summary of campaign performance"""
        
        campaigns = self._load_campaigns()
        
        summary = {
            'total_campaigns': len(campaigns),
            'campaigns_by_type': {},
            'campaigns_by_status': {},
            'recent_campaigns': 0
        }
        
        recent_date = datetime.now() - timedelta(days=30)
        
        for campaign in campaigns:
            # Count by type
            campaign_type = campaign.get('type', 'unknown')
            summary['campaigns_by_type'][campaign_type] = summary['campaigns_by_type'].get(campaign_type, 0) + 1
            
            # Count by status
            status = campaign.get('status', 'unknown')
            summary['campaigns_by_status'][status] = summary['campaigns_by_status'].get(status, 0) + 1
            
            # Count recent campaigns
            campaign_date = datetime.fromisoformat(campaign['created_at'])
            if campaign_date >= recent_date:
                summary['recent_campaigns'] += 1
        
        return summary
    
    def update_campaign_performance(self, campaign_id: str, performance_data: Dict):
        """Update campaign performance data"""
        
        campaigns = self._load_campaigns()
        
        for campaign in campaigns:
            if campaign['id'] == campaign_id:
                campaign['performance'].update(performance_data)
                campaign['last_updated'] = datetime.now().isoformat()
                break
        
        self._save_campaigns(campaigns)
    
    def mark_content_as_used(self, content_id: str):
        """Mark content as used and track usage"""
        
        content_history = self._load_content_history()
        
        for content in content_history:
            if content['id'] == content_id:
                content['used_count'] += 1
                content['last_used'] = datetime.now().isoformat()
                break
        
        self._save_content_history(content_history)
    
    def search_memory(self, query: str, memory_type: str = 'all') -> List[Dict]:
        """Search through memory for relevant information"""
        
        results = []
        query_lower = query.lower()
        
        if memory_type in ['all', 'conversations']:
            conversations = self._load_conversations()
            for conv in conversations:
                if (query_lower in conv['user_input'].lower() or 
                    query_lower in conv['agent_response'].lower()):
                    results.append({
                        'type': 'conversation',
                        'relevance': 'high',
                        'data': conv
                    })
        
        if memory_type in ['all', 'campaigns']:
            campaigns = self._load_campaigns()
            for campaign in campaigns:
                campaign_data = json.dumps(campaign).lower()
                if query_lower in campaign_data:
                    results.append({
                        'type': 'campaign',
                        'relevance': 'medium',
                        'data': campaign
                    })
        
        if memory_type in ['all', 'content']:
            content_history = self._load_content_history()
            for content in content_history:
                if (query_lower in content['content'].lower() or 
                    query_lower in content['content_type'].lower()):
                    results.append({
                        'type': 'content',
                        'relevance': 'medium',
                        'data': content
                    })
        
        # Sort by relevance and recency
        results.sort(key=lambda x: (x['relevance'], x['data'].get('timestamp', '')), reverse=True)
        
        return results[:20]  # Return top 20 results
    
    def _initialize_memory_files(self):
        """Initialize memory files if they don't exist"""
        
        files_to_init = [
            self.conversations_file,
            self.campaigns_file,
            self.content_history_file,
            self.insights_file
        ]
        
        for file_path in files_to_init:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f)
    
    def _load_conversations(self) -> List[Dict]:
        """Load conversations from file"""
        try:
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_conversations(self, conversations: List[Dict]):
        """Save conversations to file"""
        with open(self.conversations_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, indent=2, ensure_ascii=False)
    
    def _load_campaigns(self) -> List[Dict]:
        """Load campaigns from file"""
        try:
            with open(self.campaigns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_campaigns(self, campaigns: List[Dict]):
        """Save campaigns to file"""
        with open(self.campaigns_file, 'w', encoding='utf-8') as f:
            json.dump(campaigns, f, indent=2, ensure_ascii=False)
    
    def _load_content_history(self) -> List[Dict]:
        """Load content history from file"""
        try:
            with open(self.content_history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_content_history(self, content_history: List[Dict]):
        """Save content history to file"""
        with open(self.content_history_file, 'w', encoding='utf-8') as f:
            json.dump(content_history, f, indent=2, ensure_ascii=False)
    
    def _load_insights(self) -> List[Dict]:
        """Load insights from file"""
        try:
            with open(self.insights_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_insights(self, insights: List[Dict]):
        """Save insights to file"""
        with open(self.insights_file, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)