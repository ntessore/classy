#include "class_public/include/common.h"

#include <stdio.h>

int main()
{
    const char* version = _VERSION_;
    printf("%s", version+1);
    return 0;
}
