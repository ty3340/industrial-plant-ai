# Instrument Calibration Certificates - Q3 2026

## Batch Plant Production Equipment

**Document ID:** CAL-CERT-2026-Q3
**Revision:** 2
**Accreditation:** ISO/IEC 17025:2017
**Last Updated:** August 15, 2026
**Calibration Technician:** K. Manditereza
**Approved By:** J. Chen (Maintenance Manager)

This document records the calibration status of all critical measurement
instruments on the batch plant production line. Instruments are calibrated
against ISO/IEC 17025 accredited reference standards. Production of any
product requires that the relevant instruments hold a **valid** calibration
certificate on the planned production date.

---

## Calibration Certificate Details

### TEMP-01 (Reactor Temperature Transmitter)

- **Equipment:** REACTOR-01
- **Parameter:** Process temperature
- **Measurement Range:** 0-200 °C
- **Last Calibrated:** March 30, 2026
- **Calibration Interval:** 6 months
- **Reference Standard:** Fluke 1524 RTD reference (traceable to NIST)
- **As-Found Deviation:** +0.12 °C
- **As-Left Deviation:** ±0.05 °C (Specification: ±0.5 °C)
- **Result:** PASSED
- **Critical For:** Product A (requires stable temperature control of ±0.5 °C)

### PRESS-01 (Reactor Pressure Transmitter)

- **Equipment:** REACTOR-01
- **Parameter:** Vessel pressure
- **Measurement Range:** 0-10 bar
- **Last Calibrated:** February 28, 2026
- **Calibration Interval:** 6 months
- **Reference Standard:** Druck DPI 620 pressure calibrator
- **As-Left Deviation:** ±0.02 bar (Specification: ±0.1 bar)
- **Result:** PASSED

### FLOW-01 (Material A Dosing Flow Meter)

- **Equipment:** Tank 1 -> MIXER-01 (Material A)
- **Parameter:** Mass flow during dosing
- **Measurement Range:** 0-500 L/min
- **Last Calibrated:** March 12, 2026
- **Calibration Interval:** 6 months
- **Reference Standard:** Coriolis master meter (ISO 17025 accredited)
- **As-Left Deviation:** ±0.3% (Specification: ±1.0%)
- **Result:** PASSED

### FLOW-02 (Material B Dosing Flow Meter)

- **Equipment:** Tank 2 -> MIXER-01 (Material B)
- **Parameter:** Mass flow during dosing
- **Measurement Range:** 0-500 L/min
- **Last Calibrated:** February 18, 2026
- **Calibration Interval:** 6 months
- **Reference Standard:** Coriolis master meter (ISO 17025 accredited)
- **As-Left Deviation:** ±0.4% (Specification: ±1.0%)
- **Result:** PASSED - approaching recalibration due date

### LEVEL-01 (Material C Tank Level Transmitter)

- **Equipment:** Tank 3 (Material C)
- **Parameter:** Tank level
- **Measurement Range:** 0-100 %
- **Last Calibrated:** May 05, 2026
- **Calibration Interval:** 6 months
- **Reference Standard:** Surveyed reference height gauge
- **As-Left Deviation:** ±0.5% (Specification: ±2.0%)
- **Result:** PASSED

### SPEED-01 (Mixer Speed Sensor)

- **Equipment:** MIXER-01
- **Parameter:** Agitator rotational speed
- **Measurement Range:** 0-1500 RPM
- **Last Calibrated:** March 22, 2026
- **Calibration Interval:** 6 months
- **Reference Standard:** Calibrated optical tachometer
- **As-Left Deviation:** ±0.8% (Specification: <2.0% variance)
- **Result:** PASSED
- **Critical For:** Product A (mixer speed variance must be <2%)

### WEIGHT-01 (Filler Load Cell)

- **Equipment:** FILLER-01
- **Parameter:** Fill weight
- **Measurement Range:** 0-50 kg
- **Last Calibrated:** April 15, 2026
- **Calibration Interval:** 6 months
- **Reference Standard:** OIML Class F1 reference weights
- **As-Left Deviation:** ±0.1% (Specification: ±0.5%)
- **Result:** PASSED
- **Note:** Replaces the FILLER-01 weight calibration that expired February 15, 2026.

---

## Calibration Status Summary

The table below is the authoritative list of calibration expiry (due) dates.
A production run cannot proceed if a required instrument's certificate has
expired on or before the production date.

| Instrument | Type                    | Equipment  | Calibration Due | Status   |
| ---------- | ----------------------- | ---------- | --------------- | -------- |
| TEMP-01    | Temperature Transmitter | REACTOR-01 | Sep 30, 2026    | Valid    |
| PRESS-01   | Pressure Transmitter    | REACTOR-01 | Aug 28, 2026    | Valid    |
| FLOW-01    | Mass Flow Meter         | Tank 1     | Sep 12, 2026    | Valid    |
| FLOW-02    | Mass Flow Meter         | Tank 2     | Aug 18, 2026    | Due Soon |
| LEVEL-01   | Level Transmitter       | Tank 3     | Nov 05, 2026    | Valid    |
| SPEED-01   | Speed Sensor            | MIXER-01   | Sep 22, 2026    | Valid    |
| WEIGHT-01  | Load Cell               | FILLER-01  | Oct 15, 2026    | Valid    |

_(TOGGLE: Change TEMP-01 Calibration Due to Aug 10, 2026 for NO-GO - this expires the temperature transmitter that Product A depends on, triggering a Product A calibration violation.)_

---

## Critical Instrument Requirements by Product

### Product A

- **Mandatory valid calibration:** TEMP-01 (±0.5 °C control) and SPEED-01 (<2% speed variance)
- Production must NOT proceed if TEMP-01 or SPEED-01 certificates are expired
- Reactor temperature and mixer speed are the controlling parameters for Product A quality

### Product B

- Standard instrument calibration applies (less sensitive to instrument variation)
- Can proceed provided no critical instrument is expired

### Product C

- Requires valid FLOW-01, FLOW-02, and LEVEL-01 for accurate Material C dosing
- Additional verification recommended after specialized cleaning cycles

---

## Validation and Traceability

- All reference standards are traceable to national metrology institutes (NIST/NPL).
- Calibration records are retained for a minimum of 3 years.
- Out-of-tolerance instruments are tagged OUT OF SERVICE until recalibrated.
- **Next scheduled calibration review:** November 1, 2026
