# SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
# SPDX-License-Identifier: MIT
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.components import esp32
from esphome.const import CONF_ID, CONF_PORT
from esphome.core import CORE

DEPENDENCIES = ["network"]
CODEOWNERS = ["@w531t4"]

IDF_COMPONENT_REPO = "https://github.com/w531t4/cmsis_dap_tcp_esp32.git"
IDF_COMPONENT_REF = "v1.0.0"
IDF_COMPONENT_PATH = "main"

cmsis_dap_tcp_ns = cg.esphome_ns.namespace("cmsis_dap_tcp")
CmsisDapTcpComponent = cmsis_dap_tcp_ns.class_("CmsisDapTcpComponent", cg.Component)

MULTI_CONF = True

CONF_COMPONENT_STATE = "cmsis_dap_tcp"
STATE_IDF_COMPONENT_ADDED = "idf_component_added"
STATE_BASE_SDKCONFIG_SET = "base_sdkconfig_set"
STATE_UART_BRIDGE_SDKCONFIG_SET = "uart_bridge_sdkconfig_set"

CONF_TCK_PIN = "tck_pin"
CONF_TMS_PIN = "tms_pin"
CONF_TDI_PIN = "tdi_pin"
CONF_TDO_PIN = "tdo_pin"
CONF_NTRST_PIN = "ntrst_pin"
CONF_NRESET_PIN = "nreset_pin"
CONF_LED_PIN = "led_pin"
CONF_LED_ACTIVE_HIGH = "led_active_high"
CONF_UART_BRIDGE = "uart_bridge"
CONF_UART_NUM = "uart_num"
CONF_TX_PIN = "tx_pin"
CONF_RX_PIN = "rx_pin"
CONF_BAUD_RATE = "baud_rate"
CONF_DATA_BITS = "data_bits"
CONF_PARITY = "parity"
CONF_STOP_BITS = "stop_bits"
CONF_PACKET_SIZE = "packet_size"
CONF_KEEPALIVE = "keepalive"
CONF_KEEPALIVE_TIMEOUT = "keepalive_timeout"
CONF_TASK_STACK_SIZE = "task_stack_size"
CONF_TASK_PRIORITY = "task_priority"
CONF_UART_BRIDGE_TASK_STACK_SIZE = "uart_bridge_task_stack_size"
CONF_UART_BRIDGE_TASK_PRIORITY = "uart_bridge_task_priority"
CONF_IO_PORT_WRITE_CYCLES = "io_port_write_cycles"
CONF_DELAY_SLOW_CYCLES = "delay_slow_cycles"

UART_DATA_BITS = {
    7: 7,
    8: 8,
}

UART_PARITY = {
    "NONE": 0,
    "EVEN": 2,
    "ODD": 3,
}

UART_STOP_BITS = {
    1: 1,
    2: 2,
}


def _validate_framework(config):
    if not CORE.is_esp32:
        raise cv.Invalid("cmsis_dap_tcp requires an ESP32 target")
    if CORE.using_arduino:
        raise cv.Invalid("cmsis_dap_tcp requires the ESP-IDF framework")
    return config


def _validate_config(config):
    if CONF_UART_BRIDGE not in config:
        return config

    uart_bridge = config[CONF_UART_BRIDGE]
    if uart_bridge[CONF_PORT] == config[CONF_PORT]:
        raise cv.Invalid("UART bridge port must be different from CMSIS-DAP TCP port")

    return config


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(CmsisDapTcpComponent),
            cv.Required(CONF_TCK_PIN): pins.internal_gpio_output_pin_number,
            cv.Required(CONF_TMS_PIN): pins.internal_gpio_output_pin_number,
            cv.Required(CONF_TDI_PIN): pins.internal_gpio_output_pin_number,
            cv.Required(CONF_TDO_PIN): pins.internal_gpio_input_pin_number,
            cv.Optional(CONF_NTRST_PIN): pins.internal_gpio_output_pin_number,
            cv.Optional(CONF_NRESET_PIN): pins.internal_gpio_output_pin_number,
            cv.Optional(CONF_LED_PIN): pins.internal_gpio_output_pin_number,
            cv.Optional(CONF_LED_ACTIVE_HIGH, default=False): cv.boolean,
            cv.Optional(CONF_UART_BRIDGE): cv.Schema(
                {
                    cv.Required(CONF_TX_PIN): pins.internal_gpio_output_pin_number,
                    cv.Required(CONF_RX_PIN): pins.internal_gpio_input_pin_number,
                    cv.Optional(CONF_PORT, default=4442): cv.port,
                    cv.Optional(CONF_UART_NUM, default=1): cv.int_range(min=0, max=2),
                    cv.Optional(CONF_BAUD_RATE, default=115200): cv.int_range(
                        min=300, max=4000000
                    ),
                    cv.Optional(CONF_DATA_BITS, default=8): cv.one_of(7, 8, int=True),
                    cv.Optional(CONF_PARITY, default="NONE"): cv.one_of(
                        "NONE", "EVEN", "ODD", upper=True
                    ),
                    cv.Optional(CONF_STOP_BITS, default=1): cv.one_of(1, 2, int=True),
                    cv.Optional(CONF_KEEPALIVE, default=True): cv.boolean,
                    cv.Optional(CONF_KEEPALIVE_TIMEOUT, default=10): cv.int_range(
                        min=1, max=60
                    ),
                    cv.Optional(
                        CONF_UART_BRIDGE_TASK_STACK_SIZE, default=4096
                    ): cv.int_range(min=4096, max=32768),
                    cv.Optional(CONF_UART_BRIDGE_TASK_PRIORITY, default=5): cv.int_range(
                        min=0, max=24
                    ),
                }
            ),
            cv.Optional(CONF_PORT, default=4441): cv.port,
            cv.Optional(CONF_PACKET_SIZE, default=1024): cv.int_range(min=64, max=4096),
            cv.Optional(CONF_KEEPALIVE, default=True): cv.boolean,
            cv.Optional(CONF_KEEPALIVE_TIMEOUT, default=5): cv.int_range(min=1, max=60),
            cv.Optional(CONF_TASK_STACK_SIZE, default=8192): cv.int_range(
                min=4096, max=32768
            ),
            cv.Optional(CONF_TASK_PRIORITY, default=5): cv.int_range(min=0, max=24),
            cv.Optional(CONF_IO_PORT_WRITE_CYCLES, default=72): cv.int_range(
                min=0, max=100000
            ),
            cv.Optional(CONF_DELAY_SLOW_CYCLES, default=5): cv.int_range(
                min=0, max=100000
            ),
        }
    ).extend(cv.COMPONENT_SCHEMA),
    _validate_framework,
    _validate_config,
)


def _sdkconfig(name, value):
    esp32.add_idf_sdkconfig_option(name, value)


def _state():
    return CORE.data.setdefault(CONF_COMPONENT_STATE, {})


def _add_idf_component_once():
    state = _state()
    if state.get(STATE_IDF_COMPONENT_ADDED):
        return
    esp32.add_idf_component(
        name="cmsis_dap_tcp_esp32",
        repo=IDF_COMPONENT_REPO,
        ref=IDF_COMPONENT_REF,
        path=IDF_COMPONENT_PATH,
    )
    state[STATE_IDF_COMPONENT_ADDED] = True


def _set_base_sdkconfig_once(config):
    state = _state()
    if state.get(STATE_BASE_SDKCONFIG_SET):
        return

    _sdkconfig("CONFIG_ESP_DAP_JTAG_SUPPORTED", True)
    _sdkconfig("CONFIG_ESP_DAP_SWD_SUPPORTED", False)
    _sdkconfig("CONFIG_ESP_DAP_LED_SUPPORTED", True)
    _sdkconfig("CONFIG_ESP_DAP_JTAG_NTRST_SUPPORTED", True)
    _sdkconfig("CONFIG_ESP_DAP_NRESET_SUPPORTED", True)
    _sdkconfig("CONFIG_ESP_DAP_GPIO_SWCLK_TCK", config[CONF_TCK_PIN])
    _sdkconfig("CONFIG_ESP_DAP_GPIO_SWDIO_TMS", config[CONF_TMS_PIN])
    _sdkconfig("CONFIG_ESP_DAP_GPIO_TDI", config[CONF_TDI_PIN])
    _sdkconfig("CONFIG_ESP_DAP_GPIO_TDO", config[CONF_TDO_PIN])
    _sdkconfig("CONFIG_ESP_DAP_TCP_PORT", config[CONF_PORT])
    _sdkconfig("CONFIG_ESP_DAP_TCP_MAX_PKT_SIZE", config[CONF_PACKET_SIZE])
    _sdkconfig("CONFIG_ESP_DAP_TCP_USE_KEEPALIVE", config[CONF_KEEPALIVE])
    _sdkconfig("CONFIG_ESP_DAP_IO_PORT_WRITE_CYCLES", config[CONF_IO_PORT_WRITE_CYCLES])
    _sdkconfig("CONFIG_ESP_DAP_DELAY_SLOW_CYCLES", config[CONF_DELAY_SLOW_CYCLES])
    # Wrapper instances pass LED pin/polarity through runtime gpio_config.
    # Keep the compile-time fallback disabled so the first instance does not
    # accidentally define a global LED for every instance.
    _sdkconfig("CONFIG_ESP_DAP_GPIO_LED", -1)
    _sdkconfig("CONFIG_ESP_DAP_LED_ACTIVE_HIGH", False)
    _sdkconfig("CONFIG_ESP_DAP_LED_ACTIVE_LOW", True)
    if CONF_NTRST_PIN in config:
        _sdkconfig("CONFIG_ESP_DAP_GPIO_NTRST", config[CONF_NTRST_PIN])
    if CONF_NRESET_PIN in config:
        _sdkconfig("CONFIG_ESP_DAP_GPIO_NRESET", config[CONF_NRESET_PIN])
    if config[CONF_KEEPALIVE]:
        _sdkconfig(
            "CONFIG_ESP_DAP_TCP_KEEPALIVE_TIMEOUT", config[CONF_KEEPALIVE_TIMEOUT]
        )

    state[STATE_BASE_SDKCONFIG_SET] = True


def _set_uart_bridge_sdkconfig_once(uart_bridge):
    state = _state()
    if state.get(STATE_UART_BRIDGE_SDKCONFIG_SET):
        return

    _sdkconfig("CONFIG_ESP_UART_BRIDGE_ENABLED", True)
    _sdkconfig("CONFIG_ESP_UART_BRIDGE_TCP_PORT", uart_bridge[CONF_PORT])
    _sdkconfig("CONFIG_ESP_UART_BRIDGE_USE_KEEPALIVE", uart_bridge[CONF_KEEPALIVE])
    _sdkconfig("CONFIG_ESP_UART_BRIDGE_UART_NUM", uart_bridge[CONF_UART_NUM])
    _sdkconfig("CONFIG_ESP_UART_BRIDGE_REMAP_PINS", True)
    _sdkconfig("CONFIG_ESP_UART_BRIDGE_TXD_PIN", uart_bridge[CONF_TX_PIN])
    _sdkconfig("CONFIG_ESP_UART_BRIDGE_RXD_PIN", uart_bridge[CONF_RX_PIN])
    _sdkconfig("CONFIG_ESP_UART_BRIDGE_BAUD_RATE", uart_bridge[CONF_BAUD_RATE])
    _sdkconfig("CONFIG_ESP_UART_BRIDGE_DATA_BITS", uart_bridge[CONF_DATA_BITS])
    _sdkconfig("CONFIG_ESP_UART_BRIDGE_STOP_BITS", uart_bridge[CONF_STOP_BITS])
    _sdkconfig("CONFIG_ESP_UART_BRIDGE_PARITY_NONE", uart_bridge[CONF_PARITY] == "NONE")
    _sdkconfig("CONFIG_ESP_UART_BRIDGE_PARITY_EVEN", uart_bridge[CONF_PARITY] == "EVEN")
    _sdkconfig("CONFIG_ESP_UART_BRIDGE_PARITY_ODD", uart_bridge[CONF_PARITY] == "ODD")
    _sdkconfig("CONFIG_VFS_SUPPORT_SELECT", True)
    if uart_bridge[CONF_KEEPALIVE]:
        _sdkconfig(
            "CONFIG_ESP_UART_BRIDGE_KEEPALIVE_TIMEOUT",
            uart_bridge[CONF_KEEPALIVE_TIMEOUT],
        )

    state[STATE_UART_BRIDGE_SDKCONFIG_SET] = True


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    cg.add(var.set_port(config[CONF_PORT]))
    cg.add(var.set_tck_pin(config[CONF_TCK_PIN]))
    cg.add(var.set_tms_pin(config[CONF_TMS_PIN]))
    cg.add(var.set_tdi_pin(config[CONF_TDI_PIN]))
    cg.add(var.set_tdo_pin(config[CONF_TDO_PIN]))
    cg.add(var.set_task_stack_size(config[CONF_TASK_STACK_SIZE]))
    cg.add(var.set_task_priority(config[CONF_TASK_PRIORITY]))
    cg.add(var.set_keepalive(config[CONF_KEEPALIVE]))
    cg.add(var.set_keepalive_timeout(config[CONF_KEEPALIVE_TIMEOUT]))
    cg.add(var.set_io_port_write_cycles(config[CONF_IO_PORT_WRITE_CYCLES]))
    cg.add(var.set_delay_slow_cycles(config[CONF_DELAY_SLOW_CYCLES]))
    cg.add(var.set_led_active_high(config[CONF_LED_ACTIVE_HIGH]))

    _add_idf_component_once()
    _set_base_sdkconfig_once(config)

    if CONF_UART_BRIDGE in config:
        uart_bridge = config[CONF_UART_BRIDGE]
        cg.add(var.set_uart_bridge_enabled(True))
        cg.add(var.set_uart_bridge_port(uart_bridge[CONF_PORT]))
        cg.add(var.set_uart_bridge_keepalive_timeout(
            uart_bridge[CONF_KEEPALIVE_TIMEOUT] if uart_bridge[CONF_KEEPALIVE] else 0
        ))
        cg.add(var.set_uart_num(uart_bridge[CONF_UART_NUM]))
        cg.add(var.set_uart_tx_pin(uart_bridge[CONF_TX_PIN]))
        cg.add(var.set_uart_rx_pin(uart_bridge[CONF_RX_PIN]))
        cg.add(var.set_uart_baud_rate(uart_bridge[CONF_BAUD_RATE]))
        cg.add(var.set_uart_data_bits(UART_DATA_BITS[uart_bridge[CONF_DATA_BITS]]))
        cg.add(var.set_uart_parity(UART_PARITY[uart_bridge[CONF_PARITY]]))
        cg.add(var.set_uart_stop_bits(UART_STOP_BITS[uart_bridge[CONF_STOP_BITS]]))
        cg.add(
            var.set_uart_bridge_task_stack_size(
                uart_bridge[CONF_UART_BRIDGE_TASK_STACK_SIZE]
            )
        )
        cg.add(
            var.set_uart_bridge_task_priority(
                uart_bridge[CONF_UART_BRIDGE_TASK_PRIORITY]
            )
        )
        _set_uart_bridge_sdkconfig_once(uart_bridge)

    if CONF_NTRST_PIN in config:
        cg.add(var.set_ntrst_pin(config[CONF_NTRST_PIN]))

    if CONF_NRESET_PIN in config:
        cg.add(var.set_nreset_pin(config[CONF_NRESET_PIN]))

    if CONF_LED_PIN in config:
        cg.add(var.set_led_pin(config[CONF_LED_PIN]))
