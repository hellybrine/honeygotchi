#include <stdio.h>
#define MAX_SIZE 50

void printArray(int arr[], int size) {                                      // Initialising Array of 50
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

                                                                            // InsertBase
void insertElement(int arr[], int *size, int index, int element) {

    for (int i = *size; i > index; i--) {
        arr[i] = arr[i - 1];
    }

    arr[index] = element;
    (*size)++;
}
                                                                            // DeleteBase
void deleteElement(int arr[], int *size, int index) {

    for (int i = index; i < *size - 1; i++) {
        arr[i] = arr[i + 1];
    }

    (*size)--;
}

int main() {
    int arr[MAX_SIZE] = {16, 23, 39, 44, 58};
    int size = 5;

    printf("Original array: ");
    printArray(arr, size);

    //INSERTING ELEMENTS
                                                                            // Beginning
    insertElement(arr, &size, 0, 10);
    printf("Inserting at beginning: ");
    printArray(arr, size);

                                                                            // Middle
    insertElement(arr, &size, 3, 40);
    printf("Inserting in middle: ");
    printArray(arr, size);

                                                                            // End
    insertElement(arr, &size, size, 68);
    printf("Inserting at end: ");
    printArray(arr, size);




    //DELETING ELEMENTS

                                                                            // Beginning
    deleteElement(arr, &size, 0);
    printf("Deleting first element: ");
    printArray(arr, size);

                                                                            // Middle
    deleteElement(arr, &size, 2);
    printf("Deleting middle element: ");
    printArray(arr, size);

                                                                            // End
    deleteElement(arr, &size, size - 1);
    printf("Deleting last element: ");
    printArray(arr, size);

    return 0;
}
