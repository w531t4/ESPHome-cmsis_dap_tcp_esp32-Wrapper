// SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
// SPDX-License-Identifier: MIT
#pragma once

#include "esphome/components/switch/switch.h"
#include "esphome/core/component.h"

#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <stdint.h>

namespace esphome {
namespace cmsis_dap_tcp {

class CmsisDapTcpServiceSwitch;
class UartBridgeServiceSwitch;

}  // namespace cmsis_dap_tcp
}  // namespace esphome

extern "C" {
struct cmsis_dap_gpio_config;
struct cmsis_dap_tcp_config;
struct uart_bridge_config;
}

namespace esphome {
namespace cmsis_dap_tcp {

class CmsisDapTcpComponent : public Component {
 public:
  void setup() override;
  void dump_config() override;
  float get_setup_priority() const override;

  void set_port(uint16_t port) { this->port_ = port; }
  void set_tck_pin(uint8_t pin) { this->tck_pin_ = pin; }
  void set_tms_pin(uint8_t pin) { this->tms_pin_ = pin; }
  void set_tdi_pin(uint8_t pin) { this->tdi_pin_ = pin; }
  void set_tdo_pin(uint8_t pin) { this->tdo_pin_ = pin; }
  void set_ntrst_pin(uint8_t pin) { this->ntrst_pin_ = pin; }
  void set_nreset_pin(uint8_t pin) { this->nreset_pin_ = pin; }
  void set_led_pin(uint8_t pin) { this->led_pin_ = pin; }
  void set_led_active_high(bool active_high) { this->led_active_high_ = active_high; }
  void set_task_stack_size(uint32_t task_stack_size) { this->task_stack_size_ = task_stack_size; }
  void set_task_priority(uint8_t task_priority) { this->task_priority_ = task_priority; }
  void set_keepalive(bool keepalive) { this->keepalive_ = keepalive; }
  void set_keepalive_timeout(uint16_t keepalive_timeout) { this->keepalive_timeout_ = keepalive_timeout; }
  void set_io_port_write_cycles(uint32_t cycles) { this->io_port_write_cycles_ = cycles; }
  void set_delay_slow_cycles(uint32_t cycles) { this->delay_slow_cycles_ = cycles; }
  void set_uart_bridge_enabled(bool enabled) { this->uart_bridge_enabled_ = enabled; }
  void set_uart_bridge_port(uint16_t port) { this->uart_bridge_port_ = port; }
  void set_uart_bridge_keepalive_timeout(uint16_t keepalive_timeout) { this->uart_bridge_keepalive_timeout_ = keepalive_timeout; }
  void set_uart_num(uint8_t uart_num) { this->uart_num_ = uart_num; }
  void set_uart_tx_pin(uint8_t pin) { this->uart_tx_pin_ = pin; }
  void set_uart_rx_pin(uint8_t pin) { this->uart_rx_pin_ = pin; }
  void set_uart_baud_rate(uint32_t baud_rate) { this->uart_baud_rate_ = baud_rate; }
  void set_uart_data_bits(uint8_t data_bits) { this->uart_data_bits_ = data_bits; }
  void set_uart_parity(uint8_t parity) { this->uart_parity_ = parity; }
  void set_uart_stop_bits(uint8_t stop_bits) { this->uart_stop_bits_ = stop_bits; }
  void set_uart_bridge_task_stack_size(uint32_t task_stack_size) { this->uart_bridge_task_stack_size_ = task_stack_size; }
  void set_uart_bridge_task_priority(uint8_t task_priority) { this->uart_bridge_task_priority_ = task_priority; }
  void set_cmsis_dap_switch(CmsisDapTcpServiceSwitch *service_switch) { this->cmsis_dap_switch_ = service_switch; }
  void set_uart_bridge_switch(UartBridgeServiceSwitch *service_switch) { this->uart_bridge_switch_ = service_switch; }

  void set_cmsis_dap_service_enabled(bool enabled);
  void set_uart_bridge_service_enabled(bool enabled);

 protected:
  bool start_cmsis_dap_service();
  bool start_uart_bridge_service();

  uint16_t port_{0};
  uint8_t tck_pin_{0};
  uint8_t tms_pin_{0};
  uint8_t tdi_pin_{0};
  uint8_t tdo_pin_{0};
  int16_t ntrst_pin_{-1};
  int16_t nreset_pin_{-1};
  int16_t led_pin_{-1};
  bool led_active_high_{false};
  uint32_t task_stack_size_{8192};
  uint8_t task_priority_{5};
  bool task_running_{false};
  bool keepalive_{true};
  uint16_t keepalive_timeout_{5};
  uint32_t io_port_write_cycles_{72};
  uint32_t delay_slow_cycles_{5};
  TaskHandle_t task_handle_{nullptr};
  volatile int task_stop_requested_{0};
  struct cmsis_dap_gpio_config *gpio_config_{nullptr};
  struct cmsis_dap_tcp_config *tcp_config_{nullptr};
  bool uart_bridge_enabled_{false};
  uint16_t uart_bridge_port_{0};
  uint16_t uart_bridge_keepalive_timeout_{0};
  uint8_t uart_num_{1};
  uint8_t uart_tx_pin_{0};
  uint8_t uart_rx_pin_{0};
  uint32_t uart_baud_rate_{115200};
  uint8_t uart_data_bits_{8};
  uint8_t uart_parity_{0};
  uint8_t uart_stop_bits_{1};
  uint32_t uart_bridge_task_stack_size_{4096};
  uint8_t uart_bridge_task_priority_{5};
  TaskHandle_t uart_bridge_task_handle_{nullptr};
  volatile int uart_bridge_task_stop_requested_{0};
  bool uart_bridge_task_running_{false};
  struct uart_bridge_config *uart_config_{nullptr};
  CmsisDapTcpServiceSwitch *cmsis_dap_switch_{nullptr};
  UartBridgeServiceSwitch *uart_bridge_switch_{nullptr};
};

class CmsisDapTcpServiceSwitch : public switch_::Switch {
 public:
  explicit CmsisDapTcpServiceSwitch(CmsisDapTcpComponent *parent) : parent_(parent) {}

 protected:
  void write_state(bool state) override;

  CmsisDapTcpComponent *parent_;
};

class UartBridgeServiceSwitch : public switch_::Switch {
 public:
  explicit UartBridgeServiceSwitch(CmsisDapTcpComponent *parent) : parent_(parent) {}

 protected:
  void write_state(bool state) override;

  CmsisDapTcpComponent *parent_;
};

}  // namespace cmsis_dap_tcp
}  // namespace esphome
