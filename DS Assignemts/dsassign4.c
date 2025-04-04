#include <stdio.h>
#include <string.h>

int main() {
    char inputString[100];
    printf("Enter a string: ");
    fgets(inputString, sizeof(inputString), stdin);

    int Count = 0;
    char Result[100];
    int Index = 0;

    for (int i = 0; inputString[i] != '\0'; i++) {
        char c = inputString[i];
        if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u' ||
            c == 'A' || c == 'E' || c == 'I' || c == 'O' || c == 'U') {
            Count++;
        } else {
            Result[Index++] = c;
        }
    }

    Result[Index] = '\0';

    printf("Total Frequency: %d\n", Count);
    printf("String after deleting : %s\n", Result);

    return 0;
}