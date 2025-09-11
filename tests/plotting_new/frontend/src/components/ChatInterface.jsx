import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { ChatAssistantIcon, UserIcon } from './icons';

const ChatInterface = ({ expanded, currentConfig, onConfigUpdate }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI visualization assistant powered by Gemini. I can help you:\n• Create new plot configurations from your descriptions\n• Modify existing plots\n• Explain data patterns\n• Suggest improvements\n\nTry asking me to 'create a line chart' or 'change the theme to dark'!",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userText = inputText.trim();
    const userMessage = {
      id: Date.now(),
      text: userText,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);
    
    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
    }

    try {
      // Use the unified chat endpoint
      const response = await axios.post('http://localhost:8000/api/chat', {
        message: userText,
        current_config: currentConfig
      });

      const responseData = response.data;

      // Handle different response types
      if (responseData.type === 'config_new' || responseData.type === 'config_update' || responseData.type === 'config_with_analysis') {
        // Update the visualization with new/updated config
        if (onConfigUpdate && responseData.config) {
          onConfigUpdate(responseData.config);
        }
      } else if (responseData.type === 'data_analysis') {
        // Just show the analysis message, no config update
        // Could enhance this to show data preview in the future
      } else if (responseData.type === 'transformation_complete') {
        // Show transformation summary
        // Could enhance this to show before/after comparison
      } else if (responseData.type === 'need_data') {
        // Prompt user to upload data
        // Could enhance this with a file upload button
      }

      // Display the message from the AI
      const botMessage = {
        id: Date.now() + 1,
        text: responseData.message || 'I processed your request.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Error calling chat API:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        text: `I encountered an issue processing your request. Please try again or check that the backend server is running.`,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleInputChange = (e) => {
    setInputText(e.target.value);
    
    // Auto-resize textarea
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 100)}px`;
    }
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (!expanded) {
    return (
      <div className="chat-collapsed">
        <ChatAssistantIcon size={16} />
      </div>
    );
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <ChatAssistantIcon size={30} />
        <span>AI Assistant</span>
      </div>
      
      <div className="chat-messages">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div className="message-avatar">
              {message.sender === 'bot' ? <ChatAssistantIcon size={20} /> : <UserIcon size={20} />}
            </div>
            <div className="message-content">
              <div className="message-text">{message.text}</div>
              <div className="message-time">{formatTime(message.timestamp)}</div>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="message bot typing">
            <div className="message-avatar">
              <ChatAssistantIcon size={16} />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <textarea
            ref={inputRef}
            value={inputText}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your data visualization..."
            className="chat-input"
            rows="1"
            disabled={isTyping}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatInterface; 