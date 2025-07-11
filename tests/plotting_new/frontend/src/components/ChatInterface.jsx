import React, { useState, useRef, useEffect } from 'react';

// SendIcon removed - using Enter key to send messages

const BotIcon = ({ size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="10" rx="2" ry="2"></rect>
    <circle cx="12" cy="5" r="2"></circle>
    <path d="m12 7-3 4h6l-3-4z"></path>
    <line x1="8" y1="16" x2="8" y2="16"></line>
    <line x1="16" y1="16" x2="16" y2="16"></line>
  </svg>
);

const UserIcon = ({ size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
  </svg>
);

const ChatInterface = ({ expanded }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your data visualization assistant. I can help you understand your plots, suggest improvements, or answer questions about your data. How can I help you today?",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Mock responses for testing
  const mockResponses = [
    "That's an interesting question! Based on your data visualization, I can see several patterns that might be worth exploring further.",
    "Great observation! The trends in your plots suggest there might be seasonal variations in your data. Have you considered adding time-based filtering?",
    "I notice your scatter plot shows some clustering. This could indicate distinct groups in your data that might benefit from separate analysis.",
    "Your bar chart shows clear leaders in the data. Would you like me to help you highlight the top performers or add annotations?",
    "That's a thoughtful question about data interpretation. The correlation you're seeing might be influenced by external factors not shown in the current visualization.",
    "I can help you improve the readability of your plots. Consider adjusting the color palette or adding grid lines for better visual clarity.",
    "Your histogram reveals an interesting distribution. The skewness suggests you might want to consider logarithmic scaling or data transformation.",
    "Based on the patterns I see, you might want to add error bars or confidence intervals to better represent data uncertainty.",
    "That's a great point about data storytelling. Adding annotations or callout boxes could help highlight key insights for your audience.",
    "I see potential for interactive features in your visualization. Hover tooltips or clickable legends could enhance user engagement."
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputText.trim(),
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

    // Simulate typing delay
    setTimeout(() => {
      const randomResponse = mockResponses[Math.floor(Math.random() * mockResponses.length)];
      const botMessage = {
        id: Date.now() + 1,
        text: randomResponse,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);
    }, 1000 + Math.random() * 2000); // Random delay between 1-3 seconds
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
        <BotIcon size={16} />
      </div>
    );
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <BotIcon size={18} />
        <span>AI Assistant</span>
      </div>
      
      <div className="chat-messages">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div className="message-avatar">
              {message.sender === 'bot' ? <BotIcon size={16} /> : <UserIcon size={16} />}
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
              <BotIcon size={16} />
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