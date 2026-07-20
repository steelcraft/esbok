/**
 * @file gpio_blinky.c
 * @brief Пример мигания светодиодом на STM32 (HAL)
 *
 * Демонстрация использования тегов для выборочного включения
 * фрагментов кода в AsciiDoc через include::...[tags=...]
 */

#include <stm32f4xx.h>

/* tag::init_block[] */
void GPIO_Init_LED(void) {
    /* Включаем тактирование порта A */
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;

    /* Настраиваем PA5 как выход (push-pull) */
    GPIOA->MODER  &= ~(0x3U << (5 * 2));  /* сброс */
    GPIOA->MODER  |=  (0x1U << (5 * 2));  /* режим output */
    GPIOA->OTYPER &= ~(1U << 5);          /* push-pull */
    GPIOA->OSPEEDR &= ~(0x3U << (5 * 2)); /* low speed */
}
/* end::init_block[] */

/* tag::toggle_block[] */
void GPIO_Toggle_LED(void) {
    GPIOA->ODR ^= (1U << 5);
}
/* end::toggle_block[] */

/* tag::delay_block[] */
void delay_ms(uint32_t ms) {
    /* Простейшая задержка (зависит от частоты ядра) */
    volatile uint32_t count = ms * (SystemCoreClock / 4000U);
    while (count--) { __NOP(); }
}
/* end::delay_block[] */

/* tag::main_block[] */
int main(void) {
    SystemCoreClockUpdate();
    GPIO_Init_LED();

    while (1) {
        GPIO_Toggle_LED();
        delay_ms(500);
    }
    return 0;
}
/* end::main_block[] */
