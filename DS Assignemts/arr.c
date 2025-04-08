#include <stdio.h>

void display(int arr[], int n){
      // Traverse
  for(int i = 0; i < n; i++)
    {
      printf("%d\n", arr[i]);
    }
}

int indInsertion(int arr[], int size, int capacity, int index, int element){
    // Insert
    if(size>=capacity){
    return -1;
    }
    for (int i = size-1; i >= index; i--)
    {
      arr[i+1] = arr[i];
    }
    arr[index] = element;
    return 1;
}

int main()
{
    int arr[50] = {1,2,3,4,5,};
    int size = 5, element = 10, index=1;
    display(arr,size);
    indInsertion(arr, size, 50, index, element);
    size +=1;
    display (arr, size);
    return 0;
}