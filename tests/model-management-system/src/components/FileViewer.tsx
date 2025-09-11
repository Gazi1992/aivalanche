import React, { useState, useEffect } from 'react';
import { X, Download, Copy, Check, FileText, Database, Info, Code, Table, Book } from 'lucide-react';
import { ModelParameter } from '../types';
import { getModelParameters } from '../data/parametersData';

interface FileViewerProps {
  isOpen: boolean;
  onClose: () => void;
  fileType: 'cir' | 'parameters' | 'info' | 'documentation';
  fileName: string;
  modelName: string;
  modelData?: any;
  content?: any;
}

const FileViewer: React.FC<FileViewerProps> = ({ 
  isOpen, 
  onClose, 
  fileType, 
  fileName, 
  modelName,
  modelData,
  content 
}) => {
  const [copied, setCopied] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [modelParameters, setModelParameters] = useState<ModelParameter[]>([]);

  // Load parameters when modelData changes
  useEffect(() => {
    if (modelData?.model_id) {
      const params = getModelParameters(modelData.model_id);
      setModelParameters(params);
    }
  }, [modelData]);

  if (!isOpen) return null;

  // Helper function to render text with line numbers in separate columns
  const renderWithLineNumbers = (text: string) => {
    const lines = text.split('\n');
    const maxLineNumWidth = lines.length.toString().length;
    
    return (
      <div className="flex">
        {/* Line numbers column - non-selectable */}
        <div className="bg-gray-800 text-gray-400 px-3 py-6 font-mono text-sm border-r border-gray-700 select-none user-select-none">
          {lines.map((_, index) => (
            <div key={index} className="leading-6 text-right">
              {(index + 1).toString().padStart(maxLineNumWidth, ' ')}
            </div>
          ))}
        </div>
        {/* Content column */}
        <div className="flex-1 px-6 py-6 font-mono text-sm overflow-x-auto">
          {lines.map((line, index) => (
            <div key={index} className="leading-6">
              {line}
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Sample circuit file content
  const sampleCircuitContent = `* BSIM4 NMOS Model Entry Point
* Technology: 28nm
* Model Version: 4.8.1
* Date: 2025-01-11

.subckt nmos_28nm d g s b l=30n w=1u nf=1

* Include model library files
.include "libs/bsim4_core.lib"
.include "libs/bsim4_params.lib"

* Instance parameters
.param L_eff = 'L - 2*DL'
.param W_eff = 'W - 2*DW'
.param AD_eff = 'W_eff * 0.5u'
.param AS_eff = 'W_eff * 0.5u'
.param PD_eff = '2*(W_eff + 0.5u)'
.param PS_eff = '2*(W_eff + 0.5u)'

* Main transistor instance
M1 d g s b nmos_model L='L_eff' W='W_eff' AD='AD_eff' AS='AS_eff' PD='PD_eff' PS='PS_eff' NF='nf'

* Parasitic capacitances
Cgd_overlap g d 'CGDO*W_eff'
Cgs_overlap g s 'CGSO*W_eff'
Cgb_overlap g b 'CGBO*L_eff'

* Junction capacitances
Cjd d b junc_cap area='AD_eff' perim='PD_eff'
Cjs s b junc_cap area='AS_eff' perim='PS_eff'

* Temperature coefficient
.temp 27

* Model card reference
.model nmos_model nmos (
+ level = 54
+ version = 4.8.1
+ binunit = 1
+ paramchk = 1
+ mobmod = 0
+ capmod = 2
+ igcmod = 1
+ igbmod = 1
+ geomod = 1
+ diomod = 1
+ rdsmod = 0
+ rbodymod = 1
+ rgatemod = 1
+ permod = 1
+ acnqsmod = 0
+ trnqsmod = 0
)

.ends nmos_28nm

* End of file`;

  // Use actual model parameters or fall back to empty array
  const parameters = modelParameters.length > 0 ? modelParameters : [];

  // Sample documentation content (Markdown)
  const sampleDocumentation = `# BSIM4 NMOS Model Documentation

## Overview
This document provides comprehensive information about the BSIM4 NMOS model implementation for 28nm technology node.

## Model Description
The BSIM4 (Berkeley Short-channel IGFET Model 4) is an industry-standard compact model for MOSFETs. This implementation has been calibrated specifically for 28nm NMOS devices with extensive validation against silicon measurements.

## Features
- **Accurate modeling** across all regions of operation (subthreshold, linear, saturation)
- **Quantum mechanical corrections** for thin oxide effects
- **Self-heating model** for accurate power analysis
- **Noise modeling** including flicker and thermal noise
- **Non-quasi-static (NQS) effects** for high-frequency applications
- **Gate leakage modeling** with multiple components

## Usage Guidelines

### Basic Implementation
\`\`\`spice
.include "bsim4_nmos.cir"
X1 drain gate source bulk nmos_28nm L=30n W=1u NF=1
\`\`\`

### Parameter Extraction
The model parameters have been extracted using the following methodology:
1. **DC measurements** at multiple temperatures
2. **CV measurements** at various frequencies
3. **S-parameter measurements** up to 50 GHz
4. **Noise measurements** from 1 Hz to 10 GHz

### Recommended Operating Conditions
| Parameter | Min | Typical | Max | Unit |
|-----------|-----|---------|-----|------|
| VDD | 0.9 | 1.2 | 1.32 | V |
| Temperature | -40 | 27 | 125 | °C |
| Gate Length | 28 | 30 | 100 | nm |
| Gate Width | 0.1 | 1.0 | 100 | μm |

## Model Validation

### DC Characteristics
- Id-Vgs curves validated across full voltage range
- Id-Vds output characteristics verified
- Subthreshold slope: 68 mV/dec (typical)
- DIBL: 45 mV/V @ L=30nm

### AC Characteristics
- fT (transition frequency): 185 GHz @ VDD=1.2V
- fmax (maximum frequency): 220 GHz
- Gate capacitance matched within 5%

### Statistical Variations
The model includes statistical variations for Monte Carlo analysis:
- VTH variation: σ = 15 mV
- Mobility variation: σ = 5%
- Channel length variation: σ = 1 nm

## Parameter Categories

### Geometry Parameters
Parameters related to device dimensions and layout:
- **L, W**: Channel length and width
- **NF**: Number of fingers
- **AD, AS**: Drain and source areas
- **PD, PS**: Drain and source perimeters

### Threshold Voltage Parameters
- **VTH0**: Long channel threshold voltage
- **K1, K2**: Body effect coefficients
- **DVT0, DVT1, DVT2**: Short channel effects

### Mobility Parameters
- **U0**: Low-field mobility
- **UA, UB, UC**: Mobility degradation coefficients
- **VSAT**: Saturation velocity

### Capacitance Parameters
- **TOX**: Gate oxide thickness
- **CGDO, CGSO**: Overlap capacitances
- **CJ, CJSW**: Junction capacitances

## Troubleshooting

### Common Issues and Solutions

1. **Convergence Problems**
   - Reduce GMIN if necessary
   - Check for proper initial conditions
   - Verify all connections are properly made

2. **Accuracy Issues**
   - Ensure correct temperature is specified
   - Verify voltage ranges are within specifications
   - Check that device dimensions are realistic

3. **Simulation Speed**
   - Consider using simplified models for initial analysis
   - Adjust simulator tolerances appropriately
   - Use table models for very large circuits

## Examples

### Digital Inverter
\`\`\`spice
* CMOS Inverter using BSIM4 models
.include "bsim4_nmos.cir"
.include "bsim4_pmos.cir"

* NMOS
X1 out in 0 0 nmos_28nm L=30n W=500n
* PMOS  
X2 out in vdd vdd pmos_28nm L=30n W=1u

.param vdd=1.2
Vdd vdd 0 DC vdd
Vin in 0 PULSE(0 vdd 0 10p 10p 100p 200p)
\`\`\`

### Analog Amplifier
\`\`\`spice
* Simple common-source amplifier
.include "bsim4_nmos.cir"

X1 vout vg 0 0 nmos_28nm L=100n W=10u
Rd vdd vout 10k
Vdd vdd 0 DC 1.2
Vg vg 0 DC 0.6 AC 1
\`\`\`

## References
1. BSIM4.8.1 Technical Manual, UC Berkeley
2. "28nm CMOS Technology Design Guide", Internal Document
3. Cao, Y. et al., "BSIM4 Model Validation", IEEE TED, 2024
4. Model Calibration Report v1.2, Device Modeling Team

## Support
For questions or issues with this model:
- Email: modeling-support@company.com
- Documentation: /docs/bsim4_guide.pdf
- Example files: /examples/bsim4_tests/
- Bug reports: https://internal.company.com/modeling/issues

## Revision History
| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.2 | 2025-01-10 | Updated RF parameters | J. Doe |
| 1.1 | 2024-12-15 | Fixed convergence issues | J. Smith |
| 1.0 | 2024-11-01 | Initial release | J. Doe |

## License
This model is proprietary and confidential. Use is restricted to authorized personnel only.

---
*Last updated: January 11, 2025*`;

  // Sample info content
  const sampleInfoContent = {
    model_id: "MOD-BSIM4-001",
    name: "BSIM4 NMOS Model",
    version: "4.8.1",
    description: "Industry-standard BSIM4 model for 28nm NMOS transistors with extensive parameter set for accurate simulation across all regions of operation",
    technology: {
      node: "28nm",
      foundry: "Generic",
      process: "CMOS",
      variant: "Low Power"
    },
    characteristics: {
      vdd_nominal: 1.2,
      vth_nominal: 0.48,
      temperature_range: [-40, 125],
      frequency_range: [0, 50e9]
    },
    validation: {
      test_structures: 50,
      measurement_points: 15420,
      accuracy: {
        dc: 0.98,
        ac: 0.95,
        transient: 0.96
      },
      validated_by: "Device Modeling Team",
      validation_date: "2025-01-10"
    },
    usage_notes: [
      "Suitable for digital and analog circuit simulation",
      "Includes quantum mechanical corrections",
      "Self-heating effects included for accurate power analysis",
      "Validated against silicon measurements"
    ],
    references: [
      "BSIM4.8.1 Technical Manual",
      "28nm Technology Design Guide",
      "Model Validation Report v1.2"
    ],
    support: {
      contact: "modeling-support@company.com",
      documentation: "/docs/bsim4_guide.pdf",
      examples: "/examples/bsim4_tests/"
    }
  };

  const handleDownload = () => {
    let content = '';
    let filename = fileName;
    let mimeType = 'text/plain';
    
    if (fileType === 'cir') {
      content = sampleCircuitContent;
      mimeType = 'text/plain';
    } else if (fileType === 'parameters') {
      // Create CSV content
      const csvHeaders = 'name,subckt,default,min,max,unit,description\n';
      const csvContent = parameters.map(p => 
        `${p.name},${p.subckt},${p.default},${p.min || ''},${p.max || ''},${p.unit || ''},${p.description || ''}`
      ).join('\n');
      content = csvHeaders + csvContent;
      mimeType = 'text/csv';
      if (!filename.endsWith('.csv')) filename += '.csv';
    } else if (fileType === 'documentation') {
      content = sampleDocumentation;
      mimeType = 'text/markdown';
      if (!filename.endsWith('.md') && !filename.endsWith('.pdf')) filename += '.md';
    } else {
      content = JSON.stringify(sampleInfoContent, null, 2);
      mimeType = 'application/json';
      if (!filename.endsWith('.json')) filename += '.json';
    }
    
    // Create blob and download
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleCopy = () => {
    let textToCopy = '';
    if (fileType === 'cir') {
      textToCopy = sampleCircuitContent;
    } else if (fileType === 'parameters') {
      textToCopy = parameters.map(p => 
        `${p.name}\t${p.subckt}\t${p.default}\t${p.min || ''}\t${p.max || ''}\t${p.unit || ''}`
      ).join('\n');
    } else if (fileType === 'documentation') {
      textToCopy = sampleDocumentation;
    } else {
      textToCopy = JSON.stringify(sampleInfoContent, null, 2);
    }
    
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getIcon = () => {
    switch (fileType) {
      case 'cir': return <Code className="w-5 h-5" />;
      case 'parameters': return <Table className="w-5 h-5" />;
      case 'info': return <Info className="w-5 h-5" />;
      case 'documentation': return <Book className="w-5 h-5" />;
      default: return <FileText className="w-5 h-5" />;
    }
  };

  const getTitle = () => {
    switch (fileType) {
      case 'cir': return 'Circuit File Viewer';
      case 'parameters': return 'Parameters Table';
      case 'info': {
        // Determine the type of content for info files
        if (content && 'data_id' in content) {
          return 'Reference Data Information';
        } else if (content && 'testbench' in content) {
          return 'Testbench Information';
        } else {
          return 'Model Information';
        }
      }
      case 'documentation': return 'Model Documentation';
      default: return 'File Viewer';
    }
  };

  const filteredParameters = fileType === 'parameters' 
    ? parameters.filter(p => 
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.description?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : [];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              {getIcon()}
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{getTitle()}</h2>
              <p className="text-sm text-gray-500">{modelName} / {fileName}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-green-600" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Copy
                </>
              )}
            </button>
            <button 
              onClick={handleDownload}
              className="px-3 py-1.5 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Download
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto">
          {fileType === 'cir' && (
            <div className="p-0">
              <div className="bg-gray-900 text-gray-100 rounded-lg overflow-hidden">
                {renderWithLineNumbers(sampleCircuitContent)}
              </div>
            </div>
          )}

          {fileType === 'parameters' && (
            <div className="p-6">
              {/* Search bar for parameters */}
              <div className="mb-4 flex items-center gap-4">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    placeholder="Search parameters..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                  <Database className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                </div>
                <div className="text-sm text-gray-500">
                  Showing {filteredParameters.length} of {parameters.length} parameters
                </div>
              </div>

              {/* Parameters table */}
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Parameter
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Subcircuit
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Default
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Min
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Max
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Unit
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Description
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredParameters.map((param, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-mono font-medium text-gray-900">
                          {param.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {param.subckt}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {typeof param.default === 'number' && param.default < 0.001 
                            ? param.default.toExponential(2)
                            : param.default}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {param.min ? (
                            typeof param.min === 'number' && param.min < 0.001
                              ? param.min.toExponential(2)
                              : param.min
                          ) : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {param.max ? (
                            typeof param.max === 'number' && param.max < 0.001
                              ? param.max.toExponential(2)
                              : param.max
                          ) : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {param.unit || '-'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {param.description}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Statistics */}
              <div className="mt-4 grid grid-cols-4 gap-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Total Parameters</p>
                  <p className="text-lg font-semibold text-gray-900">{parameters.length}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Geometry</p>
                  <p className="text-lg font-semibold text-gray-900">7</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Electrical</p>
                  <p className="text-lg font-semibold text-gray-900">10</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Temperature</p>
                  <p className="text-lg font-semibold text-gray-900">3</p>
                </div>
              </div>
            </div>
          )}

          {fileType === 'info' && (
            <div className="p-6 space-y-6">
              {/* Determine if content is reference data or testbench */}
              {(() => {
                const isReferenceData = content && 'data_id' in content;
                const isTestbench = content && 'testbench' in content;
                const displayData = content || modelData || sampleInfoContent;
                
                return (
                  <>
                    {/* Compact info cards at the top */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      {isReferenceData ? (
                        <>
                          {/* Reference Data Compact View */}
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                            <div className="bg-white border border-gray-200 rounded p-3">
                              <p className="text-xs text-gray-500">Data Type</p>
                              <p className="text-sm font-semibold">{content.type}</p>
                            </div>
                            <div className="bg-white border border-gray-200 rounded p-3">
                              <p className="text-xs text-gray-500">Source</p>
                              <p className="text-sm font-semibold">
                                {typeof content.source === 'object' 
                                  ? content.source.simulator || JSON.stringify(content.source).slice(0, 20) + '...'
                                  : content.source}
                              </p>
                            </div>
                            <div className="bg-white border border-gray-200 rounded p-3">
                              <p className="text-xs text-gray-500">Pages</p>
                              <p className="text-sm font-semibold">{content.data?.pages?.length || 0}</p>
                            </div>
                            <div className="bg-white border border-gray-200 rounded p-3">
                              <p className="text-xs text-gray-500">Total Points</p>
                              <p className="text-sm font-semibold">
                                {content.data?.pages?.reduce((sum: number, page: any) => sum + (page.curves?.[0]?.x?.length || 0), 0) || 0}
                              </p>
                            </div>
                          </div>
                          
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                            <div className="bg-white border border-gray-200 rounded p-3">
                              <p className="text-xs text-gray-500">Device Type</p>
                              <p className="text-sm font-semibold">
                                {typeof content.device?.type === 'object' 
                                  ? JSON.stringify(content.device.type).slice(0, 20) + '...'
                                  : content.device?.type || 'N/A'}
                              </p>
                            </div>
                            <div className="bg-white border border-gray-200 rounded p-3">
                              <p className="text-xs text-gray-500">Technology</p>
                              <p className="text-sm font-semibold">
                                {typeof content.device?.technology === 'object'
                                  ? JSON.stringify(content.device.technology).slice(0, 20) + '...'
                                  : content.device?.technology || 'N/A'}
                              </p>
                            </div>
                            <div className="bg-white border border-gray-200 rounded p-3">
                              <p className="text-xs text-gray-500">Quality Score</p>
                              <p className="text-sm font-semibold">{content.quality?.score || 'N/A'}</p>
                            </div>
                            {content.device?.dimensions && (
                              <div className="bg-white border border-gray-200 rounded p-3">
                                <p className="text-xs text-gray-500">Dimensions</p>
                                <p className="text-sm font-semibold">
                                  W:{content.device.dimensions.W} L:{content.device.dimensions.L}
                                  {content.device.dimensions.NF && ` NF:${content.device.dimensions.NF}`}
                                </p>
                              </div>
                            )}
                          </div>

                          {content.tags && (
                            <div className="flex flex-wrap gap-1">
                              {content.tags.map((tag: string, idx: number) => (
                                <span key={idx} className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </>
                      ) : isTestbench ? (
                        <>
                          {/* Testbench Compact View */}
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                            <div className="bg-white border border-gray-200 rounded p-3">
                              <p className="text-xs text-gray-500">Type</p>
                              <p className="text-sm font-semibold">{content.testbench.type.replace(/_/g, ' ')}</p>
                            </div>
                            <div className="bg-white border border-gray-200 rounded p-3">
                              <p className="text-xs text-gray-500">Status</p>
                              <p className="text-sm font-semibold">{content.testbench.validated ? 'Validated' : 'Not Validated'}</p>
                            </div>
                            <div className="bg-white border border-gray-200 rounded p-3">
                              <p className="text-xs text-gray-500">Measurements</p>
                              <p className="text-sm font-semibold">{content.testbench.measurements.length}</p>
                            </div>
                            <div className="bg-white border border-gray-200 rounded p-3">
                              <p className="text-xs text-gray-500">Parameters</p>
                              <p className="text-sm font-semibold">{Object.keys(content.testbench.circuit.parameters).length}</p>
                            </div>
                          </div>

                          {content.library && (
                            <div className="grid grid-cols-3 gap-3 mb-4">
                              <div className="bg-white border border-gray-200 rounded p-3">
                                <p className="text-xs text-gray-500">Library</p>
                                <p className="text-sm font-semibold">{content.library.library_name}</p>
                              </div>
                              <div className="bg-white border border-gray-200 rounded p-3">
                                <p className="text-xs text-gray-500">Version</p>
                                <p className="text-sm font-semibold">v{content.library.version}</p>
                              </div>
                              <div className="bg-white border border-gray-200 rounded p-3">
                                <p className="text-xs text-gray-500">Organization</p>
                                <p className="text-sm font-semibold">{content.library.organization}</p>
                              </div>
                            </div>
                          )}

                          <div className="mb-4">
                            <p className="text-xs text-gray-500 mb-2">Compatible Devices</p>
                            <div className="flex flex-wrap gap-1">
                              {content.testbench.compatible_devices.map((device: string, idx: number) => (
                                <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                                  {device}
                                </span>
                              ))}
                            </div>
                          </div>

                          {content.testbench.tags && (
                            <div className="flex flex-wrap gap-1">
                              {content.testbench.tags.map((tag: string, idx: number) => (
                                <span key={idx} className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </>
                      ) : (
                        <>
                          {/* Default Model Template Compact View */}
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                            <div className="bg-white border border-gray-200 rounded p-3">
                              <p className="text-xs text-gray-500">Technology Node</p>
                              <p className="text-sm font-semibold">{modelData?.technology?.node || sampleInfoContent.technology.node}</p>
                            </div>
                            <div className="bg-white border border-gray-200 rounded p-3">
                              <p className="text-xs text-gray-500">Process</p>
                              <p className="text-sm font-semibold">{modelData?.technology?.process || sampleInfoContent.technology.process}</p>
                            </div>
                            <div className="bg-white border border-gray-200 rounded p-3">
                              <p className="text-xs text-gray-500">Nominal VDD</p>
                              <p className="text-sm font-semibold">{modelData?.characteristics?.vdd_nominal || sampleInfoContent.characteristics.vdd_nominal}V</p>
                            </div>
                            <div className="bg-white border border-gray-200 rounded p-3">
                              <p className="text-xs text-gray-500">Nominal VTH</p>
                              <p className="text-sm font-semibold">{modelData?.characteristics?.vth_nominal || sampleInfoContent.characteristics.vth_nominal}V</p>
                            </div>
                          </div>

                          <div className="mb-4">
                            <p className="text-xs text-gray-500 mb-2">Temperature Range</p>
                            <p className="text-sm font-semibold">
                              {modelData?.characteristics?.temperature_range?.[0] || sampleInfoContent.characteristics.temperature_range[0]}°C to {modelData?.characteristics?.temperature_range?.[1] || sampleInfoContent.characteristics.temperature_range[1]}°C
                            </p>
                          </div>

                          <div className="mb-4">
                            <p className="text-xs text-gray-500 mb-2">Usage Notes</p>
                            <ul className="space-y-1">
                              {(modelData?.usage_notes || sampleInfoContent.usage_notes).slice(0, 2).map((note: string, idx: number) => (
                                <li key={idx} className="flex items-start gap-1">
                                  <span className="text-purple-600 text-xs mt-0.5">•</span>
                                  <span className="text-xs text-gray-700">{note}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                          
                          {modelData?.tags && (
                            <div className="flex flex-wrap gap-1">
                              {modelData.tags.map((tag: string, idx: number) => (
                                <span key={idx} className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </>
                      )}
                    </div>

                    {/* Raw JSON Data */}
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700 mb-2">Raw Data</h3>
                      <div className="bg-gray-50 rounded-lg overflow-hidden">
                        <div className="flex">
                          {/* Line numbers column for JSON */}
                          <div className="bg-gray-200 text-gray-600 px-3 py-4 font-mono text-xs border-r border-gray-300 select-none user-select-none">
                            {JSON.stringify(displayData, null, 2).split('\n').map((_, index) => (
                              <div key={index} className="leading-5 text-right">
                                {(index + 1).toString().padStart(JSON.stringify(displayData, null, 2).split('\n').length.toString().length, ' ')}
                              </div>
                            ))}
                          </div>
                          {/* JSON content */}
                          <div className="flex-1 px-4 py-4 font-mono text-xs text-gray-700 overflow-x-auto">
                            <pre>{JSON.stringify(displayData, null, 2)}</pre>
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                );
              })()}
            </div>
          )}

          {fileType === 'documentation' && (
            <div className="p-6">
              <div className="prose prose-sm max-w-none">
                <div className="bg-white rounded-lg">
                  {/* Render markdown as formatted HTML-like structure */}
                  <div className="space-y-6">
                    {sampleDocumentation.split('\n\n').map((section, idx) => {
                      // Handle headers
                      if (section.startsWith('# ')) {
                        return <h1 key={idx} className="text-2xl font-bold text-gray-900 mb-4">{section.replace('# ', '')}</h1>;
                      } else if (section.startsWith('## ')) {
                        return <h2 key={idx} className="text-xl font-semibold text-gray-900 mt-6 mb-3">{section.replace('## ', '')}</h2>;
                      } else if (section.startsWith('### ')) {
                        return <h3 key={idx} className="text-lg font-semibold text-gray-800 mt-4 mb-2">{section.replace('### ', '')}</h3>;
                      }
                      // Handle code blocks
                      else if (section.includes('```')) {
                        const code = section.replace(/```\w*\n?/g, '').trim();
                        return (
                          <div key={idx} className="bg-gray-900 text-gray-100 rounded-lg overflow-hidden">
                            <div className="flex">
                              {/* Line numbers for code blocks */}
                              <div className="bg-gray-800 text-gray-400 px-3 py-4 font-mono text-sm border-r border-gray-700 select-none user-select-none">
                                {code.split('\n').map((_, codeIdx) => (
                                  <div key={codeIdx} className="leading-6 text-right">
                                    {(codeIdx + 1).toString().padStart(code.split('\n').length.toString().length, ' ')}
                                  </div>
                                ))}
                              </div>
                              <div className="flex-1 px-4 py-4 font-mono text-sm overflow-x-auto">
                                <pre>{code}</pre>
                              </div>
                            </div>
                          </div>
                        );
                      }
                      // Handle tables
                      else if (section.includes('|') && section.includes('---')) {
                        const lines = section.split('\n').filter(line => line.trim());
                        const headers = lines[0].split('|').filter(h => h.trim()).map(h => h.trim());
                        const rows = lines.slice(2).map(line => 
                          line.split('|').filter(cell => cell.trim()).map(cell => cell.trim())
                        );
                        return (
                          <div key={idx} className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                              <thead className="bg-gray-50">
                                <tr>
                                  {headers.map((header, hIdx) => (
                                    <th key={hIdx} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                      {header}
                                    </th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody className="bg-white divide-y divide-gray-200">
                                {rows.map((row, rIdx) => (
                                  <tr key={rIdx}>
                                    {row.map((cell, cIdx) => (
                                      <td key={cIdx} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        {cell}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        );
                      }
                      // Handle numbered lists
                      else if (/^\d+\./.test(section)) {
                        const items = section.split('\n').filter(item => item.trim());
                        return (
                          <ol key={idx} className="list-decimal list-inside space-y-2">
                            {items.map((item, iIdx) => (
                              <li key={iIdx} className="text-sm text-gray-700">
                                {item.replace(/^\d+\.\s*/, '')}
                              </li>
                            ))}
                          </ol>
                        );
                      }
                      // Handle bullet lists
                      else if (section.startsWith('- ') || section.startsWith('* ')) {
                        const items = section.split('\n').filter(item => item.trim());
                        return (
                          <ul key={idx} className="list-disc list-inside space-y-2">
                            {items.map((item, iIdx) => (
                              <li key={iIdx} className="text-sm text-gray-700">
                                {item.replace(/^[-*]\s*/, '')}
                              </li>
                            ))}
                          </ul>
                        );
                      }
                      // Handle regular paragraphs
                      else if (section.trim()) {
                        return <p key={idx} className="text-sm text-gray-700 leading-relaxed">{section}</p>;
                      }
                      return null;
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FileViewer;