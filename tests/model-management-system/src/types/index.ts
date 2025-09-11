export interface Model {
  model_id: string;
  name: string;
  version: string;
  type: 'compact' | 'behavioral';
  category: string;
  subcategory?: string;
  base_model: string;
  status: 'draft' | 'in-review' | 'validated' | 'production' | 'deprecated';
  author: Author;
  timestamps: Timestamps;
  tags: string[];
  files: ModelFiles;
  parameters: ModelParameterInfo;
  validation?: ValidationResults;
  description?: string;
  image?: string;
}

export interface ModelFiles {
  entry_point: string; // Main .cir file
  simulation_files: string[]; // .lib and .cir files
  parameters_file: string; // parameters.csv
  metadata_file: string; // metadata.json
  documentation?: string; // documentation.md or .pdf
  lib_directory?: string; // Directory containing additional .lib files
  image?: string; // Optional image file
}

export interface ModelParameterInfo {
  count: number;
  categories?: Record<string, string[]>;
  file_path: string; // Path to parameters.csv
}

export interface ModelParameter {
  name: string;
  subckt: string;
  default: string | number;
  min?: number;
  max?: number;
  unit?: string;
  description?: string;
}

export interface Author {
  name: string;
  email: string;
  department?: string;
}

export interface Timestamps {
  created: string;
  modified: string;
  validated?: string;
  last_accessed?: string;
}

export interface ReferenceData {
  data_id: string;
  name: string;
  type: 'measurement' | 'simulation';
  source: DataSource;
  device: DeviceInfo;
  measurement_conditions?: MeasurementConditions;
  data_format: DataFormat;
  data_quality: DataQuality;
  timestamps: Timestamps;
}

export interface DataSource {
  equipment?: string;
  simulator?: string;
  location?: string;
  operator?: string;
}

export interface DeviceInfo {
  type: string;
  technology: string;
  dimensions?: Record<string, any>;
  lot?: string;
  wafer?: string;
  die?: string;
}

export interface MeasurementConditions {
  temperature: number[];
  temperature_unit: string;
  voltage_range?: { min: number; max: number };
}

export interface DataFormat {
  file_type: string;
  structure?: string;
  total_size?: string;
  data_files?: string[];
}

export interface DataQuality {
  validated: boolean;
  validation_date?: string;
  noise_level?: string;
  completeness?: number;
  quality_score?: number;
}

export interface TestbenchLibrary {
  library_name: string;
  version: string;
  description: string;
  organization: string;
  created: string;
  modified: string;
  license: string;
  testbenches: Testbench[];
  usage_notes: Record<string, string>;
}

export interface Testbench {
  testbench_id: string;
  name: string;
  type: string;
  description: string;
  validated: boolean;
  tags: string[];
  schematic?: string;
  circuit: TestbenchCircuit;
  measurements: string[];
  compatible_devices: string[];
  outputs: Record<string, TestbenchOutput>;
  examples: TestbenchExample[];
}

export interface TestbenchCircuit {
  netlist: string[];
  parameters: Record<string, TestbenchParameter>;
}

export interface TestbenchParameter {
  default: string | number;
  unit: string;
  description: string;
}

export interface TestbenchOutput {
  unit: string;
  description: string;
}

export interface TestbenchExample {
  name: string;
  description: string;
  netlist: string[];
}

export interface CalibratedModel {
  model_id: string;
  name: string;
  description?: string;
  base_model: string;
  model_template_id?: string;
  version: string;
  status: string;
  category: string;
  subcategory?: string;
  technology?: any;
  author?: any;
  calibration_info: CalibrationInfo;
  reference_data: {
    data_id?: string;
    name?: string;
    measurement_data: string[];
    simulation_data?: string[];
    total_points: number;
    temperature_range?: number[];
    voltage_range?: number[];
    data_weight?: Record<string, number>;
  };
  validation?: any;
  files?: any;
  timestamps?: any;
  optimized_parameters?: Record<string, number>;
  validation_results?: ValidationResults;
  performance_metrics?: Record<string, number>;
}

export interface CalibrationInfo {
  task_id?: string;
  request_id: string;
  engineer: string;
  start_date: string | null;
  completion_date: string | null;
  total_time_hours: number;
  iterations: number;
  algorithm: string;
  accuracy?: number | null;
  rms_metric?: number | null;
  progress?: number;
  error_message?: string;
  timestamp?: string;
  metrics?: {
    accuracy?: number;
    [key: string]: any;
  };
}

export interface ValidationResults {
  dc_validation?: ValidationMetrics;
  cv_validation?: ValidationMetrics;
  rf_validation?: ValidationMetrics;
  overall_score: number;
}

export interface ValidationMetrics {
  rmse: number;
  max_error: number;
  r_squared: number;
  pass: boolean;
}

export interface WorkflowStep {
  id: number;
  name: string;
  status: 'pending' | 'in-progress' | 'completed';
  description?: string;
  progress?: number;
}

export interface ModelRequest {
  request_id: string;
  title: string;
  type: 'compact' | 'behavioral';
  component_type: string;
  technology: string;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'awaiting-info' | 'rejected' | 'accepted';
  requester: string;
  request_date: string;
  created_date?: string;
  due_date: string;
  description?: string;
  attachments?: string[];
  comments?: {
    text: string;
    author: string;
    date: string;
  }[];
  assigned_engineer?: string;
  info_requested?: string;
}