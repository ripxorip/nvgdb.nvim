#include <stdint.h>

uint32_t glob_tester = 0xdeadbeef;

int main()
{
    volatile uint32_t stack_tester = 0xb16b00b5;
    glob_tester += stack_tester;
    if (0x3 == glob_tester)
    {
        stack_tester = 0x00;
    }
    return 0;
}
