import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  Upload, FileJson, AlertCircle, CheckCircle, X, Loader2, AlertTriangle,
  ChevronRight, Cpu, LineChart, User, Shield
} from 'lucide-react';
import { Modal, Button } from '../ui';

interface ReferenceDataUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (data: any) => void;
}

interface ValidationError {
  page: string;
  curve?: number;
  issue: string;
}

interface ValidationResult {
  isValid: boolean;
  errors?: ValidationError[];
  warnings?: string[];
}

const ReferenceDataUploadModal: React.FC<ReferenceDataUploadModalProps> = ({
  isOpen,
  onClose,
  onUpload,
}) => {
  const [activeSection, setActiveSection] = useState<string>('file');
  const [file, setFile] = useState<File | null>(null);
  const [fileContent, setFileContent] = useState<any>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [validationProgress, setValidationProgress] = useState(0);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [hasValidated, setHasValidated] = useState(false);
  
  // Refs for sections
  const fileRef = useRef<HTMLDivElement>(null);
  const deviceRef = useRef<HTMLDivElement>(null);
  const measurementRef = useRef<HTMLDivElement>(null);
  const authorRef = useRef<HTMLDivElement>(null);
  const validationRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  
  // Metadata fields
  const [metadata, setMetadata] = useState({
    // File & Basic Info
    name: '',
    version: '1.0',
    data_type: 'measurement',
    description: '',
    tags: '',
    
    // Device Information
    device_type: 'mosfet',
    transistor_type: 'nmos',
    technology_node: '',
    foundry: '',
    process_variant: '',
    
    // Measurement Info
    equipment: '',
    operator: '',
    measurement_date: new Date().toISOString().split('T')[0],
    lab_location: '',
    
    // Author Info
    author_name: '',
    author_email: '',
    author_department: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Section configuration
  const sections = useMemo(() => [
    { id: 'file', label: 'File & Basic Info', icon: FileJson, ref: fileRef },
    { id: 'device', label: 'Device Information', icon: Cpu, ref: deviceRef },
    { id: 'measurement', label: 'Measurement Details', icon: LineChart, ref: measurementRef },
    { id: 'author', label: 'Author Information', icon: User, ref: authorRef },
    { id: 'validation', label: 'Validation', icon: Shield, ref: validationRef },
  ], []);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setFile(null);
      setFileContent(null);
      setValidationResult(null);
      setValidationProgress(0);
      setHasValidated(false);
      setActiveSection('file');
      setMetadata({
        name: '',
        version: '1.0',
        data_type: 'measurement',
        description: '',
        tags: '',
        device_type: 'mosfet',
        transistor_type: 'nmos',
        technology_node: '',
        foundry: '',
        process_variant: '',
        equipment: '',
        operator: '',
        measurement_date: new Date().toISOString().split('T')[0],
        lab_location: '',
        author_name: '',
        author_email: '',
        author_department: '',
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
          if (rect.top - containerTop <= 20) { // Threshold for section detection
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

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;

    if (!uploadedFile.name.endsWith('.json')) {
      setErrors({ file: 'Please upload a JSON file' });
      return;
    }

    setFile(uploadedFile);
    setErrors({});
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
        if (json.data_type) setMetadata(prev => ({ ...prev, data_type: json.data_type }));
        if (json.description) setMetadata(prev => ({ ...prev, description: json.description }));
        
        if (json.device_info) {
          if (json.device_info.device_type) setMetadata(prev => ({ ...prev, device_type: json.device_info.device_type }));
          if (json.device_info.transistor_type) setMetadata(prev => ({ ...prev, transistor_type: json.device_info.transistor_type }));
          if (json.device_info.technology_node) setMetadata(prev => ({ ...prev, technology_node: json.device_info.technology_node }));
          if (json.device_info.foundry) setMetadata(prev => ({ ...prev, foundry: json.device_info.foundry }));
          if (json.device_info.process_variant) setMetadata(prev => ({ ...prev, process_variant: json.device_info.process_variant }));
        }
        
        if (json.measurement_info) {
          if (json.measurement_info.operator) setMetadata(prev => ({ ...prev, operator: json.measurement_info.operator }));
          if (json.measurement_info.measurement_date) {
            const date = new Date(json.measurement_info.measurement_date).toISOString().split('T')[0];
            setMetadata(prev => ({ ...prev, measurement_date: date }));
          }
          if (json.measurement_info.equipment) setMetadata(prev => ({ ...prev, equipment: json.measurement_info.equipment }));
        }
        
        if (json.author) {
          if (json.author.name) setMetadata(prev => ({ ...prev, author_name: json.author.name }));
          if (json.author.email) setMetadata(prev => ({ ...prev, author_email: json.author.email }));
          if (json.author.department) setMetadata(prev => ({ ...prev, author_department: json.author.department }));
        }
        
        if (json.tags && Array.isArray(json.tags)) {
          setMetadata(prev => ({ ...prev, tags: json.tags.join(', ') }));
        }
      } catch (error) {
        setErrors({ file: 'Invalid JSON file format' });
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
          'Some data points have high noise levels',
          'Temperature compensation may be needed for accurate modeling'
        ]
      };
    } else {
      // Generate random validation errors
      const errors: ValidationError[] = [];
      
      if (fileContent?.data && Array.isArray(fileContent.data)) {
        // Random page errors
        const numPageErrors = Math.floor(Math.random() * 3) + 1;
        for (let i = 0; i < numPageErrors && i < fileContent.data.length; i++) {
          const page = fileContent.data[i];
          const errorTypes = [
            'Non-monotonic data detected',
            'Outliers detected in measurement',
            'Missing data points',
            'Discontinuity in curves',
            'Invalid parameter range'
          ];
          
          errors.push({
            page: page.page || `page_${i}`,
            curve: Math.random() > 0.5 ? Math.floor(Math.random() * 3) : undefined,
            issue: errorTypes[Math.floor(Math.random() * errorTypes.length)]
          });
        }
      }
      
      result = {
        isValid: false,
        errors,
        warnings: ['Data validation failed. Please review and correct the issues.']
      };
    }

    setValidationResult(result);
    setIsValidating(false);
    setHasValidated(true);
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    // Validate mandatory fields
    if (!metadata.name.trim()) newErrors.name = 'Name is required';
    if (!metadata.technology_node.trim()) newErrors.technology_node = 'Technology node is required';
    if (!file) newErrors.file = 'Please upload a file';
    
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
      if (errors.file) scrollToSection('file');
      else if (errors.name) scrollToSection('file');
      else if (errors.technology_node) scrollToSection('device');
      else if (errors.author_email) scrollToSection('author');
      return;
    }
    
    if (!hasValidated) {
      setErrors({ validation: 'Please validate the data before uploading' });
      scrollToSection('validation');
      return;
    }
    
    // Construct the reference data object
    const referenceData: any = {
      data_id: `REF-${Date.now()}`,
      name: metadata.name,
      version: metadata.version,
      data_type: metadata.data_type,
      description: metadata.description,
      device_info: {
        device_type: metadata.device_type,
        transistor_type: metadata.transistor_type,
        technology_node: metadata.technology_node,
        foundry: metadata.foundry,
        process_variant: metadata.process_variant,
      },
      measurement_info: {
        equipment: metadata.equipment,
        operator: metadata.operator,
        measurement_date: metadata.measurement_date,
        lab_location: metadata.lab_location,
      },
      data_quality: {
        validated: validationResult?.isValid || false,
        validation_date: validationResult ? new Date().toISOString() : undefined,
        quality_score: validationResult?.isValid ? 0.95 : 0.5,
        completeness: 1.0,
      },
      author: {
        name: metadata.author_name,
        email: metadata.author_email,
        department: metadata.author_department,
      },
      tags: metadata.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
      data: fileContent?.data || [],
      timestamps: {
        created: new Date().toISOString(),
        modified: new Date().toISOString(),
      },
    };

    onUpload(referenceData);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Upload Reference Data"
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
                (section.id === 'file' && file && metadata.name) ||
                (section.id === 'device' && metadata.technology_node) ||
                (section.id === 'measurement' && metadata.equipment) ||
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
                <div className={`w-2 h-2 rounded-full ${file ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span className="text-xs text-gray-600">File uploaded</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${metadata.name && metadata.technology_node ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span className="text-xs text-gray-600">Required fields filled</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${hasValidated ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span className="text-xs text-gray-600">Data validated</span>
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
              <p className="text-sm text-gray-500 mt-1">Upload your data file and provide basic information</p>
            </div>
            
            <div className="space-y-4">
              {/* File Upload Area */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data File <span className="text-red-500">*</span>
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-purple-400 transition-colors">
                  <input
                    type="file"
                    accept=".json"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    {file ? (
                      <div className="flex items-center justify-center gap-3">
                        <FileJson className="w-8 h-8 text-purple-600" />
                        <div className="text-left">
                          <p className="text-sm font-medium text-gray-900">{file.name}</p>
                          <p className="text-xs text-gray-500">
                            {(file.size / 1024).toFixed(2)} KB • Click to change
                          </p>
                        </div>
                      </div>
                    ) : (
                      <>
                        <Upload className="w-10 h-10 mx-auto text-gray-400 mb-3" />
                        <p className="text-sm text-gray-600">Click to upload JSON file</p>
                        <p className="text-xs text-gray-500 mt-1">or drag and drop</p>
                      </>
                    )}
                  </label>
                </div>
                {errors.file && (
                  <p className="text-xs text-red-600 mt-1">{errors.file}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Dataset Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={metadata.name}
                  onChange={(e) => setMetadata({ ...metadata, name: e.target.value })}
                  className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-purple-500 ${
                    errors.name ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="e.g., 28nm NMOS DC Characterization"
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Data Type <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={metadata.data_type}
                    onChange={(e) => setMetadata({ ...metadata, data_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="measurement">Measurement</option>
                    <option value="simulation">Simulation</option>
                    <option value="tcad">TCAD</option>
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
                  placeholder="Brief description of the dataset..."
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
                  placeholder="e.g., dc-characterization, nmos, 28nm"
                />
              </div>
            </div>
          </div>

          {/* Device Information Section */}
          <div ref={deviceRef} id="device-section" className="mb-8">
            <div className="mb-4 pb-2 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Device Information</h2>
              <p className="text-sm text-gray-500 mt-1">Specify the device characteristics and technology details</p>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Device Type <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={metadata.device_type}
                    onChange={(e) => setMetadata({ ...metadata, device_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="mosfet">MOSFET</option>
                    <option value="bjt">BJT</option>
                    <option value="diode">Diode</option>
                    <option value="resistor">Resistor</option>
                    <option value="capacitor">Capacitor</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Transistor Type <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={metadata.transistor_type}
                    onChange={(e) => setMetadata({ ...metadata, transistor_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                    disabled={metadata.device_type !== 'mosfet' && metadata.device_type !== 'bjt'}
                  >
                    <option value="nmos">NMOS</option>
                    <option value="pmos">PMOS</option>
                    <option value="npn">NPN</option>
                    <option value="pnp">PNP</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Technology Node <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={metadata.technology_node}
                  onChange={(e) => setMetadata({ ...metadata, technology_node: e.target.value })}
                  className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-purple-500 ${
                    errors.technology_node ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="e.g., 28nm, 14nm, 65nm"
                />
                {errors.technology_node && (
                  <p className="text-xs text-red-600 mt-1">{errors.technology_node}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Foundry</label>
                <input
                  type="text"
                  value={metadata.foundry}
                  onChange={(e) => setMetadata({ ...metadata, foundry: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="e.g., TSMC, GlobalFoundries, Intel"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Process Variant</label>
                <input
                  type="text"
                  value={metadata.process_variant}
                  onChange={(e) => setMetadata({ ...metadata, process_variant: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="e.g., Low Power, High Performance, GP"
                />
              </div>
            </div>
          </div>

          {/* Measurement Details Section */}
          <div ref={measurementRef} id="measurement-section" className="mb-8">
            <div className="mb-4 pb-2 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Measurement Details</h2>
              <p className="text-sm text-gray-500 mt-1">Add measurement or simulation details</p>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Measurement Equipment</label>
                <input
                  type="text"
                  value={metadata.equipment}
                  onChange={(e) => setMetadata({ ...metadata, equipment: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="e.g., Keysight B1500A, Agilent 4156C"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Operator</label>
                <input
                  type="text"
                  value={metadata.operator}
                  onChange={(e) => setMetadata({ ...metadata, operator: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="Name of the person who performed the measurement"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Measurement Date</label>
                  <input
                    type="date"
                    value={metadata.measurement_date}
                    onChange={(e) => setMetadata({ ...metadata, measurement_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Lab Location</label>
                  <input
                    type="text"
                    value={metadata.lab_location}
                    onChange={(e) => setMetadata({ ...metadata, lab_location: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                    placeholder="e.g., Building A, Room 201"
                  />
                </div>
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
                  value={metadata.author_department}
                  onChange={(e) => setMetadata({ ...metadata, author_department: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="e.g., Device Characterization, R&D"
                />
              </div>
            </div>
          </div>

          {/* Validation Section */}
          <div ref={validationRef} id="validation-section" className="mb-8">
            <div className="mb-4 pb-2 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Data Validation</h2>
              <p className="text-sm text-gray-500 mt-1">Validate data quality before uploading</p>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-8">
              {isValidating ? (
                <div className="text-center">
                  <Loader2 className="w-16 h-16 mx-auto text-purple-600 mb-4 animate-spin" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Validating Data
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Checking data quality and integrity...
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
                    Data Validation Required
                  </h3>
                  <p className="text-sm text-gray-600 mb-6">
                    Validate your data to check for quality issues before uploading
                  </p>
                  <button
                    onClick={validateData}
                    disabled={!file}
                    className="px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg font-medium hover:from-purple-700 hover:to-purple-800 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center gap-2 mx-auto"
                  >
                    <Shield className="w-5 h-5" />
                    Validate Data
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
                        Your data has passed all quality checks
                      </p>
                      {validationResult.warnings && validationResult.warnings.length > 0 && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-left mt-4 max-w-2xl mx-auto">
                          <p className="text-sm font-medium text-yellow-800 mb-2">Warnings:</p>
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
                        {validationResult.errors?.length} issues found in your data
                      </p>
                      <p className="text-sm text-gray-500 mb-4">
                        You can still upload the data and fix the issues later. The data will be marked as unvalidated.
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
                                    Page: {error.page}
                                    {error.curve !== undefined && ` | Curve: ${error.curve + 1}`}
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

export default ReferenceDataUploadModal;