# PID Compact Mode Guard

Two LAD networks that force `PID_Compact` operating mode through
`{{PID_INSTANCE}}.sRet.i_Mode`.

- `{{PID_ENABLE}} = TRUE`: if mode is not `3`, move `3` into `i_Mode`.
- `{{PID_ENABLE}} = FALSE`: if mode is not `0`, move `0` into `i_Mode`.

This is the preferred PID guard style for the current workspace because it
matches the known-good exported program pattern.

Use this after the `PID_Compact` call pattern.
