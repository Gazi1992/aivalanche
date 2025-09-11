# Examples Directory

This directory contains example files for the Model Management System, organized into three categories:

## Directory Structure

```
examples/
├── ref_data/           # Reference data examples (measurements and simulations)
├── models/             # Model examples (BSIM4, PSP, EKV)
└── testbenches/        # Testbench examples (DC, AC, Transient)
```

## Reference Data (`ref_data/`)

Contains example measurement and simulation data files in JSON format:
- **nmos_id_vds_sweep.json**: NMOS drain current vs drain-source voltage characteristics
- **pmos_capacitance_vs_frequency.json**: PMOS gate capacitance frequency response

### Reference Data Format
- Metadata section with device info and test conditions
- Data arrays with measurement values
- Units specification for all parameters

## Models (`models/`)

Contains example model files for different compact models:
- **BSIM4 NMOS Example**: 
  - `bsim4_nmos_example.cir` - SPICE model card
  - `bsim4_nmos_parameters.csv` - Parameter list with values
  - `bsim4_nmos_metadata.json` - Model metadata and validation info
- **PSP PMOS Example**:
  - `psp_pmos_example.cir` - PSP model implementation

### Model File Types
- `.cir` - SPICE-compatible model cards
- `.csv` - Parameter tables with descriptions
- `.json` - Metadata with validation and usage info

## Testbenches (`testbenches/`)

Contains example testbench configurations:
- **dc_sweep_id_vds.json**: DC sweep testbench for Id-Vds characteristics
- **ac_analysis_frequency_response.json**: AC frequency response analysis
- **transient_ring_oscillator.json**: Ring oscillator transient simulation

### Testbench Format
- Complete netlist with parameters
- Simulation settings and convergence criteria
- Measurement definitions
- Output specifications
- Validation status

## Usage

These examples can be:
1. **Uploaded directly** through the UI upload modals
2. **Used as templates** for creating new files
3. **Referenced** for correct file formats
4. **Tested** to verify system functionality

## File Formats

### JSON Structure
All JSON files follow a consistent structure with:
- Metadata/info section
- Data/parameters section
- Validation information
- Author details
- Timestamps

### CSV Format
Parameter files use standard CSV with headers:
- Parameter name
- Value
- Unit
- Category
- Description

### SPICE Format
Model cards follow standard SPICE syntax:
- Model definition with level
- Parameter assignments
- Comments for documentation

## Validation

All example files have been validated and tested with:
- Correct syntax and structure
- Realistic parameter values
- Proper units and ranges
- Complete metadata

## Notes

- Temperature values are in Celsius unless specified
- All geometric dimensions are in meters
- Voltages in Volts, currents in Amperes
- Frequencies in Hertz
- Time values in seconds