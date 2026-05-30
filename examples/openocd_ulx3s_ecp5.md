<!--
SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
SPDX-License-Identifier: MIT
-->

# OpenOCD proof path: ULX3S / ECP5

These commands assume:

- The ESPHome node is running `examples/vanilla.yaml`.
- The CMSIS-DAP TCP server is reachable at `192.168.2.175:4441`.
- Commands are run from an OpenOCD checkout root.
- The ECP5 target config is available as `tcl/fpga/lattice_ecp5.cfg`.

Adjust the IP address, port, and bitstream paths for your setup.

## TCP listener smoke test

Before running OpenOCD, confirm the CMSIS-DAP TCP port accepts a connection:

```sh
nc -vz 192.168.2.175 4441
```

Expected proof:

```text
Connection to 192.168.2.175 4441 port [tcp/*] succeeded!
```

This only proves that the ESP32 accepted a TCP connection. It does not prove
JTAG wiring, target detection, or programming.

If `examples/vanilla.yaml` has `uart_bridge` enabled, the UART bridge TCP port
can be checked separately:

```sh
nc 192.168.2.175 4442
```

This connects to the UART bridge port, not OpenOCD. Typed bytes are forwarded
to the configured UART TX pin. Bytes received on the configured UART RX pin are
sent back to the TCP client when the connected target transmits serial output.

## JTAG scan

```sh
./src/openocd -s tcl \
  -f interface/cmsis-dap-tcp.cfg \
  -c "cmsis-dap tcp host 192.168.2.175" \
  -c "cmsis-dap tcp port 4441" \
  -c "transport select jtag" \
  -f fpga/lattice_ecp5.cfg \
  -c "init; scan_chain; shutdown"
```

Expected proof:

```text
Info : CMSIS-DAP: Connecting to 192.168.2.175:4441 using TCP backend
Info : JTAG tap: ecp5.tap tap/device found: 0x21111043 (mfg: 0x021 (Lattice Semi.), part: 0x1111, ver: 0x2)
```

## Volatile SRAM load

This loads the FPGA bitstream into SRAM. It does not persist across power loss.

```sh
./src/openocd -s tcl \
  -f interface/cmsis-dap-tcp.cfg \
  -c "cmsis-dap tcp host 192.168.2.175" \
  -c "cmsis-dap tcp port 4441" \
  -c "transport select jtag" \
  -f fpga/lattice_ecp5.cfg \
  -c "adapter speed 4000" \
  -c "init" \
  -c "pld load ecp5.pld ../../fpga_led_display/ulx3s-without-passthru-12f.bit" \
  -c "shutdown"
```

Expected proof:

```text
Info : CMSIS-DAP: Connecting to 192.168.2.175:4441 using TCP backend
Info : JTAG tap: ecp5.tap tap/device found: 0x21111043 (mfg: 0x021 (Lattice Semi.), part: 0x1111, ver: 0x2)
Info : part found: LFE5U-12F-6CABGA381
```

## Persistent SPI flash programming

This writes the bitstream to the SPI flash behind the ECP5 JTAG-SPI bridge.

```sh
./src/openocd -d2 -s tcl \
  -f interface/cmsis-dap-tcp.cfg \
  -c "cmsis-dap tcp host 192.168.2.175" \
  -c "cmsis-dap tcp port 4441" \
  -c "transport select jtag" \
  -c "adapter speed 4000" \
  -f fpga/lattice_ecp5.cfg \
  -c "set JTAGSPI_CHAIN_ID ecp5.pld" \
  -f cpld/jtagspi.cfg \
  -c "init" \
  -c "jtagspi_init ecp5.pld \"\" -1" \
  -c "echo START_WRITE" \
  -c "flash write_image erase ../../fpga_led_display/ulx3s-12f.bit 0" \
  -c "echo START_VERIFY" \
  -c "flash verify_bank ecp5.spi ../../fpga_led_display/ulx3s-12f.bit 0" \
  -c "echo DONE" \
  -c "shutdown"
```

Expected proof:

```text
Info : Found flash device 'issi is25lp128d' (ID 0x18609d)
flash 'jtagspi' found at 0x00000000
START_WRITE
START_VERIFY
contents match
DONE
```

## Verify-only persistent flash contents

Use this when you want proof that flash contents still match the bitstream
without rewriting flash.

```sh
./src/openocd -d2 -s tcl \
  -f interface/cmsis-dap-tcp.cfg \
  -c "cmsis-dap tcp host 192.168.2.175" \
  -c "cmsis-dap tcp port 4441" \
  -c "transport select jtag" \
  -c "adapter speed 4000" \
  -f fpga/lattice_ecp5.cfg \
  -c "set JTAGSPI_CHAIN_ID ecp5.pld" \
  -f cpld/jtagspi.cfg \
  -c "init" \
  -c "jtagspi_init ecp5.pld \"\" -1" \
  -c "flash verify_bank ecp5.spi ../../fpga_led_display/ulx3s-12f.bit 0" \
  -c "shutdown"
```

Expected proof:

```text
Info : Found flash device 'issi is25lp128d' (ID 0x18609d)
contents match
```
