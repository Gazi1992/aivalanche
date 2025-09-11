# EKV 2.6 Model Documentation

## Overview
The EKV (Enz-Krummenacher-Vittoz) model is a charge-based MOSFET model optimized for analog circuit design, particularly in low-power applications.

## Key Features
- Continuous modeling from weak to strong inversion
- Charge-based formulation
- Symmetric source/drain treatment
- Excellent for low-power analog design
- Simple parameter extraction

## Model Equations
The drain current is expressed as:
```
ID = IS * (if - ir)
```
where IS is the specific current and if, ir are the forward and reverse normalized currents.

## Parameters
- **VTO**: Zero-bias threshold voltage
- **KP**: Transconductance parameter
- **GAMMA**: Body effect factor
- **PHI**: Surface potential
- **THETA**: Mobility reduction
- **ETA**: DIBL coefficient

## Applications
- Low-power analog circuits
- Operational amplifiers
- Voltage references
- Current mirrors
- Analog filters

## Usage Example
```spice
.include "ekv26_nmos.cir"
X1 drain gate source bulk nmos_ekv L=180n W=1u
```

## Weak Inversion
The EKV model excels in weak inversion modeling, making it ideal for:
- Subthreshold circuits
- Ultra-low power designs
- Biomedical applications

## Temperature Effects
Temperature modeling includes:
- Threshold voltage variation
- Mobility temperature dependence
- Subthreshold slope temperature effects