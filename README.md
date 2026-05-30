<!--
SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
SPDX-License-Identifier: MIT
-->
# ESPHome CMSIS-DAP TCP wrapper

External ESPHome component wrapper for `bkuschak/cmsis_dap_tcp_esp32`.

ESPHome owns Wi-Fi, logging, OTA, and the normal device lifecycle. This wrapper
starts the upstream CMSIS-DAP TCP task as an ESPHome component.

The first library-backed version is intentionally JTAG-only and single-instance.
The upstream CMSIS-DAP implementation keeps DAP state in globals, so two
independent JTAG ports will require a deeper library refactor.

## Upstream library

The `idf_components/cmsis_dap_tcp_esp32` adapter fetches
`bkuschak/cmsis_dap_tcp_esp32` during CMake configuration and builds the DAP
engine/TCP server sources from that checkout. It does not reference any local
checkout outside this repository.

## Test config

See `examples/vanilla.yaml`.

The relevant component block looks like:

```yaml
cmsis_dap_tcp:
  tck_pin: GPIO18
  tms_pin: GPIO5
  tdi_pin: GPIO23
  tdo_pin: GPIO34
  port: 4441
```
