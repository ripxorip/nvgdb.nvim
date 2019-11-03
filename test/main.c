#include <stdint.h>

struct substruct
{
    int field4;
    int field5;
    char field6;
};

struct tstruct
{
    int field1;
    int field2;
    char field3;
    struct substruct ss;
} teststruct =
{
    .field1 = 0x1,
    .field2 = 0x1,
    .field3 = 'c',
    .ss =
    {
        .field4 = 0x4,
        .field5 = 0x4,
        .field6 = 'a',
    }
};

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
