"""
Gemini AI Service for generating visualization configurations
"""
import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, api_key: str):
        """
        Initialize the Gemini service with API key
        
        Args:
            api_key: Google Gemini API key
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Gemini service initialized successfully")
    
    def generate_plot_config(self, user_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Generate a plot configuration based on user prompt
        
        Args:
            user_prompt: Natural language description of desired visualization
            
        Returns:
            Dict containing plot configuration or None if generation fails
        """
        system_prompt = """You are a visualization assistant that generates JSON configurations for a plotting application.
        Based on the user's request, generate a valid JSON configuration that follows this structure:
        
        {
            "app_title": "string",
            "theme": "light" or "dark",
            "figures": [
                {
                    "id": "unique_id",
                    "x_label": "string",
                    "y_label": "string",
                    "items": [
                        {
                            "type": "line" or "scatter" or "bar",
                            "legend_name": "string",
                            "source": "path/to/data.csv"
                        }
                    ]
                }
            ]
        }
        
        Return ONLY valid JSON, no additional text or explanation.
        """
        
        try:
            full_prompt = f"{system_prompt}\n\nUser request: {user_prompt}"
            response = self.model.generate_content(full_prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            config = json.loads(response_text.strip())
            logger.info("Successfully generated plot configuration")
            return config
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating plot config: {e}")
            return None
    
    def improve_config(self, current_config: Dict[str, Any], improvement_request: str) -> Optional[Dict[str, Any]]:
        """
        Improve an existing configuration based on user feedback
        
        Args:
            current_config: Current plot configuration
            improvement_request: User's request for changes
            
        Returns:
            Updated configuration or None if generation fails
        """
        prompt = f"""Given this current plot configuration:
        {json.dumps(current_config, indent=2)}
        
        User request: {improvement_request}
        
        Generate an improved JSON configuration that incorporates the requested changes.
        Return ONLY valid JSON, no additional text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            config = json.loads(response_text.strip())
            logger.info("Successfully improved plot configuration")
            return config
            
        except Exception as e:
            logger.error(f"Error improving config: {e}")
            return None