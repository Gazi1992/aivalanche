import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  Upload, FileJson, AlertCircle, CheckCircle, X, Loader2, AlertTriangle,
  ChevronRight, Activity, FileText, User, Shield, Zap
} from 'lucide-react';
import { Modal, Button } from '../ui';

interface TestbenchUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (data: any) => void;
}

interface ValidationError {
  section: string;
  issue: string;
}

interface ValidationResult {
  isValid: boolean;
  errors?: ValidationError[];
  warnings?: string[];
}

const TestbenchUploadModal: React.FC<TestbenchUploadModalProps> = ({
  isOpen,
  onClose,
  onUpload,
}) => {
  const [activeSection, setActiveSection] = useState<string>('file');
  const [schematicFile, setSchematicFile] = useState<File | null>(null);
  const [configFile, setConfigFile] = useState<File | null>(null);
  const [fileContent, setFileContent] = useState<any>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [validationProgress, setValidationProgress] = useState(0);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [hasValidated, setHasValidated] = useState(false);
  
  // Refs for sections
  const fileRef = useRef<HTMLDivElement>(null);
  const testbenchRef = useRef<HTMLDivElement>(null);
  const simulationRef = useRef<HTMLDivElement>(null);
  const documentationRef = useRef<HTMLDivElement>(null);
  const authorRef = useRef<HTMLDivElement>(null);
  const validationRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  
  // Metadata fields
  const [metadata, setMetadata] = useState({
    // File & Basic Info
    name: '',
    version: '1.0',
    category: 'DC',
    description: '',
    tags: '',
    
    // Testbench Configuration
    testbench_type: 'dc_sweep',
    analysis_type: 'DC',
    device_types: '',
    supported_models: '',
    complexity: 'Basic',
    
    // Simulation Settings
    simulation_time: '',
    step_size: '',
    convergence_criteria: '',
    temperature_range: '25',
    voltage_range: '',
    current_range: '',
    
    // Documentation
    documentation_url: '',
    examples_included: false,
    notes: '',
    
    // Author Info
    author_name: '',
    author_email: '',
    author_organization: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Section configuration
  const sections = useMemo(() => [
    { id: 'file', label: 'File & Basic Info', icon: FileJson, ref: fileRef },
    { id: 'testbench', label: 'Testbench Configuration', icon: Activity, ref: testbenchRef },
    { id: 'simulation', label: 'Simulation Settings', icon: Zap, ref: simulationRef },
    { id: 'documentation', label: 'Documentation', icon: FileText, ref: documentationRef },
    { id: 'author', label: 'Author Information', icon: User, ref: authorRef },
    { id: 'validation', label: 'Validation', icon: Shield, ref: validationRef },
  ], []);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setSchematicFile(null);
      setConfigFile(null);
      setFileContent(null);
      setValidationResult(null);
      setValidationProgress(0);
      setHasValidated(false);
      setActiveSection('file');
      setMetadata({
        name: '',
        version: '1.0',
        category: 'DC',
        description: '',
        tags: '',
        testbench_type: 'dc_sweep',
        analysis_type: 'DC',
        device_types: '',
        supported_models: '',
        complexity: 'Basic',
        simulation_time: '',
        step_size: '',
        convergence_criteria: '',
        temperature_range: '25',
        voltage_range: '',
        current_range: '',
        documentation_url: '',
        examples_included: false,
        notes: '',
        author_name: '',
        author_email: '',
        author_organization: '',
      });
      setErrors({});
    }
  }, [isOpen]);

  // Update active section based on scroll position
  useEffect(() => {
    const handleScroll = () => {
      if (!scrollContainerRef.current) return;
      
      const containerTop = scrollContainerRef.current.getBoundingClientRect().top;
      
      // Check which section is most visible
      for (let i = sections.length - 1; i >= 0; i--) {
        const section = sections[i];
        if (section.ref.current) {
          const rect = section.ref.current.getBoundingClientRect();
          if (rect.top - containerTop <= 20) {
            setActiveSection(section.id);
            break;
          }
        }
      }
    };

    const container = scrollContainerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, [isOpen, sections]);

  const scrollToSection = (sectionId: string) => {
    const section = sections.find(s => s.id === sectionId);
    if (section?.ref.current && scrollContainerRef.current) {
      const container = scrollContainerRef.current;
      const element = section.ref.current;
      
      // Calculate the actual position of the element relative to the container
      const containerRect = container.getBoundingClientRect();
      const elementRect = element.getBoundingClientRect();
      
      // Current scroll position + difference in positions
      const scrollTop = container.scrollTop + (elementRect.top - containerRect.top);
      
      container.scrollTo({
        top: Math.max(0, scrollTop),
        behavior: 'smooth'
      });
    }
  };

  const handleSchematicUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;

    const validExtensions = ['.svg', '.png', '.jpg', '.jpeg', '.gif', '.webp'];
    const fileExt = uploadedFile.name.toLowerCase();
    const isValidFile = validExtensions.some(ext => fileExt.endsWith(ext));
    
    if (!isValidFile) {
      setErrors({ schematic: 'Please upload a valid image file (SVG, PNG, JPG, JPEG, GIF, or WEBP)' });
      return;
    }

    setSchematicFile(uploadedFile);
    setErrors(prev => ({ ...prev, schematic: '' }));
    setHasValidated(false);
    setValidationResult(null);
  };

  const handleConfigUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;

    if (!uploadedFile.name.endsWith('.json')) {
      setErrors({ config: 'Please upload a JSON configuration file' });
      return;
    }

    setConfigFile(uploadedFile);
    setErrors(prev => ({ ...prev, config: '' }));
    setHasValidated(false);
    setValidationResult(null);

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const json = JSON.parse(event.target?.result as string);
        setFileContent(json);
        
        // Auto-fill metadata if present in the file
        if (json.name) setMetadata(prev => ({ ...prev, name: json.name }));
        if (json.version) setMetadata(prev => ({ ...prev, version: json.version }));
        if (json.category) setMetadata(prev => ({ ...prev, category: json.category }));
        if (json.description) setMetadata(prev => ({ ...prev, description: json.description }));
        if (json.testbench_type) setMetadata(prev => ({ ...prev, testbench_type: json.testbench_type }));
        if (json.analysis_type) setMetadata(prev => ({ ...prev, analysis_type: json.analysis_type }));
        if (json.device_types) setMetadata(prev => ({ ...prev, device_types: json.device_types.join(', ') }));
        if (json.supported_models) setMetadata(prev => ({ ...prev, supported_models: json.supported_models.join(', ') }));
        if (json.complexity) setMetadata(prev => ({ ...prev, complexity: json.complexity }));
        if (json.simulation_settings) {
          if (json.simulation_settings.temperature_range) {
            setMetadata(prev => ({ ...prev, temperature_range: json.simulation_settings.temperature_range }));
          }
          if (json.simulation_settings.voltage_range) {
            setMetadata(prev => ({ ...prev, voltage_range: json.simulation_settings.voltage_range }));
          }
        }
        if (json.author) {
          if (json.author.name) setMetadata(prev => ({ ...prev, author_name: json.author.name }));
          if (json.author.email) setMetadata(prev => ({ ...prev, author_email: json.author.email }));
          if (json.author.organization) setMetadata(prev => ({ ...prev, author_organization: json.author.organization }));
        }
        if (json.tags && Array.isArray(json.tags)) {
          setMetadata(prev => ({ ...prev, tags: json.tags.join(', ') }));
        }
      } catch (error) {
        setErrors({ config: 'Invalid JSON file format' });
        setFileContent(null);
      }
    };
    reader.readAsText(uploadedFile);
  };

  const validateData = async () => {
    setIsValidating(true);
    setValidationProgress(0);
    // Don't clear validation result to keep previous results visible

    // Simulate validation with progress
    const totalSteps = 5;
    for (let i = 0; i <= totalSteps; i++) {
      setValidationProgress((i / totalSteps) * 100);
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    // Randomly determine if data is valid (70% chance of being valid)
    const isValid = Math.random() > 0.3;
    
    let result: ValidationResult;
    
    if (isValid) {
      result = {
        isValid: true,
        warnings: [
          'Consider adding more voltage sweep points for better accuracy',
          'Temperature sweep could improve model robustness'
        ]
      };
    } else {
      // Generate random validation errors
      const errors: ValidationError[] = [];
      const errorTypes = [
        { section: 'Schematic', issue: 'Missing ground connection' },
        { section: 'Configuration', issue: 'Invalid sweep parameters' },
        { section: 'Simulation', issue: 'Convergence criteria too strict' },
        { section: 'Device Setup', issue: 'Incompatible device configuration' },
      ];
      
      const numErrors = Math.floor(Math.random() * 3) + 1;
      for (let i = 0; i < numErrors; i++) {
        errors.push(errorTypes[Math.floor(Math.random() * errorTypes.length)]);
      }
      
      result = {
        isValid: false,
        errors,
        warnings: ['Testbench validation failed. Please review and correct the issues.']
      };
    }

    setValidationResult(result);
    setIsValidating(false);
    setHasValidated(true);
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    // Validate mandatory fields
    if (!metadata.name.trim()) newErrors.name = 'Testbench name is required';
    if (!metadata.testbench_type.trim()) newErrors.testbench_type = 'Testbench type is required';
    if (!metadata.analysis_type.trim()) newErrors.analysis_type = 'Analysis type is required';
    if (!schematicFile && !configFile) newErrors.files = 'Please upload at least one file (schematic or configuration)';
    
    // Validate email format if provided
    if (metadata.author_email && !metadata.author_email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      newErrors.author_email = 'Invalid email format';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validateForm()) {
      // Scroll to first error
      if (errors.files || errors.name) scrollToSection('file');
      else if (errors.testbench_type || errors.analysis_type) scrollToSection('testbench');
      else if (errors.author_email) scrollToSection('author');
      return;
    }
    
    if (!hasValidated) {
      setErrors({ validation: 'Please validate the testbench before uploading' });
      scrollToSection('validation');
      return;
    }
    
    // Construct the testbench object
    const testbench: any = {
      testbench_id: `TB-${Date.now()}`,
      name: metadata.name,
      version: metadata.version,
      category: metadata.category,
      description: metadata.description,
      testbench_type: metadata.testbench_type,
      analysis_type: metadata.analysis_type,
      device_types: metadata.device_types.split(',').map(type => type.trim()).filter(type => type),
      supported_models: metadata.supported_models.split(',').map(model => model.trim()).filter(model => model),
      complexity: metadata.complexity,
      simulation_settings: {
        simulation_time: metadata.simulation_time,
        step_size: metadata.step_size,
        convergence_criteria: metadata.convergence_criteria,
        temperature_range: metadata.temperature_range,
        voltage_range: metadata.voltage_range,
        current_range: metadata.current_range,
      },
      configuration: fileContent || {},
      schematic: schematicFile ? `schematic_${schematicFile.name}` : null,
      documentation_url: metadata.documentation_url,
      examples_included: metadata.examples_included,
      notes: metadata.notes,
      validation_status: validationResult?.isValid ? 'Validated' : 'Not Validated',
      validation_date: validationResult ? new Date().toISOString() : undefined,
      author: {
        name: metadata.author_name,
        email: metadata.author_email,
        organization: metadata.author_organization,
      },
      tags: metadata.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
      timestamps: {
        created: new Date().toISOString(),
        modified: new Date().toISOString(),
      },
    };

    onUpload(testbench);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Upload Testbench"
      size="xl"
      footer={
        <div className="flex justify-between w-full">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={!hasValidated || isValidating}
          >
            Confirm Upload
          </Button>
        </div>
      }
    >
      <div className="flex gap-6">
        {/* Left Sidebar - Navigation */}
        <div className="w-64 flex-shrink-0">
          <nav className="space-y-1 sticky top-0">
            {sections.map((section) => {
              const Icon = section.icon;
              const isActive = activeSection === section.id;
              const isCompleted = 
                (section.id === 'file' && (schematicFile || configFile) && metadata.name) ||
                (section.id === 'testbench' && metadata.testbench_type && metadata.analysis_type) ||
                (section.id === 'simulation' && metadata.temperature_range) ||
                (section.id === 'documentation' && metadata.documentation_url) ||
                (section.id === 'author' && metadata.author_name) ||
                (section.id === 'validation' && hasValidated);
              
              return (
                <button
                  key={section.id}
                  onClick={() => scrollToSection(section.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive 
                      ? 'bg-purple-100 text-purple-700 border-l-4 border-purple-600' 
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${isCompleted ? 'text-green-500' : ''}`} />
                  <span className="flex-1 text-left">{section.label}</span>
                  {isCompleted && (
                    section.id === 'validation' && validationResult && !validationResult.isValid ? (
                      <AlertTriangle className="w-4 h-4 text-yellow-500" />
                    ) : (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    )
                  )}
                  <ChevronRight className={`w-4 h-4 ${isActive ? 'text-purple-600' : 'text-gray-400'}`} />
                </button>
              );
            })}
          </nav>
          
          {/* Progress Indicator */}
          <div className="mt-6 px-3">
            <div className="text-xs text-gray-500 mb-2">Upload Progress</div>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${(schematicFile || configFile) ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span className="text-xs text-gray-600">Files uploaded</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${metadata.name && metadata.testbench_type ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span className="text-xs text-gray-600">Required fields filled</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${hasValidated ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span className="text-xs text-gray-600">Testbench validated</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Content Area - All Sections */}
        <div ref={scrollContainerRef} className="flex-1 max-h-[70vh] overflow-y-auto pr-4">
          {/* File & Basic Info Section */}
          <div ref={fileRef} id="file-section" className="mb-8">
            <div className="mb-4 pb-2 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">File & Basic Information</h2>
              <p className="text-sm text-gray-500 mt-1">Upload testbench files and provide basic information</p>
            </div>
            
            <div className="space-y-4">
              {/* File Upload Grid */}
              <div className="grid grid-cols-2 gap-4">
                {/* Schematic Upload Area */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Schematic File
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-purple-400 transition-colors h-[110px] flex items-center justify-center">
                    <input
                      type="file"
                      accept=".svg,.png,.jpg,.jpeg,.gif,.webp"
                      onChange={handleSchematicUpload}
                      className="hidden"
                      id="schematic-upload"
                    />
                    <label htmlFor="schematic-upload" className="cursor-pointer w-full">
                      {schematicFile ? (
                        <div className="flex flex-col items-center justify-center">
                          <Activity className="w-6 h-6 text-purple-600 mb-1" />
                          <p className="text-sm font-medium text-gray-900 truncate max-w-[150px]" title={schematicFile.name}>
                            {schematicFile.name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {(schematicFile.size / 1024).toFixed(2)} KB
                          </p>
                        </div>
                      ) : (
                        <div className="text-center">
                          <Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                          <p className="text-sm text-gray-600">Upload schematic</p>
                          <p className="text-xs text-gray-400 mt-1">SVG, PNG, JPG, etc.</p>
                        </div>
                      )}
                    </label>
                  </div>
                  {errors.schematic && (
                    <p className="text-xs text-red-600 mt-1">{errors.schematic}</p>
                  )}
                </div>

                {/* Configuration Upload Area */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Configuration File (JSON)
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-purple-400 transition-colors h-[110px] flex items-center justify-center">
                    <input
                      type="file"
                      accept=".json"
                      onChange={handleConfigUpload}
                      className="hidden"
                      id="config-upload"
                    />
                    <label htmlFor="config-upload" className="cursor-pointer w-full">
                      {configFile ? (
                        <div className="flex flex-col items-center justify-center">
                          <FileJson className="w-6 h-6 text-purple-600 mb-1" />
                          <p className="text-sm font-medium text-gray-900 truncate max-w-[150px]" title={configFile.name}>
                            {configFile.name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {(configFile.size / 1024).toFixed(2)} KB
                          </p>
                        </div>
                      ) : (
                        <div className="text-center">
                          <Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                          <p className="text-sm text-gray-600">Upload configuration</p>
                          <p className="text-xs text-gray-400 mt-1">JSON format</p>
                        </div>
                      )}
                    </label>
                  </div>
                  {errors.config && (
                    <p className="text-xs text-red-600 mt-1">{errors.config}</p>
                  )}
                </div>
              </div>

              {errors.files && (
                <p className="text-xs text-red-600">{errors.files}</p>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Testbench Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={metadata.name}
                  onChange={(e) => setMetadata({ ...metadata, name: e.target.value })}
                  className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-purple-500 ${
                    errors.name ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="e.g., DC Sweep - MOSFET Id-Vds"
                />
                {errors.name && (
                  <p className="text-xs text-red-600 mt-1">{errors.name}</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Version</label>
                  <input
                    type="text"
                    value={metadata.version}
                    onChange={(e) => setMetadata({ ...metadata, version: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                    placeholder="1.0"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select
                    value={metadata.category}
                    onChange={(e) => setMetadata({ ...metadata, category: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="DC">DC Analysis</option>
                    <option value="AC">AC Analysis</option>
                    <option value="Transient">Transient</option>
                    <option value="Noise">Noise</option>
                    <option value="Temperature">Temperature</option>
                    <option value="Process">Process Corners</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={metadata.description}
                  onChange={(e) => setMetadata({ ...metadata, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  placeholder="Brief description of the testbench..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tags <span className="text-xs text-gray-500 ml-2">(comma-separated)</span>
                </label>
                <input
                  type="text"
                  value={metadata.tags}
                  onChange={(e) => setMetadata({ ...metadata, tags: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="e.g., dc-sweep, mosfet, output-characteristics"
                />
              </div>
            </div>
          </div>

          {/* Testbench Configuration Section */}
          <div ref={testbenchRef} id="testbench-section" className="mb-8">
            <div className="mb-4 pb-2 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Testbench Configuration</h2>
              <p className="text-sm text-gray-500 mt-1">Specify the testbench type and supported devices</p>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Testbench Type <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={metadata.testbench_type}
                    onChange={(e) => setMetadata({ ...metadata, testbench_type: e.target.value })}
                    className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-purple-500 ${
                      errors.testbench_type ? 'border-red-300' : 'border-gray-300'
                    }`}
                  >
                    <option value="dc_sweep">DC Sweep</option>
                    <option value="ac_sweep">AC Sweep</option>
                    <option value="transient">Transient Analysis</option>
                    <option value="noise">Noise Analysis</option>
                    <option value="monte_carlo">Monte Carlo</option>
                    <option value="corner">Corner Analysis</option>
                  </select>
                  {errors.testbench_type && (
                    <p className="text-xs text-red-600 mt-1">{errors.testbench_type}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Analysis Type <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={metadata.analysis_type}
                    onChange={(e) => setMetadata({ ...metadata, analysis_type: e.target.value })}
                    className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-purple-500 ${
                      errors.analysis_type ? 'border-red-300' : 'border-gray-300'
                    }`}
                  >
                    <option value="DC">DC</option>
                    <option value="AC">AC</option>
                    <option value="Transient">Transient</option>
                    <option value="Mixed">Mixed</option>
                  </select>
                  {errors.analysis_type && (
                    <p className="text-xs text-red-600 mt-1">{errors.analysis_type}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Supported Device Types
                  <span className="text-xs text-gray-500 ml-2">(comma-separated)</span>
                </label>
                <input
                  type="text"
                  value={metadata.device_types}
                  onChange={(e) => setMetadata({ ...metadata, device_types: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="e.g., MOSFET, BJT, Diode"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Supported Models
                  <span className="text-xs text-gray-500 ml-2">(comma-separated)</span>
                </label>
                <input
                  type="text"
                  value={metadata.supported_models}
                  onChange={(e) => setMetadata({ ...metadata, supported_models: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="e.g., BSIM4, PSP, EKV"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Complexity Level</label>
                <select
                  value={metadata.complexity}
                  onChange={(e) => setMetadata({ ...metadata, complexity: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                >
                  <option value="Basic">Basic</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                  <option value="Expert">Expert</option>
                </select>
              </div>
            </div>
          </div>

          {/* Simulation Settings Section */}
          <div ref={simulationRef} id="simulation-section" className="mb-8">
            <div className="mb-4 pb-2 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Simulation Settings</h2>
              <p className="text-sm text-gray-500 mt-1">Define simulation parameters and ranges</p>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Simulation Time</label>
                  <input
                    type="text"
                    value={metadata.simulation_time}
                    onChange={(e) => setMetadata({ ...metadata, simulation_time: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                    placeholder="e.g., 1ms, 100ns"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Step Size</label>
                  <input
                    type="text"
                    value={metadata.step_size}
                    onChange={(e) => setMetadata({ ...metadata, step_size: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                    placeholder="e.g., 10mV, 1ns"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Convergence Criteria</label>
                <input
                  type="text"
                  value={metadata.convergence_criteria}
                  onChange={(e) => setMetadata({ ...metadata, convergence_criteria: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="e.g., 1e-6"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Temperature Range (°C)</label>
                <input
                  type="text"
                  value={metadata.temperature_range}
                  onChange={(e) => setMetadata({ ...metadata, temperature_range: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="e.g., -40 to 125"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Voltage Range</label>
                  <input
                    type="text"
                    value={metadata.voltage_range}
                    onChange={(e) => setMetadata({ ...metadata, voltage_range: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                    placeholder="e.g., 0 to 5V"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Current Range</label>
                  <input
                    type="text"
                    value={metadata.current_range}
                    onChange={(e) => setMetadata({ ...metadata, current_range: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                    placeholder="e.g., 0 to 100mA"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Documentation Section */}
          <div ref={documentationRef} id="documentation-section" className="mb-8">
            <div className="mb-4 pb-2 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Documentation</h2>
              <p className="text-sm text-gray-500 mt-1">Provide documentation and notes</p>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Documentation URL</label>
                <input
                  type="url"
                  value={metadata.documentation_url}
                  onChange={(e) => setMetadata({ ...metadata, documentation_url: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="https://example.com/testbench-docs"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="examples-included"
                  checked={metadata.examples_included}
                  onChange={(e) => setMetadata({ ...metadata, examples_included: e.target.checked })}
                  className="w-4 h-4 text-purple-600 rounded border-gray-300 focus:ring-purple-500"
                />
                <label htmlFor="examples-included" className="text-sm text-gray-700">
                  Examples included in testbench
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Additional Notes</label>
                <textarea
                  value={metadata.notes}
                  onChange={(e) => setMetadata({ ...metadata, notes: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  placeholder="Any additional notes or special instructions..."
                />
              </div>
            </div>
          </div>

          {/* Author Information Section */}
          <div ref={authorRef} id="author-section" className="mb-8">
            <div className="mb-4 pb-2 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Author Information</h2>
              <p className="text-sm text-gray-500 mt-1">Provide author and contact information</p>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Author Name</label>
                <input
                  type="text"
                  value={metadata.author_name}
                  onChange={(e) => setMetadata({ ...metadata, author_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="Your full name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Author Email</label>
                <input
                  type="email"
                  value={metadata.author_email}
                  onChange={(e) => setMetadata({ ...metadata, author_email: e.target.value })}
                  className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-purple-500 ${
                    errors.author_email ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="your.email@company.com"
                />
                {errors.author_email && (
                  <p className="text-xs text-red-600 mt-1">{errors.author_email}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                <input
                  type="text"
                  value={metadata.author_organization}
                  onChange={(e) => setMetadata({ ...metadata, author_organization: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="e.g., Engineering, R&D, Design"
                />
              </div>
            </div>
          </div>

          {/* Validation Section */}
          <div ref={validationRef} id="validation-section" className="mb-8">
            <div className="mb-4 pb-2 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Testbench Validation</h2>
              <p className="text-sm text-gray-500 mt-1">Validate testbench configuration and parameters</p>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-8">
              {isValidating ? (
                <div className="text-center">
                  <Loader2 className="w-16 h-16 mx-auto text-purple-600 mb-4 animate-spin" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Validating Testbench
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Checking configuration and parameters...
                  </p>
                  <div className="w-64 mx-auto bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${validationProgress}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    {Math.round(validationProgress)}% complete
                  </p>
                </div>
              ) : !hasValidated ? (
                <div className="text-center">
                  <Shield className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Testbench Validation Required
                  </h3>
                  <p className="text-sm text-gray-600 mb-6">
                    Validate your testbench to check for configuration issues
                  </p>
                  <button
                    onClick={validateData}
                    disabled={!schematicFile && !configFile}
                    className="px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg font-medium hover:from-purple-700 hover:to-purple-800 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center gap-2 mx-auto"
                  >
                    <Shield className="w-5 h-5" />
                    Validate Testbench
                  </button>
                </div>
              ) : validationResult ? (
                <div className="text-center">
                  {validationResult.isValid ? (
                    <>
                      <CheckCircle className="w-16 h-16 mx-auto text-green-500 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Validation Successful
                      </h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Your testbench has passed all validation checks
                      </p>
                      {validationResult.warnings && validationResult.warnings.length > 0 && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-left mt-4 max-w-2xl mx-auto">
                          <p className="text-sm font-medium text-yellow-800 mb-2">Suggestions:</p>
                          <ul className="space-y-1">
                            {validationResult.warnings.map((warning, idx) => (
                              <li key={idx} className="flex items-start gap-2 text-xs text-yellow-700">
                                <AlertTriangle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                                {warning}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-16 h-16 mx-auto text-red-500 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Validation Failed
                      </h3>
                      <p className="text-sm text-gray-600 mb-2">
                        {validationResult.errors?.length} issues found in your testbench
                      </p>
                      <p className="text-sm text-gray-500 mb-4">
                        You can still upload the testbench and fix the issues later.
                      </p>
                      {validationResult.errors && validationResult.errors.length > 0 && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-left mt-4 max-h-64 overflow-y-auto max-w-2xl mx-auto">
                          <p className="text-sm font-medium text-red-800 mb-2">Issues found:</p>
                          <ul className="space-y-2">
                            {validationResult.errors.map((error, idx) => (
                              <li key={idx} className="flex items-start gap-2 bg-white border border-red-200 rounded p-2">
                                <X className="w-3 h-3 text-red-500 mt-0.5 flex-shrink-0" />
                                <div className="text-xs">
                                  <span className="font-medium text-gray-900">
                                    {error.section}
                                  </span>
                                  <p className="text-gray-600 mt-0.5">{error.issue}</p>
                                </div>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </>
                  )}
                  
                  <button
                    onClick={validateData}
                    className="mt-6 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
                  >
                    Re-validate
                  </button>
                </div>
              ) : null}
              
              {errors.validation && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 mt-4">
                  <p className="text-sm text-red-600 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    {errors.validation}
                  </p>
                </div>
              )}
            </div>
          </div>
          
          {/* Extra space for proper scrolling of last section */}
          <div className="h-64"></div>
        </div>
      </div>
    </Modal>
  );
};

export default TestbenchUploadModal;