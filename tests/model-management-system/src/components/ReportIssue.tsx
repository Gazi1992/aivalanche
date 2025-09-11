import React, { useState } from 'react';
import { X, AlertTriangle, Send } from 'lucide-react';

interface ReportIssueProps {
  isOpen: boolean;
  onClose: () => void;
  itemType: 'model' | 'reference-data' | 'testbench';
  itemName: string;
  itemId: string;
  onSubmit?: (issueData: IssueData) => void;
}

export interface IssueData {
  itemType: string;
  itemId: string;
  itemName: string;
  issueType: string;
  severity: string;
  description: string;
  reproductionSteps?: string;
  expectedBehavior?: string;
  actualBehavior?: string;
  userEmail?: string;
  timestamp: string;
}

const ReportIssue: React.FC<ReportIssueProps> = ({
  isOpen,
  onClose,
  itemType,
  itemName,
  itemId,
  onSubmit
}) => {
  const [issueType, setIssueType] = useState('bug');
  const [severity, setSeverity] = useState('medium');
  const [description, setDescription] = useState('');
  const [reproductionSteps, setReproductionSteps] = useState('');
  const [expectedBehavior, setExpectedBehavior] = useState('');
  const [actualBehavior, setActualBehavior] = useState('');
  const [userEmail, setUserEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const getItemTypeLabel = () => {
    switch (itemType) {
      case 'model':
        return 'Model Template';
      case 'reference-data':
        return 'Reference Data';
      case 'testbench':
        return 'Testbench';
      default:
        return 'Item';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    const issueData: IssueData = {
      itemType,
      itemId,
      itemName,
      issueType,
      severity,
      description,
      reproductionSteps,
      expectedBehavior,
      actualBehavior,
      userEmail,
      timestamp: new Date().toISOString()
    };

    // Simulate API call
    setTimeout(() => {
      if (onSubmit) {
        onSubmit(issueData);
      }
      console.log('Issue reported:', issueData);
      
      // Reset form
      setIssueType('bug');
      setSeverity('medium');
      setDescription('');
      setReproductionSteps('');
      setExpectedBehavior('');
      setActualBehavior('');
      setUserEmail('');
      setIsSubmitting(false);
      
      // Show success message (you might want to use a toast notification here)
      alert('Issue reported successfully! Our team will review it shortly.');
      
      onClose();
    }, 1000);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center px-6 py-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-orange-500" />
            <div>
              <h2 className="text-xl font-bold text-gray-900">Report an Issue</h2>
              <p className="text-sm text-gray-600">
                {getItemTypeLabel()}: {itemName}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Issue Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Issue Type
              </label>
              <select
                value={issueType}
                onChange={(e) => setIssueType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              >
                <option value="bug">Bug/Error</option>
                <option value="incorrect-data">Incorrect Data</option>
                <option value="missing-data">Missing Data</option>
                <option value="performance">Performance Issue</option>
                <option value="documentation">Documentation Issue</option>
                <option value="enhancement">Enhancement Request</option>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Severity */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Severity
              </label>
              <div className="flex gap-3">
                {['low', 'medium', 'high', 'critical'].map((level) => (
                  <button
                    key={level}
                    type="button"
                    onClick={() => setSeverity(level)}
                    className={`px-4 py-2 rounded-lg capitalize ${
                      severity === level
                        ? level === 'critical'
                          ? 'bg-red-600 text-white'
                          : level === 'high'
                          ? 'bg-orange-600 text-white'
                          : level === 'medium'
                          ? 'bg-yellow-600 text-white'
                          : 'bg-green-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description <span className="text-red-500">*</span>
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                rows={4}
                placeholder="Describe the issue you're experiencing..."
                required
              />
            </div>

            {/* Reproduction Steps (for bugs) */}
            {issueType === 'bug' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Steps to Reproduce
                </label>
                <textarea
                  value={reproductionSteps}
                  onChange={(e) => setReproductionSteps(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  placeholder="1. Open the model&#10;2. Click on...&#10;3. ..."
                />
              </div>
            )}

            {/* Expected vs Actual Behavior (for bugs and incorrect data) */}
            {(issueType === 'bug' || issueType === 'incorrect-data') && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Expected Behavior
                  </label>
                  <textarea
                    value={expectedBehavior}
                    onChange={(e) => setExpectedBehavior(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    rows={2}
                    placeholder="What should happen?"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Actual Behavior
                  </label>
                  <textarea
                    value={actualBehavior}
                    onChange={(e) => setActualBehavior(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    rows={2}
                    placeholder="What actually happens?"
                  />
                </div>
              </>
            )}

            {/* Contact Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Email (optional)
              </label>
              <input
                type="email"
                value={userEmail}
                onChange={(e) => setUserEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="email@example.com"
              />
              <p className="text-xs text-gray-500 mt-1">
                Provide your email if you'd like to receive updates about this issue
              </p>
            </div>
          </form>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
          <p className="text-xs text-gray-500">
            All issues are tracked and reviewed by our engineering team
          </p>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={!description || isSubmitting}
              className="px-4 py-2 bg-orange-600 text-white hover:bg-orange-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Submit Issue
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportIssue;