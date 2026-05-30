# SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
# SPDX-License-Identifier: MIT

set(CMSIS_DAP_TCP_ESP32_GIT_REPOSITORY
    "https://github.com/bkuschak/cmsis_dap_tcp_esp32.git"
    CACHE STRING "Remote repository for bkuschak/cmsis_dap_tcp_esp32")
set(CMSIS_DAP_TCP_ESP32_GIT_TAG
    "6764a14e1de9c96eec40fc7aa723e2ab6d8f9595"
    CACHE STRING "Git ref for bkuschak/cmsis_dap_tcp_esp32")

find_program(GIT_EXECUTABLE git REQUIRED)

set(CMSIS_DAP_TCP_ESP32_SOURCE_DIR
    "${CMAKE_BINARY_DIR}/cmsis_dap_tcp_esp32_src")

if(NOT EXISTS "${CMSIS_DAP_TCP_ESP32_SOURCE_DIR}/.git")
    execute_process(
        COMMAND "${GIT_EXECUTABLE}" clone
            "${CMSIS_DAP_TCP_ESP32_GIT_REPOSITORY}"
            "${CMSIS_DAP_TCP_ESP32_SOURCE_DIR}"
        RESULT_VARIABLE CMSIS_DAP_TCP_ESP32_CLONE_RESULT
    )
    if(NOT CMSIS_DAP_TCP_ESP32_CLONE_RESULT EQUAL 0)
        message(FATAL_ERROR
            "Failed to clone ${CMSIS_DAP_TCP_ESP32_GIT_REPOSITORY}")
    endif()
endif()

execute_process(
    COMMAND "${GIT_EXECUTABLE}" fetch --all --tags
    WORKING_DIRECTORY "${CMSIS_DAP_TCP_ESP32_SOURCE_DIR}"
    RESULT_VARIABLE CMSIS_DAP_TCP_ESP32_FETCH_RESULT
)
if(NOT CMSIS_DAP_TCP_ESP32_FETCH_RESULT EQUAL 0)
    message(FATAL_ERROR
        "Failed to fetch ${CMSIS_DAP_TCP_ESP32_GIT_REPOSITORY}")
endif()

execute_process(
    COMMAND "${GIT_EXECUTABLE}" checkout --detach "${CMSIS_DAP_TCP_ESP32_GIT_TAG}"
    WORKING_DIRECTORY "${CMSIS_DAP_TCP_ESP32_SOURCE_DIR}"
    RESULT_VARIABLE CMSIS_DAP_TCP_ESP32_CHECKOUT_RESULT
)
if(NOT CMSIS_DAP_TCP_ESP32_CHECKOUT_RESULT EQUAL 0)
    message(FATAL_ERROR
        "Failed to checkout ${CMSIS_DAP_TCP_ESP32_GIT_TAG} from "
        "${CMSIS_DAP_TCP_ESP32_GIT_REPOSITORY}")
endif()

set(CMSIS_DAP_TCP_ESP32_MAIN "${CMSIS_DAP_TCP_ESP32_SOURCE_DIR}/main")

if(NOT EXISTS "${CMSIS_DAP_TCP_ESP32_MAIN}/DAP.c")
    message(FATAL_ERROR
        "Fetched bkuschak/cmsis_dap_tcp_esp32, but did not find main/DAP.c")
endif()

idf_component_register(
    SRCS
        "${CMSIS_DAP_TCP_ESP32_MAIN}/DAP.c"
        "${CMSIS_DAP_TCP_ESP32_MAIN}/DAP_vendor.c"
        "${CMSIS_DAP_TCP_ESP32_MAIN}/JTAG_DP.c"
        "${CMSIS_DAP_TCP_ESP32_MAIN}/SWO.c"
        "${CMSIS_DAP_TCP_ESP32_MAIN}/SW_DP.c"
        "${CMSIS_DAP_TCP_ESP32_MAIN}/UART.c"
        "${CMSIS_DAP_TCP_ESP32_MAIN}/cmsis_dap_tcp.c"
    INCLUDE_DIRS
        "${CMSIS_DAP_TCP_ESP32_MAIN}"
    REQUIRES
        driver
        lwip
        esp_event
        esp_timer
        esp_wifi
        nvs_flash
    PRIV_REQUIRES
        spi_flash
)
