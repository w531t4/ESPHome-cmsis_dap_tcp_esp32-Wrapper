// SPDX-FileCopyrightText: 2026 Aaron White <w531t4@gmail.com>
// SPDX-License-Identifier: MIT
#include "cmsis_dap_tcp_component.h"

#include "esphome/core/log.h"

#include <driver/uart.h>
#include <inttypes.h>

extern "C" {
#include "cmsis_dap_tcp.h"
#ifdef CONFIG_ESP_UART_BRIDGE_ENABLED
#include "uart_bridge.h"
#endif
}

namespace esphome {
namespace cmsis_dap_tcp {

static const char *const TAG = "cmsis_dap_tcp";

static void log_optional_pin(const char *name, int16_t pin) {
  if (pin >= 0) {
    ESP_LOGCONFIG(TAG, "  %s: GPIO%d", name, pin);
  } else {
    ESP_LOGCONFIG(TAG, "  %s: not configured", name);
  }
}

static void log_optional_startup_pin(const char *name, int16_t pin) {
  if (pin >= 0) {
    ESP_LOGI(TAG, "  %s: GPIO%d", name, pin);
  } else {
    ESP_LOGI(TAG, "  %s: not configured", name);
  }
}

void CmsisDapTcpComponent::setup() {
  ESP_LOGI(TAG, "Starting CMSIS-DAP TCP server");
  ESP_LOGI(TAG, "  Port: %u", this->port_);
  ESP_LOGI(TAG, "  JTAG pins: TCK=GPIO%u TMS=GPIO%u TDI=GPIO%u TDO=GPIO%u", this->tck_pin_, this->tms_pin_,
           this->tdi_pin_, this->tdo_pin_);
  log_optional_startup_pin("nTRST", this->ntrst_pin_);
  log_optional_startup_pin("nRESET", this->nreset_pin_);
  log_optional_startup_pin("LED", this->led_pin_);
  if (this->led_pin_ >= 0) {
    ESP_LOGI(TAG, "  LED polarity: active-%s", this->led_active_high_ ? "high" : "low");
  }
  ESP_LOGI(TAG, "  Timing: io_port_write_cycles=%" PRIu32 " delay_slow_cycles=%" PRIu32,
           this->io_port_write_cycles_, this->delay_slow_cycles_);
  ESP_LOGI(TAG, "  Task: stack=%" PRIu32 " priority=%u", this->task_stack_size_, this->task_priority_);
  if (this->uart_bridge_enabled_) {
    ESP_LOGI(TAG, "  UART bridge: port=%u UART%u TX=GPIO%u RX=GPIO%u baud=%" PRIu32 " %u%c%u",
             this->uart_bridge_port_, this->uart_num_, this->uart_tx_pin_, this->uart_rx_pin_, this->uart_baud_rate_,
             this->uart_data_bits_, this->uart_parity_ == 2 ? 'E' : (this->uart_parity_ == 3 ? 'O' : 'N'),
             this->uart_stop_bits_);
    ESP_LOGI(TAG, "  UART bridge task: stack=%" PRIu32 " priority=%u", this->uart_bridge_task_stack_size_,
             this->uart_bridge_task_priority_);
  }

  auto *gpio_config = new (struct cmsis_dap_gpio_config){
      static_cast<int>(this->tck_pin_),     static_cast<int>(this->tms_pin_),   static_cast<int>(this->tdi_pin_),
      static_cast<int>(this->tdo_pin_),     static_cast<int>(this->ntrst_pin_), static_cast<int>(this->nreset_pin_),
      static_cast<int>(this->led_pin_),
      this->led_active_high_ ? 1 : 0,
      static_cast<int>(this->io_port_write_cycles_),
      static_cast<int>(this->delay_slow_cycles_),
  };
  auto *tcp_config = new (struct cmsis_dap_tcp_config){
      static_cast<int>(this->port_),
      this->keepalive_ ? 0 : 1,
      static_cast<int>(this->keepalive_timeout_),
      gpio_config,
  };

  const BaseType_t result =
      xTaskCreate(cmsis_dap_tcp_task, "cmsis_dap_tcp", this->task_stack_size_, tcp_config, this->task_priority_,
                  &this->task_handle_);
  if (result != pdPASS) {
    ESP_LOGE(TAG, "Failed to start CMSIS-DAP TCP task");
    this->mark_failed();
    return;
  }

  ESP_LOGI(TAG, "CMSIS-DAP TCP task started");

  if (this->uart_bridge_enabled_) {
#ifdef CONFIG_ESP_UART_BRIDGE_ENABLED
    auto *uart_config = new (struct uart_bridge_config){
        static_cast<int>(this->uart_bridge_port_),
        static_cast<int>(this->uart_bridge_keepalive_timeout_),
        static_cast<int>(this->uart_num_),
        static_cast<int>(this->uart_tx_pin_),
        static_cast<int>(this->uart_rx_pin_),
        static_cast<int>(this->uart_baud_rate_),
        this->uart_data_bits_ == 7 ? UART_DATA_7_BITS : UART_DATA_8_BITS,
        this->uart_parity_ == 2 ? UART_PARITY_EVEN : (this->uart_parity_ == 3 ? UART_PARITY_ODD : UART_PARITY_DISABLE),
        this->uart_stop_bits_ == 2 ? UART_STOP_BITS_2 : UART_STOP_BITS_1,
    };
    const BaseType_t uart_result =
        xTaskCreate(uart_bridge_task, "uart_bridge", this->uart_bridge_task_stack_size_, uart_config,
                    this->uart_bridge_task_priority_, &this->uart_bridge_task_handle_);
    if (uart_result != pdPASS) {
      ESP_LOGE(TAG, "Failed to start UART bridge task");
      this->mark_failed();
      return;
    }
    ESP_LOGI(TAG, "UART bridge task started");
#else
    ESP_LOGE(TAG, "UART bridge enabled in YAML but upstream UART bridge was not compiled");
    this->mark_failed();
    return;
#endif
  }
}

void CmsisDapTcpComponent::dump_config() {
  ESP_LOGCONFIG(TAG, "CMSIS-DAP TCP:");
  ESP_LOGCONFIG(TAG, "  Port: %u", this->port_);
  ESP_LOGCONFIG(TAG, "  TCK pin: GPIO%u", this->tck_pin_);
  ESP_LOGCONFIG(TAG, "  TMS pin: GPIO%u", this->tms_pin_);
  ESP_LOGCONFIG(TAG, "  TDI pin: GPIO%u", this->tdi_pin_);
  ESP_LOGCONFIG(TAG, "  TDO pin: GPIO%u", this->tdo_pin_);
  log_optional_pin("nTRST pin", this->ntrst_pin_);
  log_optional_pin("nRESET pin", this->nreset_pin_);
  log_optional_pin("LED pin", this->led_pin_);
  if (this->led_pin_ >= 0) {
    ESP_LOGCONFIG(TAG, "  LED polarity: active-%s", this->led_active_high_ ? "high" : "low");
  }
  ESP_LOGCONFIG(TAG, "  IO port write cycles: %" PRIu32, this->io_port_write_cycles_);
  ESP_LOGCONFIG(TAG, "  Delay slow cycles: %" PRIu32, this->delay_slow_cycles_);
  ESP_LOGCONFIG(TAG, "  Task stack size: %" PRIu32, this->task_stack_size_);
  ESP_LOGCONFIG(TAG, "  Task priority: %u", this->task_priority_);
  if (this->uart_bridge_enabled_) {
    ESP_LOGCONFIG(TAG, "  UART bridge:");
    ESP_LOGCONFIG(TAG, "    Port: %u", this->uart_bridge_port_);
    ESP_LOGCONFIG(TAG, "    UART: %u", this->uart_num_);
    ESP_LOGCONFIG(TAG, "    TX pin: GPIO%u", this->uart_tx_pin_);
    ESP_LOGCONFIG(TAG, "    RX pin: GPIO%u", this->uart_rx_pin_);
    ESP_LOGCONFIG(TAG, "    Baud rate: %" PRIu32, this->uart_baud_rate_);
    ESP_LOGCONFIG(TAG, "    Framing: %u%c%u", this->uart_data_bits_,
                  this->uart_parity_ == 2 ? 'E' : (this->uart_parity_ == 3 ? 'O' : 'N'), this->uart_stop_bits_);
    ESP_LOGCONFIG(TAG, "    Task stack size: %" PRIu32, this->uart_bridge_task_stack_size_);
    ESP_LOGCONFIG(TAG, "    Task priority: %u", this->uart_bridge_task_priority_);
  } else {
    ESP_LOGCONFIG(TAG, "  UART bridge: disabled");
  }
}

float CmsisDapTcpComponent::get_setup_priority() const { return setup_priority::AFTER_WIFI; }

}  // namespace cmsis_dap_tcp
}  // namespace esphome
