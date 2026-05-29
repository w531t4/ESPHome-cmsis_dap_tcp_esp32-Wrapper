// SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
// SPDX-License-Identifier: MIT
#pragma once

#include "esphome/core/component.h"

#include <string>

namespace esphome {
namespace cmsis_dap_tcp {

class CmsisDapTcpComponent : public Component {
 public:
  void setup() override;
  void dump_config() override;

  void set_message(const std::string &message) { this->message_ = message; }

 protected:
  std::string message_;
};

}  // namespace cmsis_dap_tcp
}  // namespace esphome
