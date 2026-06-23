# Compile Notes

- `{{PID_INSTANCE}}` must be a valid `PID_Compact` technology-object instance.
- The PID call itself should use `PID_Compact` version `1.2`.
- `{{PID_ENABLE}}` must be a Bool tag.
- Do not confuse `ManualEnable` with `sRet.i_Mode`.
- If TIA reports a missing technology object or instance DB, create the
  corresponding PID technology object in TIA Portal V18 before compiling.
