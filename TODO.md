<!--
SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
SPDX-License-Identifier: MIT
-->

# TODO

## 1. [x] v0 Boundary

Status: complete. The v0 boundary is recorded in `README.md`, and the current
component API matches it.

The first useful version should stay deliberately small:

- JTAG only.
  - Resolved by documenting JTAG-only v0 support in `README.md` and keeping the
    component API limited to JTAG pins.
- One CMSIS-DAP TCP instance only.
  - Resolved by documenting single-instance scope in `README.md`; upstream DAP
    state is global, so multiple ports are explicitly out of scope for v0.
- No authentication yet.
  - Resolved by documenting no-auth v0 behavior in `README.md` and not exposing
    any auth fields in the component schema.
- ESPHome owns Wi-Fi, OTA, API, logging, and normal device lifecycle.
  - Resolved by documenting ownership in `README.md`; the wrapper only starts
    the CMSIS-DAP TCP task.
- OpenOCD owns target-specific programming flows.
  - Resolved by documenting that programming commands remain OpenOCD-side.
- The wrapper starts the upstream CMSIS-DAP TCP task and exposes it on a configured TCP port.
  - Resolved by documenting the behavior in `README.md`; the component already
    starts the upstream task and accepts a configured `port`.

## 2. [x] Pin Capability Validation

- Use ESPHome's platform pin validators instead of hardcoded GPIO knowledge.
  - Resolved by using ESPHome validators in the component schema.
- Validate JTAG output pins as output-capable.
  - Resolved for `tck_pin`, `tms_pin`, and `tdi_pin` with `pins.internal_gpio_output_pin_number`.
- Validate TDO as input-capable.
  - Resolved for `tdo_pin` with `pins.internal_gpio_input_pin_number`.
- Keep optional reset pins output-capable.
  - Resolved for `ntrst_pin` and `nreset_pin` with `pins.internal_gpio_output_pin_number`.

## 3. [x] Lock Down The Working Path

- Record the exact OpenOCD commands that prove the bridge works:
  - Basic connectivity and JTAG ID scan.
  - ECP5 volatile SRAM load with `pld load`.
  - ECP5 persistent SPI flash programming with `jtagspi_program`.
  - Optional verify-only command for proving persistent flash contents.
  - Resolution: recorded in `examples/openocd_ulx3s_ecp5.md`.
- Include expected success output snippets:
  - CMSIS-DAP TCP connection.
  - ECP5 tap IDCODE.
  - Flash probe result for the ULX3S SPI flash.
  - `contents match` after verify.
  - Resolution: recorded in `examples/openocd_ulx3s_ecp5.md`..

## 4. [ ] Improve Runtime Visibility

a. [x] Make startup logging obvious:
  - TCP port.
  - TCK/TMS/TDI/TDO pins.
  - Optional reset pins.
  - Task stack size and priority.
  - Task creation success or failure.
  - Resolution: component startup and config logging now include the TCP port,
    JTAG pins, optional reset pins, task stack size, task priority, and task
    creation success or failure.
b. [x] Confirm whether `cmsis_dap_tcp_task` logs are visible through ESPHome logging or only through stdout/stderr.
  - Resolution: source inspection confirms the upstream task writes with
    `fprintf(stdout, ...)`, `fprintf(stderr, ...)`, and `perror(...)`, while its
    `LOG_DEBUG` macro is disabled by default and also writes to `stderr` when
    enabled. These are console/stdout/stderr messages, not ESPHome `ESP_LOG*`
    records, so they should not be expected in ESPHome API logs.
c. [x] Add logging for client connect/disconnect if possible without forking too much upstream code.
  - Resolution: deferred for v0. Upstream already logs connect/disconnect with
    `fprintf(stdout, ...)`, but ESPHome-visible logging would require either
    carrying a local patch or adding an upstream callback/hook. Revisit after
    the wrapper is otherwise stable.
d. [x] Add an easy non-OpenOCD smoke test to the docs:
  - `nc -vz <device-ip> 4441`
  - Expected result: TCP connection succeeds when the task is listening.
  - Resolution: documented the TCP listener smoke test in
    `examples/openocd_ulx3s_ecp5.md`, including the expected success output and
    the limitation that it only proves TCP reachability.
e. [x] Consider adding a lightweight status surface later:
  - Binary sensor for task started.
  - Text sensor for last client IP.
  - Counter for accepted connections.
  - Resolution: deferred for v0. A `task_started` binary sensor is possible
    from the wrapper because it knows whether `xTaskCreate(...)` succeeded, but
    last-client IP and accepted-connection counters require upstream
    callbacks/hooks. Revisit after the wrapper API is stable.

## 5. [ ] Clean Up Dependency Packaging

a. [x] Document the pinned commit and why it was chosen.
  - Resolution: documented the upstream repository, pinned revision, and
    decision to keep the pin in adapter CMake in
    `idf_components/cmsis_dap_tcp_esp32/README.md`.
b. [x] Keep the build reproducible without referencing any local checkout outside this repository.
  - Resolution: source inspection confirmed the ESPHome component registers the
    in-repo adapter path, the adapter fetches upstream into
    `${CMAKE_BINARY_DIR}/cmsis_dap_tcp_esp32_src`, and a repo search found no
    local checkout path references.
c. [x] Revisit the current CMake `git clone` approach after v0:
  - It works around ESP-IDF script-mode restrictions that prevent `FetchContent`.
  - It should fail loudly and clearly when `git` or network access is unavailable.
  - It should avoid unnecessary refetches when the pinned checkout already exists.
  - Resolution: kept the current `execute_process(git clone/fetch/checkout)`
    approach for v0 because it works in ESP-IDF component script mode and fails
    clearly on missing `git`, fetch, checkout, or missing-source errors.
    Avoiding repeated fetches is deferred to post-v0 packaging cleanup.
d. [x] Consider whether a small fork or package mirror is worth it later if upstream remains shaped as a complete ESP-IDF app rather than a reusable component.
  - Resolution: deferred. A fork or package mirror is not needed for v0 because
    the adapter builds against a pinned upstream revision. Future work already
    tracks the preferred next step: proposing an upstream module/component
    layout that preserves the current app build path.

## 6. [ ] Documentation

a. [x] Update the root README with:
  - What this project is.
  - What hardware has been tested.
  - Wiring table for the working setup.
  - ESPHome YAML example.
  - OpenOCD command examples.
  - Current limitations.
  - Resolution: updated `README.md` with the project overview, tested
    hardware, wiring table, ESPHome YAML snippet, OpenOCD proof-doc pointer,
    and current v0 limitations.
b. [x] Document the difference between:
  - Volatile FPGA SRAM programming.
  - Persistent SPI flash programming through JTAG-SPI.
  - Resolution: added a `Programming modes` section to `README.md` explaining
    what volatile SRAM programming does, what persistent SPI flash programming
    does, and why the JTAG-SPI bridge is involved on the tested ECP5 path.
c. [x] Include realistic performance expectations:
  - Volatile programming is much faster.
  - Persistent SPI flash writes through OpenOCD JTAG-SPI may be slow.
  - Resolution: added a `Performance expectations` section to `README.md`
    noting observed volatile SRAM and persistent JTAG-SPI flash write speeds as
    order-of-magnitude expectations rather than fixed limits.
d. [x] Document that v0 has no authentication and should be used only on trusted networks.
  - Resolution: not implemented as a separate documentation change. The v0
    limitations already state that the wrapper has no authentication layer; no
    additional trusted-network warning is being added for now.
e. [x] Later rename it to something more descriptive, such as `examples/jtag_bridge.yaml`.
  - Resolution: not actioned. Keep the current example filename for now to
    avoid churn while the wrapper is still settling.

## 7. [ ] Future Work

- [x] Compare/Constrast how we've implemented referencing the upstream project today vs. the esphome preferred way of implementing using an upstream project
- What portions of the upstream project prevent us from running multiple instances of it in our project? Provide examples of all such situations by thoroughly examining its codebase and providing examples. For each observation, identify its severity and propose solutions.
- Want to be able to program multiple targets attached to esp32
- Want a shared key to protect the endpoints
- Currently, it's unclear that the service is actually alive/healthy from the esphome interface
  - Would be nice to have a button that turns the service on/off
  - Would be nice to show the service health status
  - Would be nice to have a text sensor that shows the origin ip of the last activity

a. Authentication:
  1. Decide whether auth belongs in:
    i. the CMSIS-DAP TCP protocol wrapper
    ii. a separate TCP proxy layer
    iii. an OpenOCD-side extension.
  2. Avoid breaking compatibility with stock OpenOCD until there is a clear plan.
b. Multi-port or multi-target support:
  1. Upstream CMSIS-DAP state is global (where, citations neeed) so two independent JTAG ports are not just two component instances.
  2. Supporting two ports likely requires refactoring the DAP implementation into instance-owned state.
c. Runtime visibility:
  1. Consider proposing upstream callbacks for CMSIS-DAP TCP client connect/disconnect events.
  2. Consider adding ESPHome status sensors once the wrapper can report more
    than task creation state.
d. Upstreamability:
  1. Keep the wrapper small enough that the useful parts can be proposed upstream.
  2. Identify what should live in
    i. ESPHome
    ii. `cmsis_dap_tcp_esp32`
    iii. OpenOCD
  3. Consider proposing an upstream module/component layout that can be consumed
    by ESP-IDF component users without disrupting the project's current app
    build path.
e. Dependency packaging:
  1. [x] Avoid repeated upstream fetches when the pinned checkout already exists in
    the build directory.
      Resolved by using esphome-native repo fetching
