// SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
// SPDX-License-Identifier: MIT
#include "cmsis_dap_tcp_component.h"

#include "esphome/core/log.h"

namespace esphome {
namespace cmsis_dap_tcp {

static const char *const TAG = "cmsis_dap_tcp";

void CmsisDapTcpComponent::setup() {
  ESP_LOGI(TAG, "%s", this->message_.c_str());
}

void CmsisDapTcpComponent::dump_config() {
  ESP_LOGCONFIG(TAG, "CMSIS-DAP TCP wrapper:");
  ESP_LOGCONFIG(TAG, "  Message: %s", this->message_.c_str());
}

}  // namespace cmsis_dap_tcp
}  // namespace esphome
