import { Model, ReferenceData, TestbenchLibrary, CalibratedModel, ModelRequest } from '../types';

// Import model metadata files
import bsim4Metadata from '../data/model-templates/bsim4-nmos/metadata.json';
import pspMetadata from '../data/model-templates/psp-pmos/metadata.json';
import schottkyMetadata from '../data/model-templates/schottky-diode/metadata.json';
import bsimcmgMetadata from '../data/model-templates/bsimcmg-finfet/metadata.json';
import ekvMetadata from '../data/model-templates/ekv-nmos/metadata.json';
import hemtMetadata from '../data/model-templates/hemt-gaas/metadata.json';
import bjtMetadata from '../data/model-templates/verilog-a-bjt/metadata.json';
import bsim3PmosMetadata from '../data/model-templates/bsim3-pmos/metadata.json';
import mismatchMetadata from '../data/model-templates/mismatch-nmos/metadata.json';
import pspNmosMetadata from '../data/model-templates/psp-nmos/metadata.json';
import resistorMetadata from '../data/model-templates/verilog-a-resistor/metadata.json';
import bsim4PmosMetadata from '../data/model-templates/bsim4-pmos/metadata.json';
import ldmosMetadata from '../data/model-templates/hv-ldmos/metadata.json';
import soiMetadata from '../data/model-templates/soi-nmos/metadata.json';
import tfetMetadata from '../data/model-templates/tunnel-fet/metadata.json';

// Import reference data files
import nmosOutputTransfer from '../data/reference-data/nmos_28nm_output_transfer.json';
import pmosCapacitance from '../data/reference-data/pmos_45nm_capacitance.json';
import finFETTcad from '../data/reference-data/finfet_14nm_tcad.json';
import bjtTemperature from '../data/reference-data/bjt_sige_temperature.json';

// Import testbench library files
import mosfetTestbenches from '../data/testbenches/mosfet_testbenches.json';
import rfAnalogTestbenches from '../data/testbenches/rf_analog_testbenches.json';

// Import calibrated model metadata files
import calNmos28nmMetadata from '../data/calibrated-models/CAL-NMOS-28NM-001/metadata.json';
import calPmos40nmMetadata from '../data/calibrated-models/CAL-PMOS-40NM-001/metadata.json';
import calFinfet14nmMetadata from '../data/calibrated-models/CAL-FINFET-14NM-001/metadata.json';
import calNmos65nmMetadata from '../data/calibrated-models/CAL-NMOS-65NM-001/metadata.json';
import calPmos28nmMetadata from '../data/calibrated-models/CAL-PMOS-28NM-001/metadata.json';

class DataService {
  // Model Templates - Load from actual info.json files
  getModelTemplates(): Model[] {
    const models: Model[] = [
      {
        ...(bsim4Metadata as any),
        files: {
          entry_point: "bsim4_nmos.cir",
          simulation_files: ["bsim4_nmos.cir", "bsim4_core.lib", "bsim4_params.lib"],
          parameters_file: "parameters.csv",
          metadata_file: "metadata.json",
          documentation: "bsim4_documentation.md",
          lib_directory: "libs",
          image: "bsim4_circuit.png"
        },
        parameters: {
          count: 450,
          file_path: "parameters.csv",
          categories: {
            geometry: ["W", "L", "NF", "AD", "AS", "PD", "PS"],
            threshold: ["VTH0", "K1", "K2", "K3", "K3B", "W0", "NLX"],
            mobility: ["U0", "UA", "UB", "UC", "VSAT", "A0", "AGS"]
          }
        }
      } as Model,
      {
        ...(pspMetadata as any),
        files: {
          entry_point: "psp_pmos.cir",
          simulation_files: ["psp_pmos.cir", "psp103_core.lib", "psp_juncap.lib"],
          parameters_file: "parameters.csv",
          metadata_file: "metadata.json",
          documentation: "psp_documentation.pdf",
          lib_directory: "libs"
        },
        parameters: {
          count: 380,
          file_path: "parameters.csv",
          categories: {
            geometry: ["W", "L", "MULT"],
            electrical: ["VFB", "PHIB", "K1", "K2"],
            mobility: ["MUE", "THEMU", "MU0"]
          }
        }
      } as Model,
      {
        ...(schottkyMetadata as any),
        files: {
          entry_point: "schottky_diode.cir",
          simulation_files: ["schottky_diode.cir", "diode_core.lib"],
          parameters_file: "parameters.csv",
          metadata_file: "metadata.json",
          documentation: "schottky_diode_manual.md"
        },
        parameters: {
          count: 25,
          file_path: "parameters.csv"
        }
      } as Model,
      {
        ...(bsimcmgMetadata as any),
        files: {
          entry_point: "bsimcmg_finfet.cir",
          simulation_files: ["bsimcmg_finfet.cir", "bsimcmg_core.lib", "quantum_correction.lib"],
          parameters_file: "parameters.csv",
          metadata_file: "metadata.json",
          documentation: "bsimcmg_technical_manual.pdf",
          lib_directory: "libs",
          image: "finfet_structure.png"
        },
        parameters: {
          count: 520,
          file_path: "parameters.csv",
          categories: {
            geometry: ["TFIN", "L", "NFIN", "FPITCH"],
            electrical: ["PHIG", "VTH0", "K1", "K2"],
            quantum: ["QM0", "ETAQM", "QMFACTOR"]
          }
        }
      } as Model,
      {
        ...(ekvMetadata as any),
        files: {
          entry_point: "ekv26_nmos.cir",
          simulation_files: ["ekv26_nmos.cir", "ekv_core.lib"],
          parameters_file: "parameters.csv",
          metadata_file: "metadata.json",
          documentation: "ekv_model_guide.md"
        },
        parameters: {
          count: 44,
          file_path: "parameters.csv",
          categories: {
            basic: ["VTO", "KP", "GAMMA", "PHI"],
            mobility: ["THETA", "ETA"],
            temperature: ["TCV", "BEX"]
          }
        }
      } as Model,
      {
        ...(hemtMetadata as any),
        files: {
          entry_point: "hemt_gaas.cir",
          simulation_files: ["hemt_gaas.cir", "hemt_core.lib", "noise_model.lib"],
          parameters_file: "parameters.csv",
          metadata_file: "metadata.json",
          documentation: "hemt_rf_guide.pdf",
          lib_directory: "libs"
        },
        parameters: {
          count: 65,
          file_path: "parameters.csv",
          categories: {
            dc: ["VTO", "BETA", "LAMBDA"],
            rf: ["TAU", "RG", "RD", "RS"],
            noise: ["KF", "AF", "FFE"]
          }
        }
      } as Model,
      {
        ...(bjtMetadata as any),
        files: {
          entry_point: "bjt_model.va",
          simulation_files: ["bjt_model.va"],
          parameters_file: "parameters.csv",
          metadata_file: "metadata.json",
          documentation: "verilog_a_bjt_guide.pdf"
        },
        parameters: {
          count: 85,
          file_path: "parameters.csv",
          categories: {
            dc: ["IS", "BF", "BR", "VAF", "VAR"],
            ac: ["TF", "TR", "CJE", "CJC"],
            temperature: ["XTI", "EG", "XTB"]
          }
        }
      } as Model,
      {
        ...(bsim3PmosMetadata as any),
        files: {
          entry_point: "bsim3_pmos.cir",
          simulation_files: ["bsim3_pmos.cir", "bsim3_core.lib"],
          parameters_file: "parameters.csv",
          metadata_file: "metadata.json",
          documentation: "bsim3_legacy_guide.pdf",
          lib_directory: "libs"
        },
        parameters: {
          count: 195,
          file_path: "parameters.csv",
          categories: {
            basic: ["VTH0", "U0", "TNOM"],
            mobility: ["UA", "UB", "UC"],
            geometry: ["DWC", "DLC", "WOC"]
          }
        }
      } as Model,
      {
        ...(mismatchMetadata as any),
        files: {
          entry_point: "mismatch_nmos.cir",
          simulation_files: ["mismatch_nmos.cir", "bsim4_core.lib", "statistical.lib"],
          parameters_file: "parameters.csv",
          metadata_file: "metadata.json",
          documentation: "statistical_modeling_guide.pdf",
          lib_directory: "libs"
        },
        parameters: {
          count: 480,
          file_path: "parameters.csv",
          categories: {
            nominal: ["VTH0", "U0", "VSAT"],
            mismatch: ["AVTO", "AU0", "AS"],
            correlation: ["SCREF", "SC"]
          }
        }
      } as Model,
      {
        ...(pspNmosMetadata as any),
        files: {
          entry_point: "psp_nmos.cir",
          simulation_files: ["psp_nmos.cir", "psp103_core.lib", "psp_juncap.lib"],
          parameters_file: "parameters.csv",
          metadata_file: "metadata.json",
          documentation: "psp_nmos_manual.pdf",
          lib_directory: "libs"
        },
        parameters: {
          count: 375,
          file_path: "parameters.csv",
          categories: {
            surface: ["VFB", "PHIB", "K1"],
            mobility: ["MUE", "THEMU", "THESATB"],
            geometry: ["DWC", "DLC", "CF"]
          }
        }
      } as Model,
      {
        ...(resistorMetadata as any),
        files: {
          entry_point: "precision_resistor.va",
          simulation_files: ["precision_resistor.va"],
          parameters_file: "parameters.csv",
          metadata_file: "metadata.json",
          documentation: "precision_resistor_guide.pdf"
        },
        parameters: {
          count: 12,
          file_path: "parameters.csv",
          categories: {
            basic: ["R", "TC1", "TC2"],
            noise: ["KF", "AF"],
            voltage: ["VC1", "VC2"]
          }
        }
      } as Model,
      {
        ...(bsim4PmosMetadata as any),
        files: {
          entry_point: "bsim4_pmos.cir",
          simulation_files: ["bsim4_pmos.cir", "bsim4_core.lib", "bsim4_params.lib"],
          parameters_file: "parameters.csv",
          metadata_file: "metadata.json",
          documentation: "bsim4_pmos_guide.pdf",
          lib_directory: "libs",
          image: "pmos_structure.png"
        },
        parameters: {
          count: 445,
          file_path: "parameters.csv",
          categories: {
            geometry: ["W", "L", "NF", "AD", "AS", "PD", "PS"],
            threshold: ["VTH0", "K1", "K2", "K3", "K3B"],
            mobility: ["U0", "UA", "UB", "UC", "VSAT"]
          }
        }
      } as Model,
      {
        ...(ldmosMetadata as any),
        files: {
          entry_point: "ldmos_hv.cir",
          simulation_files: ["ldmos_hv.cir", "ldmos_core.lib", "thermal.lib"],
          parameters_file: "parameters.csv",
          metadata_file: "metadata.json",
          documentation: "ldmos_design_guide.pdf",
          lib_directory: "libs",
          image: "ldmos_cross_section.png"
        },
        parameters: {
          count: 125,
          file_path: "parameters.csv",
          categories: {
            dc: ["VTO", "KP", "THETA"],
            breakdown: ["VBD", "NBD", "ISB"],
            thermal: ["RTH", "CTH"]
          }
        }
      } as Model,
      {
        ...(soiMetadata as any),
        files: {
          entry_point: "soi_nmos.cir",
          simulation_files: ["soi_nmos.cir", "bsimsoi_core.lib", "body_bias.lib"],
          parameters_file: "parameters.csv",
          metadata_file: "metadata.json",
          documentation: "soi_modeling_guide.pdf",
          lib_directory: "libs"
        },
        parameters: {
          count: 285,
          file_path: "parameters.csv",
          categories: {
            front_gate: ["VTH0", "K1", "K2"],
            back_gate: ["K1B", "K2B", "VBX"],
            floating_body: ["AGBCP", "AEBCP"]
          }
        }
      } as Model,
      {
        ...(tfetMetadata as any),
        files: {
          entry_point: "tfet_model.va",
          simulation_files: ["tfet_model.va"],
          parameters_file: "parameters.csv",
          metadata_file: "metadata.json",
          documentation: "tfet_preliminary_guide.pdf"
        },
        parameters: {
          count: 32,
          file_path: "parameters.csv",
          categories: {
            tunneling: ["VTT", "LAMBDA_TFET", "PHIT"],
            ambipolar: ["AMBI", "VTT_AMB"],
            temperature: ["TT0", "TT1"]
          }
        }
      } as Model
    ];

    return models;
  }

  // Reference Data
  getReferenceData(): ReferenceData[] {
    // Map the JSON data to match the ReferenceData interface
    const mapReferenceData = (data: any): ReferenceData => {
      return {
        data_id: data.data_id,
        name: data.name,
        type: data.data_type || data.type || 'measurement',
        source: {
          equipment: data.measurement_info?.equipment,
          location: data.measurement_info?.location || data.measurement_info?.lab_conditions,
          operator: data.measurement_info?.operator,
          simulator: data.simulation_info?.software
        },
        device: {
          type: data.device_info?.device_type || data.device_info?.transistor_type || 'unknown',
          technology: data.device_info?.technology_node || data.device_info?.technology || 'unknown',
          dimensions: {
            w: data.instance_parameters?.w,
            l: data.instance_parameters?.l,
            nf: data.instance_parameters?.nf
          }
        },
        measurement_conditions: data.measurement_conditions || data.operating_conditions || {
          temperature: [25],
          temperature_unit: 'C'
        },
        data_format: data.data_format || {
          file_type: 'json',
          structure: 'hierarchical',
          data_files: data.data?.map((d: any) => d.name) || []
        },
        data_quality: data.data_quality || {
          validated: data.data_quality?.validated || false,
          quality_score: data.data_quality?.quality_score || 0,
          completeness: data.data_quality?.completeness,
          noise_level: data.data_quality?.validation_notes
        },
        timestamps: data.timestamps || {
          created: data.timestamps?.created || new Date().toISOString(),
          modified: data.timestamps?.modified || new Date().toISOString()
        },
        // Include the actual data pages
        data: data.data
      } as ReferenceData;
    };

    return [
      mapReferenceData(nmosOutputTransfer),
      mapReferenceData(pmosCapacitance),
      mapReferenceData(finFETTcad),
      mapReferenceData(bjtTemperature)
    ];
  }

  // Testbenches
  getTestbenchLibraries(): TestbenchLibrary[] {
    return [
      mosfetTestbenches as any as TestbenchLibrary,
      rfAnalogTestbenches as any as TestbenchLibrary
    ];
  }

  // Calibrated Models - Load from metadata files and add synthetic data for other users
  getCalibratedModels(): CalibratedModel[] {
    const calibratedModels = [
      calNmos28nmMetadata,
      calPmos40nmMetadata,
      calFinfet14nmMetadata,
      calNmos65nmMetadata,
      calPmos28nmMetadata
    ];

    const baseModels = calibratedModels.map(metadata => ({
      model_id: metadata.model_id,
      name: metadata.name,
      description: metadata.description,
      base_model: metadata.base_model,
      model_template_id: metadata.model_template_id,
      version: metadata.version,
      status: metadata.status,
      category: metadata.category,
      subcategory: metadata.subcategory,
      technology: metadata.technology,
      author: metadata.author,
      calibration_info: {
        ...metadata.calibration_info,
        timestamp: metadata.calibration_info?.completion_date || metadata.timestamps?.created,
        metrics: {
          accuracy: metadata.calibration_info?.accuracy || 0
        }
      },
      reference_data: metadata.reference_data,
      validation: metadata.validation,
      files: metadata.files,
      timestamps: metadata.timestamps
    } as CalibratedModel));

    // Add more synthetic models for other users
    const additionalModels: CalibratedModel[] = [
      {
        model_id: "CAL-PMOS-65NM-002",
        name: "65nm PMOS High-Speed Model",
        description: "Optimized PMOS model for high-frequency applications",
        base_model: "BSIM4",
        version: "2.1.0",
        status: "in-progress",
        category: "transistor",
        subcategory: "pmos",
        technology: { node: "65nm", foundry: "GF" },
        author: { 
          name: "Sarah Chen", 
          email: "sarah.chen@company.com",
          department: "RF Team"
        },
        calibration_info: {
          request_id: "REQ-2025-004",
          engineer: "Sarah Chen",
          start_date: "2025-01-12T08:00:00Z",
          completion_date: null,
          total_time_hours: 8.5,
          iterations: 45,
          algorithm: "Gradient Descent",
          progress: 65,
          timestamp: "2025-01-14T10:00:00Z",
          metrics: { accuracy: 88.5 }
        },
        reference_data: {
          measurement_data: ["REF-MEAS-003"],
          total_points: 8500,
          temperature_range: [25, 85],
          voltage_range: [0, 1.8]
        }
      },
      {
        model_id: "CAL-NMOS-14NM-003",
        name: "14nm NMOS Low-Power Model",
        description: "Ultra-low power NMOS model for IoT applications",
        base_model: "PSP",
        version: "1.5.2",
        status: "completed",
        category: "transistor",
        subcategory: "nmos",
        technology: { node: "14nm", foundry: "Intel" },
        author: { 
          name: "Michael Brown", 
          email: "m.brown@company.com",
          department: "Low Power Design"
        },
        calibration_info: {
          request_id: "REQ-2025-005",
          engineer: "Michael Brown",
          start_date: "2025-01-05T09:00:00Z",
          completion_date: "2025-01-08T16:00:00Z",
          total_time_hours: 24,
          iterations: 198,
          algorithm: "Simulated Annealing",
          accuracy: 97.2,
          timestamp: "2025-01-08T16:00:00Z",
          metrics: { accuracy: 97.2 }
        },
        reference_data: {
          measurement_data: ["REF-MEAS-004", "REF-MEAS-005"],
          total_points: 22000,
          temperature_range: [-20, 100],
          voltage_range: [0, 0.8]
        }
      },
      {
        model_id: "CAL-BJT-40NM-001",
        name: "40nm NPN BJT Model",
        description: "High-gain bipolar junction transistor model",
        base_model: "Gummel-Poon",
        version: "1.0.0",
        status: "failed",
        category: "transistor",
        subcategory: "bjt",
        technology: { node: "40nm", foundry: "STM" },
        author: { 
          name: "Lisa Wang", 
          email: "lisa.wang@company.com",
          department: "Analog Design"
        },
        calibration_info: {
          request_id: "REQ-2025-006",
          engineer: "Lisa Wang",
          start_date: "2025-01-10T10:00:00Z",
          completion_date: "2025-01-10T15:00:00Z",
          total_time_hours: 5,
          iterations: 52,
          algorithm: "Nelder-Mead",
          accuracy: 72.5,
          error_message: "Convergence failed - insufficient data coverage",
          timestamp: "2025-01-10T15:00:00Z",
          metrics: { accuracy: 72.5 }
        },
        reference_data: {
          measurement_data: ["REF-MEAS-006"],
          total_points: 3200,
          temperature_range: [25],
          voltage_range: [0, 3.3]
        }
      },
      {
        model_id: "CAL-DIODE-SIC-001",
        name: "SiC Schottky Diode Model",
        description: "Power diode model for high-voltage applications",
        base_model: "SPICE Diode",
        version: "2.0.1",
        status: "completed",
        category: "diode",
        subcategory: "schottky",
        technology: { material: "SiC", voltage_rating: "1200V" },
        author: { 
          name: "Robert Taylor", 
          email: "r.taylor@company.com",
          department: "Power Electronics"
        },
        calibration_info: {
          request_id: "REQ-2025-007",
          engineer: "Robert Taylor",
          start_date: "2025-01-07T08:30:00Z",
          completion_date: "2025-01-09T14:00:00Z",
          total_time_hours: 28,
          iterations: 234,
          algorithm: "Trust Region",
          accuracy: 96.8,
          timestamp: "2025-01-09T14:00:00Z",
          metrics: { accuracy: 96.8 }
        },
        reference_data: {
          measurement_data: ["REF-MEAS-007", "REF-MEAS-008"],
          simulation_data: ["REF-SIM-020"],
          total_points: 18500,
          temperature_range: [-55, 175],
          voltage_range: [0, 1200]
        }
      },
      {
        model_id: "CAL-OPAMP-28NM-001",
        name: "28nm OpAmp Behavioral Model",
        description: "Behavioral model for operational amplifier",
        base_model: "Verilog-A",
        version: "1.3.0",
        status: "in-progress",
        category: "amplifier",
        subcategory: "opamp",
        technology: { node: "28nm", foundry: "TSMC" },
        author: { 
          name: "Jennifer Martinez", 
          email: "j.martinez@company.com",
          department: "Mixed-Signal Team"
        },
        calibration_info: {
          request_id: "REQ-2025-008",
          engineer: "Jennifer Martinez",
          start_date: "2025-01-13T09:00:00Z",
          completion_date: null,
          total_time_hours: 12,
          iterations: 89,
          algorithm: "Differential Evolution",
          progress: 45,
          timestamp: "2025-01-14T12:00:00Z",
          metrics: { accuracy: 85.3 }
        },
        reference_data: {
          measurement_data: [],
          simulation_data: ["REF-SIM-021", "REF-SIM-022"],
          total_points: 5600,
          temperature_range: [0, 85],
          voltage_range: [0, 1.2]
        }
      },
      {
        model_id: "CAL-INDUCTOR-RF-001",
        name: "RF Spiral Inductor Model",
        description: "High-Q inductor model for RF applications",
        base_model: "Pi-Model",
        version: "1.1.0",
        status: "completed",
        category: "passive",
        subcategory: "inductor",
        technology: { process: "65nm RF CMOS" },
        author: { 
          name: "David Kim", 
          email: "d.kim@company.com",
          department: "RF Design"
        },
        calibration_info: {
          request_id: "REQ-2025-009",
          engineer: "David Kim",
          start_date: "2025-01-06T10:00:00Z",
          completion_date: "2025-01-07T18:00:00Z",
          total_time_hours: 16,
          iterations: 142,
          algorithm: "Genetic Algorithm",
          accuracy: 94.5,
          timestamp: "2025-01-07T18:00:00Z",
          metrics: { accuracy: 94.5 }
        },
        reference_data: {
          measurement_data: ["REF-MEAS-009"],
          total_points: 8900,
          temperature_range: [25],
          voltage_range: [0, 3.3]
        }
      }
    ];

    return [...baseModels, ...additionalModels];
  }

  // Model Requests
  getModelRequests(): ModelRequest[] {
    return [
      {
        request_id: "REQ-2025-001",
        title: "28nm NMOS Model Update",
        type: "compact",
        component_type: "NMOS Transistor",
        technology: "28nm",
        priority: "high",
        status: "pending",
        requester: "John Doe",
        request_date: "2025-01-10T09:00:00Z",
        due_date: "2025-01-15T17:00:00Z",
        description: "Update model to match latest silicon measurements",
        attachments: ["silicon_data_v2.csv", "test_conditions.pdf"],
        comments: [
          { text: "Please prioritize subthreshold region", author: "John Doe", date: "2025-01-10T10:00:00Z" }
        ]
      },
      {
        request_id: "REQ-2025-002",
        title: "Power Amplifier Behavioral Model",
        type: "behavioral",
        component_type: "RF Amplifier",
        technology: "65nm",
        priority: "medium",
        status: "awaiting-info",
        requester: "Jane Smith",
        request_date: "2025-01-08T10:00:00Z",
        due_date: "2025-01-20T17:00:00Z",
        info_requested: "Please provide S-parameter measurements at 5GHz",
        comments: [
          { text: "Need S-parameter data for model validation", author: "Engineer", date: "2025-01-11T14:00:00Z" }
        ]
      },
      {
        request_id: "REQ-2025-003",
        title: "SiC Diode Recovery Model",
        type: "compact",
        component_type: "Power Diode",
        technology: "SiC",
        priority: "low",
        status: "pending",
        requester: "Mike Johnson",
        request_date: "2025-01-09T14:00:00Z",
        due_date: "2025-01-25T17:00:00Z"
      },
      {
        request_id: "REQ-2025-004",
        title: "14nm FinFET PMOS Calibration",
        type: "compact",
        component_type: "PMOS FinFET",
        technology: "14nm",
        priority: "high",
        status: "pending",
        requester: "Sarah Chen",
        request_date: "2025-01-12T08:30:00Z",
        due_date: "2025-01-18T17:00:00Z",
        description: "High-speed PMOS model for 5G RF applications"
      },
      {
        request_id: "REQ-2025-005",
        title: "GaN HEMT Power Model",
        type: "compact",
        component_type: "GaN HEMT",
        technology: "GaN",
        priority: "medium",
        status: "accepted",
        requester: "Robert Taylor",
        request_date: "2025-01-11T14:00:00Z",
        due_date: "2025-01-22T17:00:00Z",
        description: "High power GaN HEMT model for power amplifiers",
        assigned_engineer: "David Kim"
      },
      {
        request_id: "REQ-2025-006",
        title: "40nm BJT Temperature Model",
        type: "compact",
        component_type: "NPN BJT",
        technology: "40nm",
        priority: "low",
        status: "rejected",
        requester: "Lisa Wang",
        request_date: "2025-01-05T11:00:00Z",
        due_date: "2025-01-16T17:00:00Z",
        description: "Temperature-dependent BJT model",
        comments: [
          { text: "Insufficient test data provided", author: "Engineer", date: "2025-01-06T10:00:00Z" }
        ]
      },
      {
        request_id: "REQ-2025-007",
        title: "LDMOS RF Power Model",
        type: "compact",
        component_type: "LDMOS",
        technology: "130nm",
        priority: "medium",
        status: "pending",
        requester: "Michael Brown",
        request_date: "2025-01-13T09:15:00Z",
        due_date: "2025-01-24T17:00:00Z",
        description: "LDMOS model for base station applications"
      },
      {
        request_id: "REQ-2025-008",
        title: "7nm NMOS Corner Model",
        type: "compact",
        component_type: "NMOS Transistor",
        technology: "7nm",
        priority: "high",
        status: "awaiting-info",
        requester: "Jennifer Martinez",
        request_date: "2025-01-06T10:30:00Z",
        due_date: "2025-01-17T17:00:00Z",
        description: "Process corner model for yield analysis",
        info_requested: "Need corner lot measurements for FF/SS corners",
        comments: [
          { text: "Awaiting corner lot data", author: "Engineer", date: "2025-01-08T11:00:00Z" }
        ]
      },
      {
        request_id: "REQ-2025-009",
        title: "Varactor Diode C-V Model",
        type: "compact",
        component_type: "Varactor Diode",
        technology: "45nm",
        priority: "medium",
        status: "pending",
        requester: "David Wilson",
        request_date: "2025-01-14T13:00:00Z",
        due_date: "2025-01-26T17:00:00Z",
        description: "Voltage-controlled capacitor model for VCOs"
      },
      {
        request_id: "REQ-2025-010",
        title: "SOI NMOS Mismatch Model",
        type: "compact",
        component_type: "SOI NMOS",
        technology: "22nm",
        priority: "low",
        status: "accepted",
        requester: "Emily Garcia",
        request_date: "2025-01-07T15:45:00Z",
        due_date: "2025-01-19T17:00:00Z",
        description: "Statistical mismatch model for analog design",
        assigned_engineer: "Sarah Chen"
      },
      {
        request_id: "REQ-2025-011",
        title: "Tunnel FET I-V Model",
        type: "compact",
        component_type: "Tunnel FET",
        technology: "10nm",
        priority: "medium",
        status: "pending",
        requester: "Alex Thompson",
        request_date: "2025-01-15T08:00:00Z",
        due_date: "2025-01-28T17:00:00Z",
        description: "Ultra-low power tunnel FET model"
      },
      {
        request_id: "REQ-2025-012",
        title: "InGaAs HEMT Noise Model",
        type: "compact",
        component_type: "InGaAs HEMT",
        technology: "InGaAs",
        priority: "high",
        status: "pending",
        requester: "Maria Rodriguez",
        request_date: "2025-01-04T12:20:00Z",
        due_date: "2025-01-14T17:00:00Z",
        description: "Low-noise amplifier model for mmWave"
      }
    ];
  }

  // Workflow Steps
  getWorkflowSteps() {
    return [
      { id: 1, name: "Request", status: "completed" as const, description: "Model request received and validated", progress: 100 },
      { id: 2, name: "Data Prep", status: "completed" as const, description: "Reference data cleaned and formatted", progress: 100 },
      { id: 3, name: "Calibration", status: "in-progress" as const, description: "Parameter optimization in progress", progress: 65 },
      { id: 4, name: "Validation", status: "pending" as const, description: "Model validation against test data", progress: 0 },
      { id: 5, name: "Report", status: "pending" as const, description: "Generate calibration report", progress: 0 }
    ];
  }

  // Statistics
  getStatistics() {
    return {
      totalModels: 156,
      activeRequests: 12,
      completedThisMonth: 23,
      averageAccuracy: 96.5,
      averageCalibrationTime: 4.2,
      libraryStats: {
        modelTemplates: 45,
        referenceDatasets: 238,
        testbenches: 67,
        calibratedModels: 156
      }
    };
  }
}

const dataService = new DataService();
export default dataService;