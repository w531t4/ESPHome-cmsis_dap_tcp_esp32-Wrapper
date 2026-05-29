# SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
# SPDX-License-Identifier: MIT
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID

CODEOWNERS = []

cmsis_dap_tcp_ns = cg.esphome_ns.namespace("cmsis_dap_tcp")
CmsisDapTcpComponent = cmsis_dap_tcp_ns.class_("CmsisDapTcpComponent", cg.Component)

CONF_MESSAGE = "message"

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(CmsisDapTcpComponent),
        cv.Optional(CONF_MESSAGE, default="vanilla external component loaded"): cv.string,
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    cg.add(var.set_message(config[CONF_MESSAGE]))
