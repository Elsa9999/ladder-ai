# Missing Pattern Backlog

These patterns are not yet complete library entries. Add them only from real
TIA Portal V18 exports or from code that is proven by import/compile.

## High Priority

- `TP` pulse timer
- `TOF` off-delay timer
- `R_TRIG` / `P_TRIG` rising-edge instruction
- `F_TRIG` falling-edge instruction
- `NORM_X`
- `SCALE_X`
- `LIMIT`
- `SEL`
- HMI tag binding examples for WinCC Advanced

## Medium Priority

- `DIV` as a native instruction export, if different from the current generated
  real division pattern.
- `MOVE_BLK`
- `FILL_BLK`
- Array element access examples
- UDT data block examples
- Optimized DB examples
- Standard Non-Optimized DB examples beyond Modbus holding registers

## Hardware/Project Setup Patterns

These may not be reliably importable as block XML and may require a seed TIA
project instead:

- CPU clock memory byte setup
- CPU system memory byte setup
- PROFINET network topology
- HMI device and screen objects
- Technology Object creation for `PID_Compact`
- RS485 communication module hardware configuration

## Legacy Only

- GET/PUT PLC-to-PLC communication examples, only for comparison with old
  projects. Do not use them for new contest work.
