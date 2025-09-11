# Schottky Diode Model Documentation

## Overview
This document describes the Schottky diode model for SiC power electronics applications.

## Model Features
- Zero reverse recovery time
- High breakdown voltage (650V)
- Low forward voltage drop
- Temperature-dependent characteristics
- Accurate capacitance modeling

## Parameters
Key model parameters include:
- IS: Saturation current
- N: Ideality factor  
- RS: Series resistance
- BV: Breakdown voltage
- CJO: Junction capacitance

## Applications
- Power converters
- Switch-mode power supplies
- Solar inverters
- Motor drives

## Usage Example
```spice
.include "schottky_diode.cir"
X1 anode cathode schottky_sic area=1e-6
```