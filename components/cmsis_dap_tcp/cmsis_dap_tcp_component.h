// SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
// SPDX-License-Identifier: MIT
#pragma once

#include "esphome/core/component.h"

#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

namespace esphome {
namespace cmsis_dap_tcp {

class CmsisDapTcpComponent : public Component {
 public:
  void setup() override;
  void dump_config() override;
  float get_setup_priority() const override;

  void set_port(uint16_t port) { this->port_ = port; }
  void set_task_stack_size(uint32_t task_stack_size) { this->task_stack_size_ = task_stack_size; }
  void set_task_priority(uint8_t task_priority) { this->task_priority_ = task_priority; }

 protected:
  uint16_t port_{0};
  uint32_t task_stack_size_{8192};
  uint8_t task_priority_{5};
  TaskHandle_t task_handle_{nullptr};
};

}  // namespace cmsis_dap_tcp
}  // namespace esphome
