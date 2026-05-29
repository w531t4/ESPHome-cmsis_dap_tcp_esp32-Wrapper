<!--
SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
SPDX-License-Identifier: MIT
-->
# ESPHome CMSIS-DAP TCP wrapper

This repo starts with a vanilla ESPHome external component named
`cmsis_dap_tcp`.

The first milestone is deliberately small: prove ESPHome can discover,
configure, compile, and instantiate the external component. Once that works,
the CMSIS-DAP TCP library integration can be added in a separate step.

## Test config

See `examples/vanilla.yaml`.
