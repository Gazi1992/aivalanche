import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  FileJson, AlertCircle, CheckCircle, X, Loader2, AlertTriangle,
  ChevronRight, Code2, Book, User, Shield, Layers, Table
} from 'lucide-react';
import { Modal, Button } from '../ui';

interface ModelTemplateUploadModalProps {
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

const ModelTemplateUploadModal: React.FC<ModelTemplateUploadModalProps> = ({
  isOpen,
  onClose,
  onUpload,
}) => {
  const [activeSection, setActiveSection] = useState<string>('file');
  const [uploadedFiles, setUploadedFiles] = useState<{
    metadata: File | null;
    parameters: File | null;
    circuit: File | null;
    documentation: File[] | null;
    libraries: File[] | null;
    other: File[] | null;
  }>({
    metadata: null,
    parameters: null,
    circuit: null,
    documentation: null,
    libraries: null,
    other: null,
  });
  const [metadataContent, setMetadataContent] = useState<any>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [validationProgress, setValidationProgress] = useState(0);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [hasValidated, setHasValidated] = useState(false);
  
  // Refs for sections
  const fileRef = useRef<HTMLDivElement>(null);
  const modelRef = useRef<HTMLDivElement>(null);
  const parametersRef = useRef<HTMLDivElement>(null);
  const documentationRef = useRef<HTMLDivElement>(null);
  const authorRef = useRef<HTMLDivElement>(null);
  const validationRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  
  // Metadata fields
  const [metadata, setMetadata] = useState({
    // File & Basic Info
    name: '',
    version: '1.0',
    category: 'MOSFET',
    description: '',
    tags: '',
    
    // Model Information
    model_type: 'BSIM4',
    model_level: '',
    technology_nodes: '',
    vendor: '',
    license: 'Open Source',
    
    // Parameter Settings
    default_params: '',
    parameter_count: '',
    instance_params: '',
    model_params: '',
    
    // Documentation
    documentation_url: '',
    examples_included: false,
    validation_status: 'Not Validated',
    
    // Author Info
    author_name: '',
    author_email: '',
    author_organization: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Section configuration
  const sections = useMemo(() => [
    { id: 'file', label: 'File & Basic Info', icon: FileJson, ref: fileRef },
    { id: 'model', label: 'Model Information', icon: Code2, ref: modelRef },
    { id: 'parameters', label: 'Parameter Settings', icon: Table, ref: parametersRef },
    { id: 'documentation', label: 'Documentation', icon: Book, ref: documentationRef },
    { id: 'author', label: 'Author Information', icon: User, ref: authorRef },
    { id: 'validation', label: 'Validation', icon: Shield, ref: validationRef },
  ], []);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setUploadedFiles({
        metadata: null,
        parameters: null,
        circuit: null,
        documentation: null,
        libraries: null,
        other: null,
      });
      setMetadataContent(null);
      setValidationResult(null);
      setValidationProgress(0);
      setHasValidated(false);
      setActiveSection('file');
      setMetadata({
        name: '',
        version: '1.0',
        category: 'MOSFET',
        description: '',
        tags: '',
        model_type: 'BSIM4',
        model_level: '',
        technology_nodes: '',
        vendor: '',
        license: 'Open Source',
        default_params: '',
        parameter_count: '',
        instance_params: '',
        model_params: '',
        documentation_url: '',
        examples_included: false,
        validation_status: 'Not Validated',
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

  const handleMetadataUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;

    if (!uploadedFile.name.endsWith('.json')) {
      setErrors({ metadata: 'Please upload a JSON metadata file' });
      return;
    }

    setUploadedFiles(prev => ({ ...prev, metadata: uploadedFile }));
    setErrors({});
    setHasValidated(false);
    setValidationResult(null);

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const json = JSON.parse(event.target?.result as string);
        setMetadataContent(json);
        
        // Auto-fill metadata if present in the file
        if (json.name) setMetadata(prev => ({ ...prev, name: json.name }));
        if (json.version) setMetadata(prev => ({ ...prev, version: json.version }));
        if (json.category) setMetadata(prev => ({ ...prev, category: json.category }));
        if (json.description) setMetadata(prev => ({ ...prev, description: json.description }));
        if (json.model_type) setMetadata(prev => ({ ...prev, model_type: json.model_type }));
        if (json.model_level) setMetadata(prev => ({ ...prev, model_level: json.model_level }));
        if (json.technology_nodes) setMetadata(prev => ({ ...prev, technology_nodes: json.technology_nodes.join(', ') }));
        if (json.vendor) setMetadata(prev => ({ ...prev, vendor: json.vendor }));
        if (json.license) setMetadata(prev => ({ ...prev, license: json.license }));
        if (json.author) {
          if (json.author.name) setMetadata(prev => ({ ...prev, author_name: json.author.name }));
          if (json.author.email) setMetadata(prev => ({ ...prev, author_email: json.author.email }));
          if (json.author.organization) setMetadata(prev => ({ ...prev, author_organization: json.author.organization }));
        }
        if (json.tags && Array.isArray(json.tags)) {
          setMetadata(prev => ({ ...prev, tags: json.tags.join(', ') }));
        }
        if (json.parameters) {
          const paramCount = Object.keys(json.parameters).length;
          setMetadata(prev => ({ ...prev, parameter_count: paramCount.toString() }));
        }
      } catch (error) {
        setErrors({ metadata: 'Invalid JSON file format' });
        setMetadataContent(null);
      }
    };
    reader.readAsText(uploadedFile);
  };

  const handleFileUpload = (type: 'parameters' | 'circuit', e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;

    if (type === 'parameters' && !uploadedFile.name.endsWith('.csv')) {
      setErrors({ [type]: 'Please upload a CSV file for parameters' });
      return;
    }
    if (type === 'circuit' && !uploadedFile.name.endsWith('.cir')) {
      setErrors({ [type]: 'Please upload a .cir circuit file' });
      return;
    }

    setUploadedFiles(prev => ({ ...prev, [type]: uploadedFile }));
    setErrors(prev => ({ ...prev, [type]: '' }));
    setHasValidated(false);
    setValidationResult(null);
  };

  const handleMultipleFileUpload = (type: 'documentation' | 'libraries' | 'other', e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFiles = e.target.files;
    if (!uploadedFiles || uploadedFiles.length === 0) return;

    const filesArray = Array.from(uploadedFiles);
    setUploadedFiles(prev => {
      const existingFiles = prev[type];
      if (existingFiles && Array.isArray(existingFiles)) {
        return {
          ...prev, 
          [type]: [...existingFiles, ...filesArray]
        };
      } else {
        return {
          ...prev, 
          [type]: filesArray
        };
      }
    });
    setErrors(prev => ({ ...prev, [type]: '' }));
    setHasValidated(false);
    setValidationResult(null);
  };

  const removeFile = (type: 'documentation' | 'libraries' | 'other', index: number) => {
    setUploadedFiles(prev => {
      const files = prev[type];
      if (!files) return prev;
      const newFiles = files.filter((_, i) => i !== index);
      return { ...prev, [type]: newFiles.length > 0 ? newFiles : null };
    });
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
          'Some parameters may need adjustment for specific technologies',
          'Consider adding more documentation examples'
        ]
      };
    } else {
      // Generate random validation errors
      const errors: ValidationError[] = [];
      const errorTypes = [
        { section: 'Parameters', issue: 'Missing required parameter definitions' },
        { section: 'Model', issue: 'Incompatible model level specified' },
        { section: 'Documentation', issue: 'Missing parameter descriptions' },
        { section: 'File Structure', issue: 'Invalid parameter format detected' },
      ];
      
      const numErrors = Math.floor(Math.random() * 3) + 1;
      for (let i = 0; i < numErrors; i++) {
        errors.push(errorTypes[Math.floor(Math.random() * errorTypes.length)]);
      }
      
      result = {
        isValid: false,
        errors,
        warnings: ['Model template validation failed. Please review and correct the issues.']
      };
    }

    setValidationResult(result);
    setIsValidating(false);
    setHasValidated(true);
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    // Validate mandatory fields
    if (!metadata.name.trim()) newErrors.name = 'Model name is required';
    if (!metadata.model_type.trim()) newErrors.model_type = 'Model type is required';
    if (!metadata.technology_nodes.trim()) newErrors.technology_nodes = 'Technology nodes are required';
    if (!uploadedFiles.circuit) newErrors.circuit = 'Circuit file (.cir) is required';
    if (!uploadedFiles.parameters) newErrors.parameters = 'Parameters file (.csv) is required';
    
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
      if (errors.circuit || errors.parameters || errors.name) scrollToSection('file');
      else if (errors.model_type || errors.technology_nodes) scrollToSection('model');
      else if (errors.author_email) scrollToSection('author');
      return;
    }
    
    if (!hasValidated) {
      setErrors({ validation: 'Please validate the model template before uploading' });
      scrollToSection('validation');
      return;
    }
    
    // Construct the model template object
    const modelTemplate: any = {
      template_id: `TPL-${Date.now()}`,
      name: metadata.name,
      version: metadata.version,
      category: metadata.category,
      description: metadata.description,
      model_type: metadata.model_type,
      model_level: metadata.model_level,
      technology_nodes: metadata.technology_nodes.split(',').map(node => node.trim()).filter(node => node),
      vendor: metadata.vendor,
      license: metadata.license,
      parameters: metadataContent?.parameters || {},
      default_values: metadataContent?.default_values || {},
      files: {
        metadata: uploadedFiles.metadata?.name,
        parameters: uploadedFiles.parameters?.name,
        circuit: uploadedFiles.circuit?.name,
        documentation: uploadedFiles.documentation?.map(f => f.name) || [],
        libraries: uploadedFiles.libraries?.map(f => f.name) || [],
        other: uploadedFiles.other?.map(f => f.name) || [],
      },
      documentation_url: metadata.documentation_url,
      examples_included: metadata.examples_included,
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

    onUpload(modelTemplate);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Upload Model Template"
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
                (section.id === 'file' && uploadedFiles.circuit && uploadedFiles.parameters && metadata.name) ||
                (section.id === 'model' && metadata.model_type && metadata.technology_nodes) ||
                (section.id === 'parameters' && metadata.parameter_count) ||
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
                <div className={`w-2 h-2 rounded-full ${uploadedFiles.circuit && uploadedFiles.parameters ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span className="text-xs text-gray-600">Required files uploaded</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${metadata.name && metadata.model_type && metadata.technology_nodes ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span className="text-xs text-gray-600">Required fields filled</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${hasValidated ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span className="text-xs text-gray-600">Template validated</span>
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
              <p className="text-sm text-gray-500 mt-1">Upload your model template file and provide basic information</p>
            </div>
            
            <div className="space-y-6">
              {/* First Row - Required Files */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Required Files</h3>
                <div className="grid grid-cols-2 gap-4">
                  {/* Circuit File Upload */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Circuit File (.cir) <span className="text-red-500">*</span>
                    </label>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-purple-400 transition-colors h-[100px] flex items-center justify-center">
                      <input
                        type="file"
                        accept=".cir"
                        onChange={(e) => handleFileUpload('circuit', e)}
                        className="hidden"
                        id="circuit-upload"
                      />
                      <label htmlFor="circuit-upload" className="cursor-pointer w-full">
                        {uploadedFiles.circuit ? (
                          <div className="flex flex-col items-center justify-center">
                            <Code2 className="w-6 h-6 text-purple-600 mb-1" />
                            <p className="text-sm font-medium text-gray-900 truncate max-w-[180px]" title={uploadedFiles.circuit.name}>
                              {uploadedFiles.circuit.name}
                            </p>
                            <p className="text-xs text-gray-500">
                              {(uploadedFiles.circuit.size / 1024).toFixed(2)} KB
                            </p>
                          </div>
                        ) : (
                          <div className="text-center">
                            <Code2 className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                            <p className="text-sm text-gray-600">Upload .cir file</p>
                          </div>
                        )}
                      </label>
                    </div>
                    {errors.circuit && (
                      <p className="text-xs text-red-600 mt-1">{errors.circuit}</p>
                    )}
                  </div>

                  {/* Parameters File Upload */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Parameters File (.csv) <span className="text-red-500">*</span>
                    </label>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-purple-400 transition-colors h-[100px] flex items-center justify-center">
                      <input
                        type="file"
                        accept=".csv"
                        onChange={(e) => handleFileUpload('parameters', e)}
                        className="hidden"
                        id="parameters-upload"
                      />
                      <label htmlFor="parameters-upload" className="cursor-pointer w-full">
                        {uploadedFiles.parameters ? (
                          <div className="flex flex-col items-center justify-center">
                            <Table className="w-6 h-6 text-purple-600 mb-1" />
                            <p className="text-sm font-medium text-gray-900 truncate max-w-[180px]" title={uploadedFiles.parameters.name}>
                              {uploadedFiles.parameters.name}
                            </p>
                            <p className="text-xs text-gray-500">
                              {(uploadedFiles.parameters.size / 1024).toFixed(2)} KB
                            </p>
                          </div>
                        ) : (
                          <div className="text-center">
                            <Table className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                            <p className="text-sm text-gray-600">Upload parameters.csv</p>
                          </div>
                        )}
                      </label>
                    </div>
                    {errors.parameters && (
                      <p className="text-xs text-red-600 mt-1">{errors.parameters}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Second Row - Optional Files */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Optional Files</h3>
                <div className="grid grid-cols-3 gap-4">
                  {/* Metadata File Upload */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Metadata (metadata.json)
                    </label>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-3 hover:border-purple-400 transition-colors h-[80px] flex items-center justify-center">
                      <input
                        type="file"
                        accept=".json"
                        onChange={handleMetadataUpload}
                        className="hidden"
                        id="metadata-upload"
                      />
                      <label htmlFor="metadata-upload" className="cursor-pointer w-full">
                        {uploadedFiles.metadata ? (
                          <div className="flex flex-col items-center justify-center">
                            <FileJson className="w-5 h-5 text-purple-600 mb-1" />
                            <p className="text-xs font-medium text-gray-900 truncate max-w-[120px]" title={uploadedFiles.metadata.name}>
                              {uploadedFiles.metadata.name}
                            </p>
                            <p className="text-xs text-gray-500">
                              {(uploadedFiles.metadata.size / 1024).toFixed(1)} KB
                            </p>
                          </div>
                        ) : (
                          <div className="text-center">
                            <FileJson className="w-5 h-5 mx-auto text-gray-400 mb-1" />
                            <p className="text-xs text-gray-600">Upload metadata</p>
                          </div>
                        )}
                      </label>
                    </div>
                  </div>

                  {/* Documentation Files Upload */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Documentation
                    </label>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-3 hover:border-purple-400 transition-colors h-[80px] flex items-center justify-center">
                      <input
                        type="file"
                        accept=".md,.pdf,.txt,.doc,.docx"
                        multiple
                        onChange={(e) => handleMultipleFileUpload('documentation', e)}
                        className="hidden"
                        id="documentation-upload"
                      />
                      <label htmlFor="documentation-upload" className="cursor-pointer w-full">
                        {uploadedFiles.documentation && uploadedFiles.documentation.length > 0 ? (
                          <div className="flex flex-col items-center justify-center">
                            <Book className="w-5 h-5 text-purple-600 mb-1" />
                            <p className="text-xs font-medium text-gray-900">{uploadedFiles.documentation.length} file(s)</p>
                            <p className="text-xs text-gray-500">Add more</p>
                          </div>
                        ) : (
                          <div className="text-center">
                            <Book className="w-5 h-5 mx-auto text-gray-400 mb-1" />
                            <p className="text-xs text-gray-600">Upload docs</p>
                          </div>
                        )}
                      </label>
                    </div>
                  </div>

                  {/* Library Files Upload */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Libraries (.lib)
                    </label>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-3 hover:border-purple-400 transition-colors h-[80px] flex items-center justify-center">
                      <input
                        type="file"
                        accept=".lib"
                        multiple
                        onChange={(e) => handleMultipleFileUpload('libraries', e)}
                        className="hidden"
                        id="libraries-upload"
                      />
                      <label htmlFor="libraries-upload" className="cursor-pointer w-full">
                        {uploadedFiles.libraries && uploadedFiles.libraries.length > 0 ? (
                          <div className="flex flex-col items-center justify-center">
                            <Layers className="w-5 h-5 text-purple-600 mb-1" />
                            <p className="text-xs font-medium text-gray-900">{uploadedFiles.libraries.length} file(s)</p>
                            <p className="text-xs text-gray-500">Add more</p>
                          </div>
                        ) : (
                          <div className="text-center">
                            <Layers className="w-5 h-5 mx-auto text-gray-400 mb-1" />
                            <p className="text-xs text-gray-600">Upload .lib</p>
                          </div>
                        )}
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              {/* File List Display for Multiple Files */}
              {((uploadedFiles.documentation && uploadedFiles.documentation.length > 0) || 
                (uploadedFiles.libraries && uploadedFiles.libraries.length > 0) ||
                (uploadedFiles.other && uploadedFiles.other.length > 0)) && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <h4 className="text-xs font-semibold text-gray-700 mb-2">Uploaded Files</h4>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {uploadedFiles.documentation?.map((file, idx) => (
                      <div key={`doc-${idx}`} className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <Book className="w-3 h-3 text-gray-500" />
                          <span className="text-gray-700">{file.name}</span>
                        </div>
                        <button
                          onClick={() => removeFile('documentation', idx)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ))}
                    {uploadedFiles.libraries?.map((file, idx) => (
                      <div key={`lib-${idx}`} className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <Layers className="w-3 h-3 text-gray-500" />
                          <span className="text-gray-700">{file.name}</span>
                        </div>
                        <button
                          onClick={() => removeFile('libraries', idx)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ))}
                    {uploadedFiles.other?.map((file, idx) => (
                      <div key={`other-${idx}`} className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <FileJson className="w-3 h-3 text-gray-500" />
                          <span className="text-gray-700">{file.name}</span>
                        </div>
                        <button
                          onClick={() => removeFile('other', idx)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Model Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={metadata.name}
                  onChange={(e) => setMetadata({ ...metadata, name: e.target.value })}
                  className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-purple-500 ${
                    errors.name ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="e.g., BSIM4 v4.8.2"
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
                    <option value="MOSFET">MOSFET</option>
                    <option value="BJT">BJT</option>
                    <option value="Diode">Diode</option>
                    <option value="Resistor">Resistor</option>
                    <option value="Capacitor">Capacitor</option>
                    <option value="Other">Other</option>
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
                  placeholder="Brief description of the model template..."
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
                  placeholder="e.g., compact-model, bsim, 28nm"
                />
              </div>
            </div>
          </div>

          {/* Model Information Section */}
          <div ref={modelRef} id="model-section" className="mb-8">
            <div className="mb-4 pb-2 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Model Information</h2>
              <p className="text-sm text-gray-500 mt-1">Specify the model characteristics and compatibility</p>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Model Type <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={metadata.model_type}
                  onChange={(e) => setMetadata({ ...metadata, model_type: e.target.value })}
                  className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-purple-500 ${
                    errors.model_type ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="e.g., BSIM4, PSP, EKV"
                />
                {errors.model_type && (
                  <p className="text-xs text-red-600 mt-1">{errors.model_type}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Model Level</label>
                <input
                  type="text"
                  value={metadata.model_level}
                  onChange={(e) => setMetadata({ ...metadata, model_level: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="e.g., 54, 103"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Technology Nodes <span className="text-red-500">*</span>
                  <span className="text-xs text-gray-500 ml-2">(comma-separated)</span>
                </label>
                <input
                  type="text"
                  value={metadata.technology_nodes}
                  onChange={(e) => setMetadata({ ...metadata, technology_nodes: e.target.value })}
                  className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-purple-500 ${
                    errors.technology_nodes ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="e.g., 28nm, 14nm, 7nm"
                />
                {errors.technology_nodes && (
                  <p className="text-xs text-red-600 mt-1">{errors.technology_nodes}</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Vendor</label>
                  <input
                    type="text"
                    value={metadata.vendor}
                    onChange={(e) => setMetadata({ ...metadata, vendor: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                    placeholder="e.g., Berkeley, ASU"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">License</label>
                  <select
                    value={metadata.license}
                    onChange={(e) => setMetadata({ ...metadata, license: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="Open Source">Open Source</option>
                    <option value="Commercial">Commercial</option>
                    <option value="Academic">Academic</option>
                    <option value="Proprietary">Proprietary</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Parameter Settings Section */}
          <div ref={parametersRef} id="parameters-section" className="mb-8">
            <div className="mb-4 pb-2 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Parameter Settings</h2>
              <p className="text-sm text-gray-500 mt-1">Define model parameters and defaults</p>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Number of Parameters</label>
                <input
                  type="text"
                  value={metadata.parameter_count}
                  onChange={(e) => setMetadata({ ...metadata, parameter_count: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="Auto-detected from file"
                  disabled
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Instance Parameters
                  <span className="text-xs text-gray-500 ml-2">(comma-separated)</span>
                </label>
                <textarea
                  value={metadata.instance_params}
                  onChange={(e) => setMetadata({ ...metadata, instance_params: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  rows={2}
                  placeholder="e.g., W, L, NF, M"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Model Parameters
                  <span className="text-xs text-gray-500 ml-2">(comma-separated)</span>
                </label>
                <textarea
                  value={metadata.model_params}
                  onChange={(e) => setMetadata({ ...metadata, model_params: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  placeholder="e.g., VTH0, U0, VSAT, TOXE"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Default Parameter Values</label>
                <textarea
                  value={metadata.default_params}
                  onChange={(e) => setMetadata({ ...metadata, default_params: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  placeholder="JSON format: {&quot;VTH0&quot;: 0.5, &quot;U0&quot;: 0.03}"
                />
              </div>
            </div>
          </div>

          {/* Documentation Section */}
          <div ref={documentationRef} id="documentation-section" className="mb-8">
            <div className="mb-4 pb-2 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Documentation</h2>
              <p className="text-sm text-gray-500 mt-1">Provide documentation and examples</p>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Documentation URL</label>
                <input
                  type="url"
                  value={metadata.documentation_url}
                  onChange={(e) => setMetadata({ ...metadata, documentation_url: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  placeholder="https://example.com/model-docs"
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
                  Examples included in template
                </label>
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
              <h2 className="text-lg font-semibold text-gray-900">Template Validation</h2>
              <p className="text-sm text-gray-500 mt-1">Validate template structure and parameters</p>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-8">
              {isValidating ? (
                <div className="text-center">
                  <Loader2 className="w-16 h-16 mx-auto text-purple-600 mb-4 animate-spin" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Validating Template
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Checking template structure and parameters...
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
                    Template Validation Required
                  </h3>
                  <p className="text-sm text-gray-600 mb-6">
                    Validate your template to check for structural issues
                  </p>
                  <button
                    onClick={validateData}
                    disabled={!uploadedFiles.circuit || !uploadedFiles.parameters}
                    className="px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg font-medium hover:from-purple-700 hover:to-purple-800 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center gap-2 mx-auto"
                  >
                    <Shield className="w-5 h-5" />
                    Validate Template
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
                        Your template has passed all structural checks
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
                        {validationResult.errors?.length} issues found in your template
                      </p>
                      <p className="text-sm text-gray-500 mb-4">
                        You can still upload the template and fix the issues later.
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

export default ModelTemplateUploadModal;