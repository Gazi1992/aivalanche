import React from 'react';
import { X, Info, FileText, Database, FolderOpen, CheckCircle, AlertCircle } from 'lucide-react';

interface DataStructureGuideProps {
  isOpen: boolean;
  onClose: () => void;
  type: 'model' | 'reference' | 'testbench';
}

const DataStructureGuide: React.FC<DataStructureGuideProps> = ({ isOpen, onClose, type }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Info className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {type === 'model' ? 'Model Template Structure Guide' : 
                 type === 'reference' ? 'Reference Data Structure Guide' :
                 'Testbench Library Structure Guide'}
              </h2>
              <p className="text-sm text-gray-500">
                Learn how to create and structure {type === 'model' ? 'model templates' : 
                                                   type === 'reference' ? 'reference data files' :
                                                   'testbench libraries'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 p-1"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {type === 'model' ? (
            <div className="space-y-6">
              {/* Model Template Overview */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Model Template Structure</h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-4">
                    Each model template is organized in a specific folder structure with required and optional files:
                  </p>
                  <div className="space-y-2 font-mono text-sm">
                    <div className="flex items-center gap-2">
                      <FolderOpen className="w-4 h-4 text-yellow-600" />
                      <span className="font-semibold">model_id/</span>
                      <span className="text-gray-500">(e.g., nmos_45nm_v2)</span>
                    </div>
                    <div className="ml-6 space-y-2">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-blue-500" />
                        <span>model.cir</span>
                        <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">Required</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Database className="w-4 h-4 text-green-500" />
                        <span>parameters.csv</span>
                        <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">Required</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-yellow-500" />
                        <span>metadata.json</span>
                        <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">Required</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-indigo-500" />
                        <span>documentation.md</span>
                        <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded">Optional</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <FolderOpen className="w-4 h-4 text-yellow-600" />
                        <span>libs/</span>
                        <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded">Optional</span>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              {/* File Descriptions */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">File Descriptions</h3>
                <div className="space-y-4">
                  <div className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <FileText className="w-5 h-5 text-blue-500 mt-0.5" />
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">model.cir (Circuit File)</h4>
                        <p className="text-sm text-gray-600 mt-1">
                          Main SPICE model file containing subcircuit definitions and model equations.
                        </p>
                        <div className="mt-2 bg-gray-100 rounded p-3 font-mono text-xs">
                          <div className="text-gray-700">
                            .subckt nmos_45nm d g s b<br/>
                            * Model parameters and equations<br/>
                            .param vth0=0.5<br/>
                            * Device structure<br/>
                            M1 d g s b nmos W=1u L=45n<br/>
                            .ends
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <Database className="w-5 h-5 text-green-500 mt-0.5" />
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">parameters.csv</h4>
                        <p className="text-sm text-gray-600 mt-1">
                          CSV file defining all model parameters with their properties.
                        </p>
                        <div className="mt-2 bg-gray-100 rounded p-3">
                          <table className="text-xs w-full">
                            <thead className="text-left border-b border-gray-300">
                              <tr>
                                <th className="pb-1">name</th>
                                <th className="pb-1">subckt</th>
                                <th className="pb-1">default</th>
                                <th className="pb-1">min</th>
                                <th className="pb-1">max</th>
                                <th className="pb-1">unit</th>
                                <th className="pb-1">description</th>
                              </tr>
                            </thead>
                            <tbody className="font-mono">
                              <tr>
                                <td>VTH0</td>
                                <td>nmos</td>
                                <td>0.5</td>
                                <td>0.3</td>
                                <td>0.7</td>
                                <td>V</td>
                                <td>Threshold voltage</td>
                              </tr>
                              <tr>
                                <td>U0</td>
                                <td>nmos</td>
                                <td>450</td>
                                <td>200</td>
                                <td>600</td>
                                <td>cm²/Vs</td>
                                <td>Mobility</td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <FileText className="w-5 h-5 text-yellow-500 mt-0.5" />
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">metadata.json</h4>
                        <p className="text-sm text-gray-600 mt-1">
                          JSON file containing model metadata, versioning, and configuration.
                        </p>
                        <div className="mt-2 bg-gray-100 rounded p-3 font-mono text-xs">
                          <div className="text-gray-700">
                            {`{
  "name": "NMOS 45nm",
  "version": "2.1.0",
  "date": "2024-03-15",
  "author": "Engineering Team",
  "description": "Production-ready 45nm NMOS model",
  "base_model": "BSIM4",
  "status": "validated",
  "category": "MOSFET",
  "subcategory": "NMOS",
  "tags": ["45nm", "nmos", "digital", "analog"]
}`}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              {/* Best Practices */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Best Practices</h3>
                <div className="space-y-2">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <p className="text-sm text-gray-600">Use consistent naming conventions for model IDs and files</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <p className="text-sm text-gray-600">Include comprehensive parameter descriptions in the CSV</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <p className="text-sm text-gray-600">Document all subcircuits and their terminals</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <p className="text-sm text-gray-600">Version control your models and maintain change logs</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5" />
                    <p className="text-sm text-gray-600">Always validate models against reference data before marking as production</p>
                  </div>
                </div>
              </section>
            </div>
          ) : type === 'reference' ? (
            <div className="space-y-6">
              {/* Reference Data Overview */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Reference Data JSON Structure</h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-4">
                    Reference data files are JSON documents with a specific schema containing metadata and measurement/simulation data:
                  </p>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-semibold">data_id</span>
                      <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">Required</span>
                      <span className="text-sm text-gray-500">Unique identifier (e.g., "REF-MEAS-001")</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-semibold">name</span>
                      <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">Required</span>
                      <span className="text-sm text-gray-500">Descriptive name of the dataset</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-semibold">data</span>
                      <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">Required</span>
                      <span className="text-sm text-gray-500">Array of data pages with measurements</span>
                    </div>
                  </div>
                </div>
              </section>

              {/* JSON Schema */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Complete JSON Schema</h3>
                <div className="bg-gray-100 rounded-lg p-4 overflow-x-auto">
                  <pre className="text-xs font-mono text-gray-700">
{`{
  // Required Fields
  "data_id": "REF-MEAS-001",           // Unique identifier
  "name": "Dataset Name",              // Display name
  "version": "1.0",                    // Version string
  "data_type": "measurement",          // "measurement" or "simulation"
  "description": "...",                // Detailed description
  
  // Device Information (Required)
  "device_info": {
    "device_type": "mosfet",          // Device category
    "transistor_type": "nmos",        // Specific type
    "technology_node": "45nm",        // Technology node
    "foundry": "Generic",              // Foundry name
    "process_variant": "LP"           // Optional: Process variant
  },
  
  // Measurement/Simulation Info (Required)
  "measurement_info": {                // or "simulation_info"
    "equipment": "Keysight B1500A",   // Equipment/simulator used
    "operator": "John Doe",           // Person responsible
    "measurement_date": "2024-03-15", // ISO date
    "lab_conditions": {...}           // Optional: Environmental data
  },
  
  // Data Quality (Required)
  "data_quality": {
    "validated": true,                 // Validation status
    "completeness": 0.95,             // Data completeness (0-1)
    "quality_score": 0.92,            // Quality metric (0-1)
    "measurement_points": 1000,       // Number of data points
    "validation_notes": "..."         // Optional notes
  },
  
  // Author Information (Required)
  "author": {
    "name": "Dr. Jane Smith",
    "email": "jane.smith@company.com",
    "department": "Device Characterization"
  },
  
  // Timestamps (Required)
  "timestamps": {
    "created": "2024-03-15T10:00:00Z",
    "modified": "2024-03-20T15:30:00Z"
  },
  
  // Tags (Optional but recommended)
  "tags": ["45nm", "nmos", "dc", "validated"],
  
  // Data Pages (Required - at least one)
  "data": [
    {
      "type": "ids_vgs",               // Measurement type
      "name": "Transfer Characteristics",
      "page": "transfer_lin",          // Unique page ID
      "testbench_type": "dc_sweep",
      "x_name": "vgs",                 // X-axis variable
      "y_name": "ids",                 // Y-axis variable
      "extra_var_name": "vds",         // Optional: sweep variable
      "x_unit": "V",
      "y_unit": "A",
      "extra_var_unit": "V",
      "operating_conditions": {
        "temperature": 25,
        "vbs": 0
      },
      "instance_parameters": {
        "w": 10e-6,
        "l": 45e-9,
        "nf": 1
      },
      "curves": [
        {
          "x_values": [0, 0.1, 0.2, ...],
          "y_values": [1e-12, 1e-11, ...],
          "extra_var_value": 0.05
        }
      ]
    }
  ]
}`}
                  </pre>
                </div>
              </section>

              {/* Data Page Structure */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Data Page Structure</h3>
                <div className="space-y-4">
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">Page Fields</h4>
                    <div className="space-y-2 text-sm">
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <span className="font-mono font-semibold">page</span>
                          <p className="text-gray-600 text-xs">Unique page identifier</p>
                        </div>
                        <div>
                          <span className="font-mono font-semibold">name</span>
                          <p className="text-gray-600 text-xs">Display name for the page</p>
                        </div>
                        <div>
                          <span className="font-mono font-semibold">type</span>
                          <p className="text-gray-600 text-xs">Measurement type</p>
                        </div>
                      </div>
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <span className="font-mono font-semibold">x_name, y_name</span>
                          <p className="text-gray-600 text-xs">Axis variable names</p>
                        </div>
                        <div>
                          <span className="font-mono font-semibold">x_unit, y_unit</span>
                          <p className="text-gray-600 text-xs">Units for axis values</p>
                        </div>
                        <div>
                          <span className="font-mono font-semibold">curves</span>
                          <p className="text-gray-600 text-xs">Array of data curves</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">Curve Data</h4>
                    <p className="text-sm text-gray-600 mb-2">
                      Each curve contains x and y value arrays, plus optional sweep parameter:
                    </p>
                    <div className="bg-gray-100 rounded p-3 font-mono text-xs">
                      <div className="text-gray-700">
                        {`"curves": [
  {
    "x_values": [0, 0.1, 0.2, 0.3, ...],
    "y_values": [1e-12, 1e-11, 1e-10, ...],
    "extra_var_value": 0.05  // Optional
  }
]`}
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              {/* Validation Rules */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Validation Rules</h3>
                <div className="space-y-2">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <p className="text-sm text-gray-600">All x_values and y_values arrays must have the same length</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <p className="text-sm text-gray-600">data_id must be unique across all reference data files</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <p className="text-sm text-gray-600">Page IDs must be unique within each data file</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <p className="text-sm text-gray-600">Quality score should be between 0 and 1</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5" />
                    <p className="text-sm text-gray-600">Use ISO 8601 format for all timestamps</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5" />
                    <p className="text-sm text-gray-600">Numerical data should use scientific notation where appropriate</p>
                  </div>
                </div>
              </section>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Testbench Library Overview */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Testbench Library Structure</h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-4">
                    Testbench libraries are JSON files containing collections of related testbenches for device characterization:
                  </p>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-semibold">library_name</span>
                      <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">Required</span>
                      <span className="text-sm text-gray-500">Name of the testbench library</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-semibold">testbenches</span>
                      <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">Required</span>
                      <span className="text-sm text-gray-500">Array of testbench definitions</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-semibold">version</span>
                      <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">Required</span>
                      <span className="text-sm text-gray-500">Library version number</span>
                    </div>
                  </div>
                </div>
              </section>

              {/* Testbench Schema */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Testbench Definition Schema</h3>
                <div className="bg-gray-100 rounded-lg p-4 overflow-x-auto">
                  <pre className="text-xs font-mono text-gray-700">
{`{
  "testbench_id": "dc_id_vd",           // Unique testbench identifier
  "name": "DC Output Characteristics",  // Display name
  "type": "dc_sweep",                   // Analysis type
  "description": "...",                 // Detailed description
  "validated": true,                    // Validation status
  "tags": ["mosfet", "dc", "id-vd"],   // Search tags
  "schematic": "schematics/dc.png",    // Circuit diagram path
  
  // Circuit Definition (Required)
  "circuit": {
    "netlist": [                       // SPICE netlist lines
      "VDS drain 0 DC {{vds}}",
      "VGS gate 0 DC {{vgs}}",
      "XDUT drain gate source bulk {{model_subckt}} W={{w}} L={{l}}"
    ],
    "parameters": {                    // Testbench parameters
      "vds": {
        "default": 0,
        "unit": "V",
        "description": "Drain-source voltage"
      },
      "vgs": {
        "default": 0.6,
        "unit": "V",
        "description": "Gate-source voltage"
      }
    }
  },
  
  // Measurements (Required)
  "measurements": [                    // SPICE .measure statements
    ".measure dc id_max MAX I(VDS)",
    ".measure dc vth FIND V(gate) WHEN I(VDS)=1e-7"
  ],
  
  // Output Parameters (Required)
  "outputs": {
    "id_max": {
      "unit": "A",
      "description": "Maximum drain current"
    },
    "vth": {
      "unit": "V",
      "description": "Threshold voltage"
    }
  },
  
  // Compatible Devices (Required)
  "compatible_devices": ["nmos", "pmos"],
  
  // Examples (Optional but recommended)
  "examples": [
    {
      "name": "Basic Id-Vd sweep",
      "description": "Simple output characteristic",
      "netlist": [                    // Complete SPICE netlist
        "* Id-Vd Example",
        ".include 'model.lib'",
        "VDS drain 0 DC 0",
        "VGS gate 0 DC 0.6",
        "XDUT drain gate source bulk nmos W=10u L=45n",
        ".dc VDS 0 1.8 0.01 VGS 0.3 1.5 0.3",
        ".probe dc I(VDS)",
        ".end"
      ]
    }
  ]
}`}
                  </pre>
                </div>
              </section>

              {/* Circuit Parameters */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Circuit and Parameters</h3>
                <div className="space-y-4">
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">Netlist Template</h4>
                    <p className="text-sm text-gray-600 mb-2">
                      The netlist array contains circuit connectivity with parameter placeholders:
                    </p>
                    <ul className="space-y-1 text-sm text-gray-600 list-disc list-inside">
                      <li>Use {`{{parameter}}`} syntax for runtime substitution</li>
                      <li>XDUT is the standard name for Device Under Test</li>
                      <li>Include only circuit connectivity, not simulator commands</li>
                      <li>Parameters can be device dimensions, voltages, or other values</li>
                    </ul>
                  </div>

                  <div className="border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">Measurements and Outputs</h4>
                    <p className="text-sm text-gray-600 mb-2">
                      Define measurements and expected output parameters:
                    </p>
                    <ul className="space-y-1 text-sm text-gray-600 list-disc list-inside">
                      <li>Measurements use standard SPICE .measure syntax</li>
                      <li>Each output must have a corresponding measurement</li>
                      <li>Include units and descriptions for all outputs</li>
                      <li>Output names should match measurement names</li>
                    </ul>
                  </div>
                </div>
              </section>

              {/* Testbench Types */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Common Testbench Types</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="border border-gray-200 rounded-lg p-3">
                    <h4 className="font-mono text-sm font-semibold text-gray-900 mb-1">dc_sweep</h4>
                    <p className="text-xs text-gray-600">DC characterization (Id-Vd, Id-Vg)</p>
                  </div>
                  <div className="border border-gray-200 rounded-lg p-3">
                    <h4 className="font-mono text-sm font-semibold text-gray-900 mb-1">ac_analysis</h4>
                    <p className="text-xs text-gray-600">Small signal and capacitance</p>
                  </div>
                  <div className="border border-gray-200 rounded-lg p-3">
                    <h4 className="font-mono text-sm font-semibold text-gray-900 mb-1">transient</h4>
                    <p className="text-xs text-gray-600">Switching and timing analysis</p>
                  </div>
                  <div className="border border-gray-200 rounded-lg p-3">
                    <h4 className="font-mono text-sm font-semibold text-gray-900 mb-1">noise</h4>
                    <p className="text-xs text-gray-600">Noise figure and parameters</p>
                  </div>
                  <div className="border border-gray-200 rounded-lg p-3">
                    <h4 className="font-mono text-sm font-semibold text-gray-900 mb-1">sp_analysis</h4>
                    <p className="text-xs text-gray-600">S-parameter extraction</p>
                  </div>
                  <div className="border border-gray-200 rounded-lg p-3">
                    <h4 className="font-mono text-sm font-semibold text-gray-900 mb-1">hb_analysis</h4>
                    <p className="text-xs text-gray-600">Harmonic balance and distortion</p>
                  </div>
                </div>
              </section>

              {/* Best Practices */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Best Practices</h3>
                <div className="space-y-2">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <p className="text-sm text-gray-600">Group related testbenches in the same library file</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <p className="text-sm text-gray-600">Provide at least one complete example for each testbench</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <p className="text-sm text-gray-600">Include schematic images for visual reference</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <p className="text-sm text-gray-600">Use descriptive testbench_id values</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5" />
                    <p className="text-sm text-gray-600">Validate testbenches with actual device models before marking as validated</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5" />
                    <p className="text-sm text-gray-600">Ensure output names match measurement variable names</p>
                  </div>
                </div>
              </section>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500">
              {type === 'model' 
                ? 'Follow these guidelines to ensure compatibility with the model management system'
                : type === 'reference' 
                ? 'Ensure your JSON files follow this schema for proper visualization and analysis'
                : 'Use this structure to create reusable testbench libraries for device characterization'}
            </p>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              Close Guide
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataStructureGuide;