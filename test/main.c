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

int dummy_func2(int test1)
{
    int temp_var = test1*8;
    temp_var++;
    return temp_var*2;
}


int dummy_func1(int test3)
{
    int temp_var = test3 + 1;
    temp_var++;
    temp_var = dummy_func2(temp_var);
    return temp_var << 3;
}

uint32_t glob_tester = 0xdeadbeef;

int main()
{
    volatile uint32_t stack_tester = 0xb16b00b5;
    glob_tester += stack_tester;
    glob_tester += dummy_func1(stack_tester);
    if (0x3 == glob_tester)
    {
        stack_tester = 0x00;
    }
    return 0;
}
