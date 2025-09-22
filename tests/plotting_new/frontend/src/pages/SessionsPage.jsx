import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './SessionsPage.css';

const SessionsPage = () => {
  const [sessions, setSessions] = useState([]);
  const [viewMode, setViewMode] = useState('cards'); // 'cards' or 'table'
  const [user, setUser] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState(null);
  const [isCreating, setIsCreating] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Get user from localStorage
    const storedUser = localStorage.getItem('user');
    if (!storedUser) {
      navigate('/login');
      return;
    }
    setUser(JSON.parse(storedUser));

    // Load sessions
    loadSessions();
  }, [navigate]);

  const loadSessions = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/sessions');
      setSessions(response.data.sessions || []);
    } catch (error) {
      console.error('Error loading sessions:', error);
      // Start with empty sessions if there's an error
      setSessions([]);
    }
  };

  const handleCreateSession = async () => {
    setIsCreating(true);
    try {
      const response = await axios.post('http://localhost:8000/api/sessions', {
        name: `New Session ${sessions.length + 1}`,
        description: 'Click to edit description'
      });

      // Reload sessions
      await loadSessions();
    } catch (error) {
      console.error('Error creating session:', error);
      alert('Failed to create session. Please try again.');
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteSession = (session) => {
    setSessionToDelete(session);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (sessionToDelete) {
      try {
        await axios.delete(`http://localhost:8000/api/sessions/${sessionToDelete.id}`);
        // Reload sessions from server to ensure consistency
        await loadSessions();
      } catch (error) {
        console.error('Error deleting session:', error);
        alert('Failed to delete session. Please try again.');
      }
    }
    setShowDeleteConfirm(false);
    setSessionToDelete(null);
  };

  const handleOpenSession = (sessionId) => {
    // Navigate to visualization page with session context
    localStorage.setItem('currentSession', sessionId);
    navigate('/visualization');
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('currentSession');
    navigate('/login');
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="sessions-page">
      {/* Sidebar */}
      <div className="sessions-sidebar">
        <div className="sidebar-header">
          <h2>Data Studio</h2>
        </div>

        {user && (
          <div className="user-profile">
            <div className="user-avatar">
              {user.username ? user.username[0].toUpperCase() : 'U'}
            </div>
            <div className="user-info">
              <div className="user-name">{user.username || 'User'}</div>
              <div className="user-status">Active</div>
            </div>
          </div>
        )}

        <nav className="sidebar-nav">
          <a className="nav-item active">
            <span className="nav-icon">📊</span>
            <span className="nav-text">Sessions</span>
          </a>
          <a className="nav-item">
            <span className="nav-icon">⚙️</span>
            <span className="nav-text">Settings</span>
          </a>
          <a className="nav-item">
            <span className="nav-icon">📚</span>
            <span className="nav-text">Documentation</span>
          </a>
        </nav>

        <div className="sidebar-footer">
          <button className="logout-button" onClick={handleLogout}>
            <span className="logout-icon">🚪</span>
            <span>Logout</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="sessions-main">
        <div className="sessions-header">
          <h1>My Sessions</h1>
          <div className="header-actions">
            <div className="view-toggle">
              <button
                className={`toggle-btn ${viewMode === 'cards' ? 'active' : ''}`}
                onClick={() => setViewMode('cards')}
                title="Card View"
              >
                <span>⊞</span>
              </button>
              <button
                className={`toggle-btn ${viewMode === 'table' ? 'active' : ''}`}
                onClick={() => setViewMode('table')}
                title="Table View"
              >
                <span>☰</span>
              </button>
            </div>
            <button
              className="create-session-btn"
              onClick={handleCreateSession}
              disabled={isCreating}
            >
              <span>+</span> New Session
            </button>
          </div>
        </div>

        <div className="sessions-content">
          {sessions.length === 0 ? (
            <div className="empty-state">
              <h3>No sessions yet</h3>
              <p>Create your first session to get started</p>
              <button className="create-first-btn" onClick={handleCreateSession}>
                Create First Session
              </button>
            </div>
          ) : viewMode === 'cards' ? (
            <div className="sessions-grid">
              {sessions.map(session => (
                <div key={session.id} className="session-card">
                  <div className="card-header">
                    <h3>{session.name}</h3>
                    <button
                      className="delete-btn"
                      onClick={() => handleDeleteSession(session)}
                      title="Delete session"
                    >
                      🗑️
                    </button>
                  </div>
                  <p className="card-description">{session.description}</p>
                  <div className="card-meta">
                    <span className="meta-item">
                      Created: {formatDate(session.created_at)}
                    </span>
                    <span className="meta-item">
                      Modified: {formatDate(session.last_modified)}
                    </span>
                  </div>
                  <button
                    className="open-session-btn"
                    onClick={() => handleOpenSession(session.id)}
                  >
                    Open Session
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="sessions-table-container">
              <table className="sessions-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Created</th>
                    <th>Last Modified</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {sessions.map(session => (
                    <tr key={session.id}>
                      <td className="session-name">{session.name}</td>
                      <td className="session-description">{session.description}</td>
                      <td>{formatDate(session.created_at)}</td>
                      <td>{formatDate(session.last_modified)}</td>
                      <td className="session-actions">
                        <button
                          className="action-btn open"
                          onClick={() => handleOpenSession(session.id)}
                        >
                          Open
                        </button>
                        <button
                          className="action-btn delete"
                          onClick={() => handleDeleteSession(session)}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="modal-overlay" onClick={() => setShowDeleteConfirm(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Delete Session</h3>
            <p>Are you sure you want to delete "{sessionToDelete?.name}"?</p>
            <p className="warning-text">This action cannot be undone.</p>
            <div className="modal-actions">
              <button className="cancel-btn" onClick={() => setShowDeleteConfirm(false)}>
                Cancel
              </button>
              <button className="confirm-delete-btn" onClick={confirmDelete}>
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SessionsPage;