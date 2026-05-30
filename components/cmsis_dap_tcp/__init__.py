# SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
# SPDX-License-Identifier: MIT
from pathlib import Path

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.components import esp32
from esphome.const import CONF_ID, CONF_PORT
from esphome.core import CORE

DEPENDENCIES = ["network"]
CODEOWNERS = ["@w531t4"]

cmsis_dap_tcp_ns = cg.esphome_ns.namespace("cmsis_dap_tcp")
CmsisDapTcpComponent = cmsis_dap_tcp_ns.class_("CmsisDapTcpComponent", cg.Component)

CONF_TCK_PIN = "tck_pin"
CONF_TMS_PIN = "tms_pin"
CONF_TDI_PIN = "tdi_pin"
CONF_TDO_PIN = "tdo_pin"
CONF_NTRST_PIN = "ntrst_pin"
CONF_NRESET_PIN = "nreset_pin"
CONF_PACKET_SIZE = "packet_size"
CONF_KEEPALIVE = "keepalive"
CONF_KEEPALIVE_TIMEOUT = "keepalive_timeout"
CONF_TASK_STACK_SIZE = "task_stack_size"
CONF_TASK_PRIORITY = "task_priority"
CONF_IO_PORT_WRITE_CYCLES = "io_port_write_cycles"
CONF_DELAY_SLOW_CYCLES = "delay_slow_cycles"


def _validate_framework(config):
    if not CORE.is_esp32:
        raise cv.Invalid("cmsis_dap_tcp requires an ESP32 target")
    if CORE.using_arduino:
        raise cv.Invalid("cmsis_dap_tcp requires the ESP-IDF framework")
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
            cv.Optional(CONF_PORT, default=4441): cv.port,
            cv.Optional(CONF_PACKET_SIZE, default=1024): cv.int_range(min=64, max=4096),
            cv.Optional(CONF_KEEPALIVE, default=True): cv.boolean,
            cv.Optional(CONF_KEEPALIVE_TIMEOUT, default=5): cv.int_range(min=1, max=60),
            cv.Optional(CONF_TASK_STACK_SIZE, default=8192): cv.int_range(
                min=4096, max=32768
            ),
            cv.Optional(CONF_TASK_PRIORITY, default=5): cv.int_range(min=0, max=24),
            cv.Optional(CONF_IO_PORT_WRITE_CYCLES, default=2): cv.int_range(
                min=0, max=64
            ),
            cv.Optional(CONF_DELAY_SLOW_CYCLES, default=0): cv.int_range(
                min=0, max=100000
            ),
        }
    ).extend(cv.COMPONENT_SCHEMA),
    _validate_framework,
)


def _define(name, value=1):
    cg.add_build_flag(f"-D{name}={value}")


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    cg.add(var.set_port(config[CONF_PORT]))
    cg.add(var.set_task_stack_size(config[CONF_TASK_STACK_SIZE]))
    cg.add(var.set_task_priority(config[CONF_TASK_PRIORITY]))

    component_root = Path(__file__).resolve().parents[2]
    esp32.add_idf_component(
        name="cmsis_dap_tcp_esp32",
        path=str(component_root / "idf_components" / "cmsis_dap_tcp_esp32"),
    )

    _define("CONFIG_ESP_DAP_JTAG_SUPPORTED")
    _define("CONFIG_ESP_DAP_GPIO_SWCLK_TCK", config[CONF_TCK_PIN])
    _define("CONFIG_ESP_DAP_GPIO_SWDIO_TMS", config[CONF_TMS_PIN])
    _define("CONFIG_ESP_DAP_GPIO_TDI", config[CONF_TDI_PIN])
    _define("CONFIG_ESP_DAP_GPIO_TDO", config[CONF_TDO_PIN])
    _define("CONFIG_ESP_DAP_TCP_PORT", config[CONF_PORT])
    _define("CONFIG_ESP_DAP_TCP_MAX_PKT_SIZE", config[CONF_PACKET_SIZE])
    _define("CONFIG_ESP_DAP_IO_PORT_WRITE_CYCLES", config[CONF_IO_PORT_WRITE_CYCLES])
    _define("CONFIG_ESP_DAP_DELAY_SLOW_CYCLES", config[CONF_DELAY_SLOW_CYCLES])

    if CONF_NTRST_PIN in config:
        _define("CONFIG_ESP_DAP_NTRST_SUPPORTED")
        _define("CONFIG_ESP_DAP_GPIO_NTRST", config[CONF_NTRST_PIN])

    if CONF_NRESET_PIN in config:
        _define("CONFIG_ESP_DAP_NRESET_SUPPORTED")
        _define("CONFIG_ESP_DAP_GPIO_NRESET", config[CONF_NRESET_PIN])

    if config[CONF_KEEPALIVE]:
        _define("CONFIG_ESP_DAP_TCP_USE_KEEPALIVE")
        _define("CONFIG_ESP_DAP_TCP_KEEPALIVE_TIMEOUT", config[CONF_KEEPALIVE_TIMEOUT])
