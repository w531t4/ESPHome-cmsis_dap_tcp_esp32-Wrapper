// SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
// SPDX-License-Identifier: MIT
#include "cmsis_dap_tcp_component.h"

#include "esphome/core/log.h"

#include <inttypes.h>

extern "C" {
#include "DAP.h"
#include "cmsis_dap_tcp.h"
}

namespace esphome {
namespace cmsis_dap_tcp {

static const char *const TAG = "cmsis_dap_tcp";

void CmsisDapTcpComponent::setup() {
  ESP_LOGI(TAG, "Starting CMSIS-DAP TCP server on port %u", this->port_);

  DAP_Setup();

  const BaseType_t result =
      xTaskCreate(cmsis_dap_tcp_task, "cmsis_dap_tcp", this->task_stack_size_, nullptr, this->task_priority_,
                  &this->task_handle_);
  if (result != pdPASS) {
    ESP_LOGE(TAG, "Failed to start CMSIS-DAP TCP task");
    this->mark_failed();
  }
}

void CmsisDapTcpComponent::dump_config() {
  ESP_LOGCONFIG(TAG, "CMSIS-DAP TCP:");
  ESP_LOGCONFIG(TAG, "  Port: %u", this->port_);
  ESP_LOGCONFIG(TAG, "  Task stack size: %" PRIu32, this->task_stack_size_);
  ESP_LOGCONFIG(TAG, "  Task priority: %u", this->task_priority_);
}

float CmsisDapTcpComponent::get_setup_priority() const { return setup_priority::AFTER_WIFI; }

}  // namespace cmsis_dap_tcp
}  // namespace esphome
