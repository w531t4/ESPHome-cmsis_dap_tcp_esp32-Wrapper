<!--
SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
SPDX-License-Identifier: MIT
-->
# ESPHome CMSIS-DAP TCP wrapper

External ESPHome component wrapper for `w531t4/cmsis_dap_tcp_esp32`, a fork of
the original `bkuschak/cmsis_dap_tcp_esp32` project.

ESPHome owns Wi-Fi, logging, OTA, and the normal device lifecycle. This wrapper
starts the upstream CMSIS-DAP TCP task as an ESPHome component.

The result is an ESP32 running ESPHome that can act as a network-attached
CMSIS-DAP JTAG adapter. OpenOCD connects to the ESP32 over TCP, then performs
target-specific JTAG operations such as FPGA SRAM loading or SPI flash
programming.

The wrapper can also enable the upstream UART-to-TCP bridge task, with UART
settings supplied from the ESPHome YAML.

## Tested hardware

The current working path has been tested with:

- ESP32 dev board using the ESP-IDF framework under ESPHome.
- ULX3S / Lattice ECP5 target.
- OpenOCD using the `cmsis-dap-tcp` backend and `fpga/lattice_ecp5.cfg`.
- ULX3S SPI flash detected through OpenOCD JTAG-SPI as `issi is25lp128d`.

Other ESP32 boards and JTAG targets may work, but they are outside the current
tested v1 path.

## Wiring

The example configuration uses this ESP32 JTAG pin assignment:

| CMSIS-DAP signal | ESP32 GPIO |
| --- | --- |
| TCK | GPIO18 |
| TMS | GPIO5 |
| TDI | GPIO23 |
| TDO | GPIO34 |
| LED | GPIO32 |

Connect the JTAG signals to the matching JTAG pins on the target. The LED pin is
optional and is driven while the probe is connected. `nTRST` and `nRESET` are
also optional; add `ntrst_pin` and `nreset_pin` when your target wiring needs
them.

The same example also configures a UART bridge:

| UART signal | ESP32 GPIO |
| --- | --- |
| TX | GPIO3 |
| RX | GPIO1 |

Wire ESP32 TX to the target RX and ESP32 RX to the target TX.

## ESPHome YAML

See `examples/vanilla.yaml` for the complete test configuration. The JTAG-only
component block is:

```yaml
cmsis_dap_tcp:
  tck_pin: GPIO18
  tms_pin: GPIO5
  tdi_pin: GPIO23
  tdo_pin: GPIO34
  led_pin: GPIO32
  led_active_high: false
  port: 4441
  service_name: CMSIS-DAP Primary
  io_port_write_cycles: 72
  delay_slow_cycles: 5
```

To also expose a target UART over TCP, configure `cmsis_dap_tcp.uart_bridge`:

```yaml
cmsis_dap_tcp:
  tck_pin: GPIO18
  tms_pin: GPIO5
  tdi_pin: GPIO23
  tdo_pin: GPIO34
  led_pin: GPIO32
  led_active_high: false
  port: 4441
  service_name: CMSIS-DAP Primary
  uart_bridge:
    tx_pin: GPIO3
    rx_pin: GPIO1
    port: 4442
    uart_num: 1
    baud_rate: 115200
    data_bits: 8
    parity: NONE
    stop_bits: 1
```

The example uses ESPHome to configure Wi-Fi, API, OTA, logging, and fallback AP
behavior.

`service_name` is optional. When omitted, service switches use the default names
`CMSIS-DAP TCP Service {port}` and `UART Bridge Service {port}`. When set, the
CMSIS-DAP switch name uses `{service_name} {port}` and the UART bridge switch
name uses `{service_name} UART {port}` unless `cmsis_dap_switch` or
`uart_bridge_switch` explicitly sets a switch name.

## UART Bridge

The UART bridge uses the upstream `uart_bridge_task()` implementation. The
wrapper maps YAML options into the upstream ESP-IDF sdkconfig values and enables
`CONFIG_VFS_SUPPORT_SELECT` so the upstream bridge can wait on both TCP sockets
and UART VFS file descriptors inside the ESPHome build.

`led_pin`, `led_active_high`, `io_port_write_cycles`, and
`delay_slow_cycles` are passed through to the upstream CMSIS-DAP runtime GPIO
configuration. Leave timing at the defaults unless target timing needs to be
tuned.

For a quick smoke test, connect to the configured bridge port:

```sh
nc 192.168.2.175 4442
```

This proves the TCP listener accepts a connection. Seeing data in the TCP
session requires a target connected to the UART bus that actively transmits
serial output.

## OpenOCD

Detailed OpenOCD proof commands live in `examples/openocd_ulx3s_ecp5.md`.
That document includes:

- A non-OpenOCD TCP listener smoke test with `nc`.
- ECP5 JTAG ID scan.
- Volatile FPGA SRAM load with `pld load`.
- Persistent SPI flash programming through JTAG-SPI.
- Verify-only proof for persistent flash contents.

## Programming modes

For the tested ECP5 path, OpenOCD can program the FPGA in two different ways:

- Volatile SRAM programming loads the bitstream directly into the FPGA fabric.
  It is useful for quick tests, but the design is lost when the target loses
  power or reconfigures.
- Persistent SPI flash programming writes the bitstream to the flash connected
  to the FPGA. On the ULX3S path this is done through the ECP5 JTAG-SPI bridge,
  so the FPGA can reload the design from flash after reset or power cycle.

## Performance expectations

| Operation | Expected behavior |
| --- | --- |
| Volatile FPGA SRAM programming | Fastest path; best fit for iterating on a design. The tested ULX3S/ECP5 path loaded around 73 KiB/s. |
| Persistent SPI flash write through OpenOCD JTAG-SPI | Much slower because OpenOCD writes flash through the FPGA's JTAG bridge. The tested ULX3S/ECP5 path wrote a roughly 220 KiB bitstream around 3 KiB/s. |

Treat the measured numbers as order-of-magnitude expectations rather than fixed
limits. Adapter speed, Wi-Fi quality, OpenOCD behavior, target flash, and
bitstream size can all change the result.

## v1 Scope

This project is currently a v1 ESPHome wrapper around the upstream
`cmsis_dap_tcp_esp32` component. The wrapper keeps ESPHome responsible for the
device lifecycle while exposing runtime-configured CMSIS-DAP TCP and optional
UART bridge tasks.

- It exposes a CMSIS-DAP TCP server from inside an ESPHome ESP-IDF firmware.
- It can expose an upstream-managed UART bridge over TCP.
- It supports JTAG-only CMSIS-DAP operation in the tested path.
- It supports multiple `cmsis_dap_tcp` YAML instances when they use distinct
  TCP ports and non-overlapping GPIO resources.
- Per-instance runtime config covers JTAG pins, optional `nTRST`/`nRESET`, LED
  pin and polarity, CMSIS-DAP TCP port, keepalive behavior, and low-level timing
  values.
- Per-instance UART bridge config covers TCP port, UART number, TX/RX pins,
  baud rate, data bits, parity, stop bits, keepalive timeout, task stack size,
  and task priority.
- It has no authentication layer.
- ESPHome owns Wi-Fi, logging, OTA, API, and normal device lifecycle.
- OpenOCD owns target-specific programming flows.
- The current tested target path is ULX3S / Lattice ECP5 over OpenOCD
  `cmsis-dap-tcp`.

Things this v1 does not claim yet:

- SWD support.
- CMSIS-DAP UART command support.
- SWO support.
- Authenticated TCP access.
- Generic OTA replacement behavior.
- OpenOCD target/plugin changes.
- Runtime status sensors for client IP, accepted-connection counters, or
  upstream task health beyond task creation.

The upstream component rejects conflicting runtime resources. Two CMSIS-DAP TCP
instances must use different TCP ports and disjoint JTAG/reset/LED GPIOs. UART
bridge instances must also use distinct TCP ports and UART resources.

## Upstream library

The fork (`w531t4/cmsis_dap_tcp_esp32`) tracks the original `bkuschak/cmsis_dap_tcp_esp32` project. Keep
changes shaped so useful pieces can be proposed back upstream.
