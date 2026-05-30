<!--
SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
SPDX-License-Identifier: MIT
-->
# ESP-IDF install

https://docs.espressif.com/projects/esp-idf/en/stable/esp32/get-started/linux-macos-setup-legacy.html

1. mkdir -p ~/esp
1. cd ~/esp
1. git clone -b v5.3.2 --recursive https://github.com/espressif/esp-idf.git
1. cd ~/esp/esp-idf
1. ./install.sh esp32
1. . $HOME/esp/esp-idf/export.sh

# project url
https://github.com/bkuschak/cmsis_dap_tcp_esp32

[13:52:26.377][I][app:154]: ESPHome version 2026.4.5 compiled on 2026-05-20 12:19:35 -0400
[13:52:26.377][I][app:161]: ESP32 Chip: ESP32 rev3.1, 2 core(s)
[13:52:26.398][C][wifi:1505]:   Local MAC: D8:BC:38:D5:F1:10
[13:52:26.427][C][wifi:1216]:   IP Address: 192.168.2.175
[13:52:26.427][C][wifi:1227]:   Hostname: 'esphome-web-d5f110'

# build firmware
used default sdkconfig

idf.py fullclean menuconfig
update wifi ssid/creds
    CONFIG_ESP_DAP_GPIO_SWCLK_TCK=18
    CONFIG_ESP_DAP_GPIO_SWDIO_TMS=5
    CONFIG_ESP_DAP_GPIO_TDI=23
    CONFIG_ESP_DAP_GPIO_TDO=34
    CONFIG_ESP_UART_BRIDGE_ENABLED=y
    CONFIG_ESP_UART_BRIDGE_TCP_PORT=4442
    CONFIG_ESP_UART_BRIDGE_USE_KEEPALIVE=y
    CONFIG_ESP_UART_BRIDGE_KEEPALIVE_TIMEOUT=10
    CONFIG_ESP_UART_BRIDGE_UART_NUM=1
    CONFIG_ESP_UART_BRIDGE_REMAP_PINS=y
    CONFIG_ESP_UART_BRIDGE_TXD_PIN=25
    CONFIG_ESP_UART_BRIDGE_RXD_PIN=26
    CONFIG_ESP_UART_BRIDGE_BAUD_RATE=115200
    CONFIG_ESP_UART_BRIDGE_DATA_BITS=8
    CONFIG_ESP_UART_BRIDGE_PARITY_NONE=y
    # CONFIG_ESP_UART_BRIDGE_PARITY_EVEN is not set
    # CONFIG_ESP_UART_BRIDGE_PARITY_ODD is not set
    CONFIG_ESP_UART_BRIDGE_STOP_BITS=1
idf.py build flash
# build openocd
git clone git://git.code.sf.net/p/openocd/code openocd
cd openocd
./bootstrap
./configure --disable-werror
make -j4


# write config file to tcl/interface/cmsis-dap-tcp.cfg

tcl/interface/cmsis_dap_tcp.cfg configuration file to point to your ESP32's IP address:

adapter driver cmsis-dap
cmsis-dap backend tcp
cmsis-dap tcp host 192.168.2.175
cmsis-dap tcp port 4441
transport select jtag
reset_config none

# run openocd
./src/openocd --search tcl \
              -f tcl/interface/cmsis-dap-tcp.cfg \
              -f tcl/target/stm32f1x.cfg \
              -c "program firmware.elf verify reset exit"

./src/openocd --search tcl \
              -f tcl/interface/cmsis-dap-tcp.cfg \
              -f tcl/fpga/lattice_ecp5.cfg \
              -c "program ulx3s.bit verify reset exit"


# this works
./src/openocd -s tcl \
  -f interface/cmsis-dap-tcp.cfg \
  -c "cmsis-dap tcp host 192.168.2.175" \
  -c "cmsis-dap tcp port 4441" \
  -c "transport select jtag" \
  -f fpga/lattice_ecp5.cfg \

  -c "init; scan_chain; lattice read_status ecp5.pld; shutdown"

should show something like

Info : JTAG tap: ecp5.tap tap/device found: 0x21111043 (mfg: 0x021 (Lattice Semi.), part: 0x1111, ver: 0x2)

./src/openocd -s tcl \
  -f interface/cmsis-dap-tcp.cfg \
  -c "cmsis-dap tcp host 192.168.2.175" \
  -c "cmsis-dap tcp port 4441" \
  -c "transport select jtag" \
  -f fpga/lattice_ecp5.cfg \
  -c "init" \
  -c "pld devices" \
  -c "lattice read_user ecp5.pld" \
  -c "shutdown"

should show something like
0xfffffffe

# programming sram -- non-persistent
./src/openocd -s tcl \
  -f interface/cmsis-dap-tcp.cfg \
  -c "cmsis-dap tcp host 192.168.2.175" \
  -c "cmsis-dap tcp port 4441" \
  -c "transport select jtag" \
  -f fpga/lattice_ecp5.cfg \
  -c "adapter speed 1000" \
  -c "init" \
  -c "pld load ecp5.pld ../../fpga_led_display/ulx3s-12f.bit" \
  -c "shutdown"

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


# this will persist + display output at each stage

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

# compiling code
uvx --python 3.13 esphome run examples/vanilla.yaml

x --python 3.13 esphome run examples/vanilla.yaml --device /dev/ttyUSB0