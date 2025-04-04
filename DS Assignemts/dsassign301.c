#include <stdio.h>
#include <string.h>

                                                                            // Merge Function
void mergeStrings(char result[], const char str1[], const char str2[]) {
    strcpy(result, str1);                                                   // Str 1
    strcat(result, str2);                                                   // Str 2
}

                                                                            // Reverse
void reverseString(char str[]) {
    int length = strlen(str);
    for (int i = 0; i < length / 2; i++) {
        char temp = str[i];
        str[i] = str[length - i - 1];
        str[length - i - 1] = temp;
    }
}

int main() {
    char str1[100];
    char str2[100];
    char merged[100 * 2];                                                   // Merge

                                                                            // Inputs
    printf("String 1 : ");
    scanf("%s", str1);

    printf("String 2 : ");
    scanf("%s", str2);

                                                                            // Print merge
    mergeStrings(merged, str1, str2);
    printf("Merged : %s\n", merged);

                                                                            // Reverse merged
    reverseString(merged);
    printf("Reversed : %s\n", merged);

    return 0;
}
