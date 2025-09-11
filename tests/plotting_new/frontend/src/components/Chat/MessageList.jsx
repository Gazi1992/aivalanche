import React from 'react';
import './MessageList.css';

const MessageList = ({ messages, onActionClick }) => {
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  const renderMessageContent = (message) => {
    // Handle different message types
    if (message.isFile) {
      return (
        <div className="message-file">
          <span className="file-icon">📄</span>
          <span>{message.content}</span>
        </div>
      );
    }
    
    if (message.dataPreview) {
      return (
        <>
          <div className="message-text">{message.content}</div>
          <div className="message-data-preview">
            <div className="preview-badge">📊 Data loaded</div>
            <div className="preview-info">
              {message.dataPreview.shape && (
                <span>{message.dataPreview.shape.rows} rows × {message.dataPreview.shape.columns} columns</span>
              )}
            </div>
          </div>
        </>
      );
    }
    
    // Parse message content for special formatting
    const lines = message.content.split('\n');
    return (
      <div className="message-text">
        {lines.map((line, index) => {
          // Check for bullet points
          if (line.startsWith('•') || line.startsWith('-')) {
            return (
              <div key={index} className="message-bullet">{line}</div>
            );
          }
          // Check for code blocks (simple detection)
          if (line.startsWith('```')) {
            return null; // Skip code fence markers
          }
          return (
            <div key={index}>{line || <br />}</div>
          );
        })}
      </div>
    );
  };
  
  const renderSuggestions = (suggestions) => {
    if (!suggestions || suggestions.length === 0) return null;
    
    return (
      <div className="message-suggestions">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            className="suggestion-chip"
            onClick={() => onActionClick(suggestion.action)}
          >
            {suggestion.text}
          </button>
        ))}
      </div>
    );
  };
  
  return (
    <div className="message-list">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`message ${message.type} ${message.isError ? 'error' : ''}`}
        >
          <div className="message-avatar">
            {message.type === 'bot' ? (
              <span className="bot-avatar">🤖</span>
            ) : (
              <span className="user-avatar">👤</span>
            )}
          </div>
          
          <div className="message-content">
            {renderMessageContent(message)}
            
            {message.responseType && (
              <div className="message-type-badge">
                {message.responseType.replace(/_/g, ' ')}
              </div>
            )}
            
            {renderSuggestions(message.suggestions)}
            
            <div className="message-time">
              {formatTime(message.timestamp)}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MessageList;