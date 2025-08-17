"""
Gemini AI Service for chat and visualization configuration generation
"""
import json
import logging
from typing import Dict, Any, Optional, List
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
        # Store conversation history for context
        self.conversation_history = []
        logger.info("Gemini service initialized successfully")
    
    def chat_response(self, user_message: str, current_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a chat message and determine appropriate response
        
        Args:
            user_message: User's chat message
            current_config: Current visualization configuration if available
            
        Returns:
            Dict with response type and content
        """
        # First, determine if this is a visualization request
        classification_prompt = f"""
        Analyze this user message and determine if it's related to data visualization/plotting.
        
        User message: "{user_message}"
        
        Respond with ONLY one of these words:
        - "VISUALIZATION" if the user wants to create, modify, or asks about plots/charts/visualizations
        - "GENERAL" if it's a greeting, general question, or unrelated to visualization
        
        Examples:
        "Create a line chart" -> VISUALIZATION
        "Change theme to dark" -> VISUALIZATION  
        "Hi" -> GENERAL
        "How are you?" -> GENERAL
        "What can you do?" -> GENERAL
        """
        
        try:
            classification_response = self.model.generate_content(classification_prompt)
            message_type = classification_response.text.strip().upper()
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            
            if "VISUALIZATION" in message_type:
                # Determine if it's a modification or new creation
                is_modification = current_config and any(word in user_message.lower() for word in [
                    'change', 'modify', 'update', 'adjust', 'improve', 'add', 'remove', 'delete'
                ])
                
                if is_modification:
                    config = self.improve_config(current_config, user_message)
                    if config:
                        response_text = "I've updated the visualization based on your request. The changes should be visible now."
                        self.conversation_history.append({"role": "assistant", "content": response_text})
                        return {
                            "type": "config_update",
                            "config": config,
                            "message": response_text
                        }
                else:
                    config = self.generate_plot_config(user_message)
                    if config:
                        response_text = "I've created a new visualization based on your request."
                        self.conversation_history.append({"role": "assistant", "content": response_text})
                        return {
                            "type": "config_new",
                            "config": config,
                            "message": response_text
                        }
                
                # If config generation failed
                error_msg = "I understood you want to work with visualizations, but I had trouble generating the configuration. Could you please be more specific?"
                self.conversation_history.append({"role": "assistant", "content": error_msg})
                return {
                    "type": "error",
                    "message": error_msg
                }
            else:
                # Handle general conversation with context
                return self.general_chat(user_message)
                
        except Exception as e:
            logger.error(f"Error in chat_response: {e}")
            error_msg = f"I encountered an error processing your message: {str(e)}"
            return {
                "type": "error",
                "message": error_msg
            }
    
    def general_chat(self, user_message: str) -> Dict[str, Any]:
        """
        Handle general conversation that's not about visualization
        
        Args:
            user_message: User's message
            
        Returns:
            Dict with chat response
        """
        # Build context from conversation history
        context = "Previous conversation:\n"
        for msg in self.conversation_history[-5:]:  # Last 5 messages for context
            context += f"{msg['role']}: {msg['content']}\n"
        
        prompt = f"""
        You are a helpful AI assistant for a data visualization application. 
        You can help users create and modify charts, but also engage in general conversation.
        
        {context if len(self.conversation_history) > 1 else ""}
        
        User: {user_message}
        
        Respond naturally and helpfully. If they're greeting you, greet them back and mention you can help with visualizations.
        Keep responses concise and friendly.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return {
                "type": "chat",
                "message": response_text
            }
        except Exception as e:
            logger.error(f"Error in general_chat: {e}")
            return {
                "type": "error",
                "message": "I'm having trouble responding right now. Please try again."
            }
    
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
            "app_title": "string (title for the app window)",
            "theme": "light" or "dark",
            "left_margin": number (default: 10),
            "right_margin": number (default: 10),
            "top_margin": number (default: 10),
            "bottom_margin": number (default: 10),
            "grid_layout": {
                "rows": number (default: 1),
                "cols": number (default: 1),
                "horizontal_spacing": number (default: 20),
                "vertical_spacing": number (default: 20)
            },
            "figures": [
                {
                    "id": "unique_id (e.g., figure1)",
                    "visibility": boolean (default: true),
                    "x_label": "string",
                    "y_label": "string",
                    "x_scale": "linear" or "log",
                    "y_scale": "linear" or "log",
                    "grid_x": boolean,
                    "grid_y": boolean,
                    "items": [
                        {
                            "id": "unique_id (e.g., plot1)",
                            "type": "line" or "scatter" or "bar" or "histogram",
                            "source": "data/filename.csv",
                            "x_column": "column_name",
                            "y_column": "column_name",
                            "legend_name": "string",
                            "legend_visible": boolean,
                            "line_color": "#hexcolor",
                            "line_width": number,
                            "symbol_size": number (0 for no symbols)
                        }
                    ]
                }
            ]
        }
        
        Common data files available:
        - data/temperature_data.csv (columns: time, sensor1, sensor2)
        - data/sales_data.csv (columns: month, revenue, profit)
        - data/population.csv (columns: year, population)
        
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
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")