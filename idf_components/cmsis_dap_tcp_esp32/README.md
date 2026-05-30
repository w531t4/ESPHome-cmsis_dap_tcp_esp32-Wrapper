<!--
SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
SPDX-License-Identifier: MIT
-->

# cmsis_dap_tcp_esp32 adapter

This is an ESP-IDF component adapter for `bkuschak/cmsis_dap_tcp_esp32`.

The upstream project is currently shaped as a complete ESP-IDF app, and its
`main/CMakeLists.txt` includes `main.c`. ESPHome already owns Wi-Fi and app
startup, so this adapter builds only the CMSIS-DAP engine and TCP server source
files.

The adapter fetches the upstream repository during CMake configuration with
`git`:

`https://github.com/bkuschak/cmsis_dap_tcp_esp32.git`

The fetched revision is pinned in `CMakeLists.txt` with
`CMSIS_DAP_TCP_ESP32_GIT_TAG`. The checkout is placed under the ESPHome/IDF
build directory, not next to this repository.
