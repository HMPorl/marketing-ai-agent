import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class StyleGuideManager:
    """
    Manages The Hireman's content style guide and learning from user feedback
    """
    
    def __init__(self, style_guide_path: str = None):
        self.style_guide_path = style_guide_path or "data/style_guide.json"
        self.style_guide = self.load_style_guide()
        
    def load_style_guide(self) -> Dict:
        """Load the style guide from JSON file"""
        try:
            if os.path.exists(self.style_guide_path):
                with open(self.style_guide_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._create_default_style_guide()
        except Exception as e:
            print(f"Error loading style guide: {e}")
            return self._create_default_style_guide()
    
    def save_style_guide(self):
        """Save the current style guide to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.style_guide_path), exist_ok=True)
            
            # Update timestamp
            self.style_guide["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.style_guide_path, 'w', encoding='utf-8') as f:
                json.dump(self.style_guide, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving style guide: {e}")
    
    def add_feedback(self, content_type: str, feedback: str, example: Dict = None):
        """
        Add user feedback to the style guide
        
        Args:
            content_type: 'title', 'description', 'features', etc.
            feedback: User's feedback text
            example: Optional example of good/bad content
        """
        feedback_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content_type": content_type,
            "feedback": feedback,
            "example": example
        }
        
        self.style_guide["feedback_log"].append(feedback_entry)
        self.save_style_guide()
        
        # Process feedback to update guidelines
        self._process_feedback(feedback_entry)
    
    def add_approved_example(self, content_type: str, content: str, product_code: str = None):
        """Add an approved example to the style guide"""
        example = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content_type": content_type,
            "content": content,
            "product_code": product_code
        }
        
        self.style_guide["approved_examples"].append(example)
        self.save_style_guide()
    
    def add_rejected_example(self, content_type: str, content: str, reason: str, product_code: str = None):
        """Add a rejected example with reason"""
        example = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content_type": content_type,
            "content": content,
            "reason": reason,
            "product_code": product_code
        }
        
        self.style_guide["rejected_examples"].append(example)
        self.save_style_guide()
    
    def get_title_guidelines(self) -> Dict:
        """Get title formatting guidelines"""
        return self.style_guide.get("title_guidelines", {})
    
    def get_description_guidelines(self) -> Dict:
        """Get description formatting guidelines"""
        return self.style_guide.get("description_guidelines", {})
    
    def get_tone_guidelines(self) -> Dict:
        """Get tone and language guidelines"""
        return self.style_guide.get("description_guidelines", {}).get("tone", {})
    
    def get_category_intro(self, category: str) -> str:
        """Get the standard intro text for a product category"""
        patterns = self.style_guide.get("content_patterns", {}).get("category_intros", {})
        return patterns.get(category, "for professional applications")
    
    def should_avoid_word(self, word: str) -> bool:
        """Check if a word should be avoided based on tone guidelines"""
        avoid_words = self.get_tone_guidelines().get("avoid", [])
        return word.lower() in [w.lower() for w in avoid_words]
    
    def get_preferred_words(self) -> List[str]:
        """Get list of preferred words/phrases"""
        return self.get_tone_guidelines().get("prefer", [])
    
    def _process_feedback(self, feedback_entry: Dict):
        """
        Process feedback to automatically update guidelines where possible
        """
        feedback = feedback_entry["feedback"].lower()
        content_type = feedback_entry["content_type"]
        
        # Look for patterns in feedback to update guidelines
        if "avoid" in feedback or "don't use" in feedback:
            # Extract words/phrases to avoid
            if content_type == "title":
                # Add to title avoid list
                pass
            elif content_type in ["description", "features"]:
                # Add to tone avoid list
                pass
        
        elif "prefer" in feedback or "use instead" in feedback:
            # Extract preferred alternatives
            pass
        
        # This could be enhanced with NLP to automatically extract
        # specific guidance from natural language feedback
    
    def _create_default_style_guide(self) -> Dict:
        """Create a default style guide structure"""
        return {
            "version": "1.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "company_info": {
                "name": "The Hireman",
                "website": "thehireman.co.uk",
                "location": "London",
                "tone": "professional, factual, no marketing fluff"
            },
            "title_guidelines": {
                "format": "Clean product name only",
                "avoid": [],
                "include": ["Brand name", "Model number", "Product type"]
            },
            "description_guidelines": {
                "structure": {
                    "intro": {
                        "length": "1-2 sentences",
                        "content": "Brief factual description"
                    },
                    "key_features": {
                        "format": "HTML unordered list"
                    }
                },
                "tone": {
                    "avoid": [],
                    "prefer": []
                }
            },
            "content_patterns": {},
            "feedback_log": [],
            "approved_examples": [],
            "rejected_examples": []
        }
    
    def get_recent_feedback(self, limit: int = 10) -> List[Dict]:
        """Get recent feedback entries"""
        feedback_log = self.style_guide.get("feedback_log", [])
        return feedback_log[-limit:] if len(feedback_log) > limit else feedback_log
    
    def get_approved_examples(self, content_type: str = None) -> List[Dict]:
        """Get approved examples, optionally filtered by content type"""
        examples = self.style_guide.get("approved_examples", [])
        if content_type:
            return [ex for ex in examples if ex.get("content_type") == content_type]
        return examples
    
    def export_style_guide(self) -> str:
        """Export the current style guide as formatted text"""
        guide = self.style_guide
        
        export_text = f"""
# The Hireman Content Style Guide
Version: {guide.get('version', '1.0')}
Last Updated: {guide.get('last_updated', 'Unknown')}

## Company Information
- Name: {guide.get('company_info', {}).get('name', 'The Hireman')}
- Website: {guide.get('company_info', {}).get('website', 'thehireman.co.uk')}
- Tone: {guide.get('company_info', {}).get('tone', 'Professional, factual')}

## Title Guidelines
Format: {guide.get('title_guidelines', {}).get('format', 'Product name only')}

### Avoid in Titles:
{chr(10).join('- ' + item for item in guide.get('title_guidelines', {}).get('avoid', []))}

## Description Guidelines
Structure: {guide.get('description_guidelines', {}).get('structure', {}).get('intro', {}).get('content', 'Brief intro + key features')}

### Words to Avoid:
{chr(10).join('- ' + item for item in guide.get('description_guidelines', {}).get('tone', {}).get('avoid', []))}

### Preferred Words:
{chr(10).join('- ' + item for item in guide.get('description_guidelines', {}).get('tone', {}).get('prefer', []))}

## Recent Feedback ({len(guide.get('feedback_log', []))})
{chr(10).join(f"- {fb.get('timestamp', '')}: {fb.get('feedback', '')}" for fb in guide.get('feedback_log', [])[-5:])}

## Approved Examples ({len(guide.get('approved_examples', []))})
{chr(10).join(f"- {ex.get('content_type', '')}: {ex.get('content', '')[:100]}..." for ex in guide.get('approved_examples', [])[-5:])}
        """
        
        return export_text.strip()