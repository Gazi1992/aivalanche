import { ModelParameter } from '../types';

// BSIM4 NMOS Parameters (from actual CSV file)
export const bsim4NmosParameters: ModelParameter[] = [
  { name: 'VTH0', subckt: 'nmos_model', default: '0.482', min: 0.3, max: 0.7, unit: 'V', description: 'Long channel threshold voltage at Vbs=0' },
  { name: 'U0', subckt: 'nmos_model', default: '445.3', min: 200, max: 600, unit: 'cm²/Vs', description: 'Low-field mobility at Tnom' },
  { name: 'VSAT', subckt: 'nmos_model', default: '8.15e4', min: 5e4, max: 1.2e5, unit: 'm/s', description: 'Saturation velocity at Tnom' },
  { name: 'K1', subckt: 'nmos_model', default: '0.523', min: 0.3, max: 0.8, unit: 'V^0.5', description: 'First-order body effect coefficient' },
  { name: 'K2', subckt: 'nmos_model', default: '0.0098', min: -0.1, max: 0.1, unit: '-', description: 'Second-order body effect coefficient' },
  { name: 'K3', subckt: 'nmos_model', default: '80', min: 30, max: 100, unit: '-', description: 'Narrow width coefficient' },
  { name: 'K3B', subckt: 'nmos_model', default: '0', min: -5, max: 5, unit: 'V^-1', description: 'Body effect coefficient of K3' },
  { name: 'W0', subckt: 'nmos_model', default: '2.5e-6', min: 1e-6, max: 5e-6, unit: 'm', description: 'Narrow width parameter' },
  { name: 'TOX', subckt: 'nmos_model', default: '1.38e-9', min: 1e-9, max: 2e-9, unit: 'm', description: 'Gate oxide thickness' },
  { name: 'TOXM', subckt: 'nmos_model', default: '1.38e-9', min: 1e-9, max: 2e-9, unit: 'm', description: 'Gate oxide thickness for CV model' },
  { name: 'XJ', subckt: 'nmos_model', default: '1.48e-7', min: 1e-7, max: 2e-7, unit: 'm', description: 'Junction depth' },
  { name: 'NCH', subckt: 'nmos_model', default: '1.68e17', min: 1e17, max: 3e17, unit: 'cm^-3', description: 'Channel doping concentration' },
  { name: 'NSUB', subckt: 'nmos_model', default: '6e16', min: 1e16, max: 1e17, unit: 'cm^-3', description: 'Substrate doping concentration' },
  { name: 'XT', subckt: 'nmos_model', default: '1.55e-7', min: 1e-7, max: 2e-7, unit: 'm', description: 'Doping depth' },
  { name: 'VOFF', subckt: 'nmos_model', default: '-0.08', min: -0.2, max: 0, unit: 'V', description: 'Offset voltage in subthreshold region' },
  { name: 'NFACTOR', subckt: 'nmos_model', default: '1.02', min: 0.8, max: 1.5, unit: '-', description: 'Subthreshold swing factor' },
  { name: 'CDSC', subckt: 'nmos_model', default: '2.4e-4', min: 0, max: 1e-3, unit: 'F/m²', description: 'Drain-source coupling capacitance' },
  { name: 'CDSCB', subckt: 'nmos_model', default: '0', min: -1e-4, max: 1e-4, unit: 'F/Vm²', description: 'Body-bias sensitivity of CDSC' },
  { name: 'CDSCD', subckt: 'nmos_model', default: '0', min: -1e-4, max: 1e-4, unit: 'F/Vm²', description: 'Drain-bias sensitivity of CDSC' },
  { name: 'CIT', subckt: 'nmos_model', default: '0', min: -1e-3, max: 1e-3, unit: 'F/m²', description: 'Interface trap capacitance' },
  { name: 'UA', subckt: 'nmos_model', default: '9.8e-10', min: 5e-10, max: 2e-9, unit: 'm/V', description: 'First-order mobility degradation' },
  { name: 'UB', subckt: 'nmos_model', default: '1.05e-18', min: 5e-19, max: 2e-18, unit: 'm²/V²', description: 'Second-order mobility degradation' },
  { name: 'UC', subckt: 'nmos_model', default: '-4.65e-11', min: -1e-10, max: 0, unit: 'V^-1', description: 'Body-effect mobility degradation' },
  { name: 'EU', subckt: 'nmos_model', default: '1.67', min: 1, max: 2, unit: '-', description: 'Mobility exponent' },
  { name: 'A0', subckt: 'nmos_model', default: '1', min: 0.5, max: 2, unit: '-', description: 'Bulk charge effect coefficient' },
  { name: 'AGS', subckt: 'nmos_model', default: '0.44', min: 0.1, max: 1, unit: 'V^-1', description: 'Gate-bias coefficient of Abulk' },
  { name: 'B0', subckt: 'nmos_model', default: '0', min: -1, max: 1, unit: 'm', description: 'Bulk charge effect width parameter' },
  { name: 'B1', subckt: 'nmos_model', default: '0', min: -1, max: 1, unit: 'm', description: 'Bulk charge effect bias parameter' },
  { name: 'KETA', subckt: 'nmos_model', default: '-0.047', min: -0.2, max: 0, unit: 'V^-1', description: 'Body-bias coefficient of bulk charge' },
  { name: 'A1', subckt: 'nmos_model', default: '0', min: -0.5, max: 0.5, unit: 'V^-1', description: 'First non-saturation parameter' },
  { name: 'A2', subckt: 'nmos_model', default: '1', min: 0.5, max: 1.5, unit: '-', description: 'Second non-saturation parameter' },
  { name: 'DVT0', subckt: 'nmos_model', default: '2.18', min: 1, max: 3, unit: '-', description: 'First coefficient of short-channel effect' },
  { name: 'DVT1', subckt: 'nmos_model', default: '0.535', min: 0.3, max: 0.8, unit: '-', description: 'Second coefficient of short-channel effect' },
  { name: 'DVT2', subckt: 'nmos_model', default: '-0.032', min: -0.1, max: 0, unit: 'V^-1', description: 'Body-bias coefficient of short-channel' },
  { name: 'DVT0W', subckt: 'nmos_model', default: '0', min: -1, max: 1, unit: '-', description: 'First coefficient of narrow width effect' },
  { name: 'DVT1W', subckt: 'nmos_model', default: '5.3e6', min: 1e6, max: 1e7, unit: 'm^-1', description: 'Second coefficient of narrow width effect' },
  { name: 'DVT2W', subckt: 'nmos_model', default: '-0.032', min: -0.1, max: 0, unit: 'V^-1', description: 'Body-bias coefficient of narrow width' },
  { name: 'DROUT', subckt: 'nmos_model', default: '0.56', min: 0.1, max: 1, unit: '-', description: 'L dependence coefficient of DIBL' },
  { name: 'DSUB', subckt: 'nmos_model', default: '0.56', min: 0.1, max: 1, unit: '-', description: 'Subthreshold DIBL coefficient' },
  { name: 'ETA0', subckt: 'nmos_model', default: '0.08', min: 0, max: 0.2, unit: '-', description: 'Subthreshold region DIBL coefficient' },
  { name: 'ETAB', subckt: 'nmos_model', default: '-0.07', min: -0.2, max: 0, unit: 'V^-1', description: 'Body-bias coefficient for DIBL' },
  { name: 'PCLM', subckt: 'nmos_model', default: '1.28', min: 0.5, max: 2, unit: '-', description: 'Channel length modulation parameter' },
  { name: 'PDIBLC1', subckt: 'nmos_model', default: '0.385', min: 0.1, max: 0.5, unit: '-', description: 'First parameter of DIBL effect' },
  { name: 'PDIBLC2', subckt: 'nmos_model', default: '8.6e-3', min: 1e-3, max: 0.02, unit: '-', description: 'Second parameter of DIBL effect' },
  { name: 'PDIBLCB', subckt: 'nmos_model', default: '0', min: -0.1, max: 0.1, unit: 'V^-1', description: 'Body effect coefficient of DIBL' },
  { name: 'PSCBE1', subckt: 'nmos_model', default: '4.24e8', min: 1e8, max: 1e9, unit: 'V/m', description: 'First substrate current body-effect' },
  { name: 'PSCBE2', subckt: 'nmos_model', default: '1e-5', min: 1e-6, max: 1e-4, unit: 'm/V', description: 'Second substrate current body-effect' },
  { name: 'PVAG', subckt: 'nmos_model', default: '0', min: -1, max: 1, unit: '-', description: 'Gate voltage dependence of Rout' },
];

// PSP PMOS Parameters  
export const pspPmosParameters: ModelParameter[] = [
  { name: 'VFB', subckt: 'pmos_model', default: '-1.05', min: -1.5, max: -0.8, unit: 'V', description: 'Flatband voltage' },
  { name: 'PHIB', subckt: 'pmos_model', default: '1.13', min: 1.0, max: 1.3, unit: 'V', description: 'Surface potential at strong inversion' },
  { name: 'K1', subckt: 'pmos_model', default: '0.65', min: 0.5, max: 0.8, unit: 'V^0.5', description: 'Body effect coefficient' },
  { name: 'K2', subckt: 'pmos_model', default: '-0.08', min: -0.2, max: 0.05, unit: '-', description: 'Second-order body effect' },
  { name: 'MUE', subckt: 'pmos_model', default: '165', min: 100, max: 250, unit: 'cm²/Vs', description: 'Mobility at Tref' },
  { name: 'THEMU', subckt: 'pmos_model', default: '-1.5', min: -2.0, max: -1.0, unit: '-', description: 'Temperature coefficient of mobility' },
  { name: 'MU0', subckt: 'pmos_model', default: '0.04', min: 0.02, max: 0.06, unit: 'm²/Vs', description: 'Low-field mobility' },
  { name: 'CS', subckt: 'pmos_model', default: '0.7', min: 0.5, max: 1.0, unit: '-', description: 'Coulomb scattering coefficient' },
  { name: 'XCOR', subckt: 'pmos_model', default: '0.4', min: 0.2, max: 0.6, unit: '-', description: 'Velocity overshoot coefficient' },
  { name: 'FETA', subckt: 'pmos_model', default: '1.0', min: 0.5, max: 1.5, unit: '-', description: 'Velocity saturation parameter' },
  { name: 'RS', subckt: 'pmos_model', default: '150', min: 100, max: 300, unit: 'Ω·μm', description: 'Source resistance' },
  { name: 'RD', subckt: 'pmos_model', default: '150', min: 100, max: 300, unit: 'Ω·μm', description: 'Drain resistance' },
  { name: 'RSB', subckt: 'pmos_model', default: '0', min: -50, max: 50, unit: 'Ω·μm', description: 'Body-bias dependent source resistance' },
  { name: 'RDB', subckt: 'pmos_model', default: '0', min: -50, max: 50, unit: 'Ω·μm', description: 'Body-bias dependent drain resistance' },
  { name: 'RSG', subckt: 'pmos_model', default: '0', min: -50, max: 50, unit: 'Ω·μm', description: 'Gate-bias dependent source resistance' },
  { name: 'RDG', subckt: 'pmos_model', default: '0', min: -50, max: 50, unit: 'Ω·μm', description: 'Gate-bias dependent drain resistance' },
  { name: 'VSAT', subckt: 'pmos_model', default: '7.5e4', min: 5e4, max: 1e5, unit: 'm/s', description: 'Saturation velocity' },
  { name: 'XISAT', subckt: 'pmos_model', default: '0.3', min: 0.1, max: 0.5, unit: '-', description: 'VSAT temperature coefficient' },
  { name: 'THESAT', subckt: 'pmos_model', default: '0.9', min: 0.5, max: 1.5, unit: '-', description: 'Velocity saturation temperature parameter' },
  { name: 'THESATB', subckt: 'pmos_model', default: '0.0', min: -0.5, max: 0.5, unit: 'V^-1', description: 'Body effect of velocity saturation' },
  { name: 'THESATG', subckt: 'pmos_model', default: '0.0', min: -0.5, max: 0.5, unit: 'V^-1', description: 'Gate effect of velocity saturation' },
  { name: 'A1', subckt: 'pmos_model', default: '0.0', min: -0.5, max: 0.5, unit: 'V^-1', description: 'CLM parameter' },
  { name: 'A2', subckt: 'pmos_model', default: '1.0', min: 0.5, max: 1.5, unit: '-', description: 'CLM parameter' },
  { name: 'A3', subckt: 'pmos_model', default: '1.0', min: 0.5, max: 1.5, unit: '-', description: 'CLM parameter' },
  { name: 'A4', subckt: 'pmos_model', default: '0.0', min: -0.5, max: 0.5, unit: 'V', description: 'CLM parameter' },
  { name: 'STA2', subckt: 'pmos_model', default: '0.0', min: -1e-3, max: 1e-3, unit: 'V^-1', description: 'DIBL parameter for VT' },
  { name: 'DIB0', subckt: 'pmos_model', default: '1.0', min: 0.5, max: 2.0, unit: '-', description: 'DIBL coefficient' },
  { name: 'DIB1', subckt: 'pmos_model', default: '0.7', min: 0.3, max: 1.0, unit: '-', description: 'DIBL coefficient' },
  { name: 'DIB2', subckt: 'pmos_model', default: '2e-3', min: 0, max: 5e-3, unit: '-', description: 'DIBL coefficient' },
];

// Add more model parameters as needed...

// Map model IDs to their parameters
export const modelParametersMap: { [key: string]: ModelParameter[] } = {
  'MOD-BSIM4-001': bsim4NmosParameters,  // BSIM4 NMOS
  'MOD-PSP-001': pspPmosParameters,       // PSP PMOS
  'MOD-BSIM4-002': pspPmosParameters,     // BSIM4 PMOS (using PSP params as example)
  'MOD-PSP-002': bsim4NmosParameters,     // PSP NMOS (using BSIM4 params as example)
  'MOD-BSIM3-002': pspPmosParameters,     // BSIM3 PMOS
  'MOD-EKV-001': bsim4NmosParameters,     // EKV NMOS
  'MOD-BSIMCMG-001': bsim4NmosParameters, // BSIMCMG FinFET
  'MOD-DIODE-001': [],                    // Schottky Diode
  'MOD-HEMT-001': [],                     // HEMT GaAs
  'MOD-BJT-001': [],                      // BJT
  'MOD-MISMATCH-001': bsim4NmosParameters,// Mismatch NMOS
  'MOD-RES-001': [],                      // Resistor
  'MOD-LDMOS-001': [],                    // LDMOS
  'MOD-SOI-001': bsim4NmosParameters,     // SOI NMOS
  'MOD-TFET-001': [],                     // Tunnel FET
};

export function getModelParameters(modelId: string): ModelParameter[] {
  return modelParametersMap[modelId] || [];
}