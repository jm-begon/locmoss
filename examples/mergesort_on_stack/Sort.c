/* ========================================================================= *
 * InsertionSort
 * Implementation of the InsertionSort algorithm.
 * ========================================================================= */

#include <stdio.h>
#include <stdlib.h>

static void mergeSort(int array[], int p, int r);
static void merge(int array[], int p, int q, int r);


static void mergeSort(int array[], int p, int r)
{
    int n = r - p + 1;
    if (n <= 1)
        return;
    int q = p + (n + 1) / 2;
    mergeSort(array, p, q - 1);
    mergeSort(array, q, r);
    merge(array, p, q, r);
}

static void merge(int array[], int p, int q, int r)
{

    int i = p, j = q, n = r-p+1;
    int aux[n];

    for (int k = 1; k < n; k++)
    {
        if (i == q)
            aux[k] = array[j++];
        else if (j == r + 1)
            aux[k] = array[i++];
        else if (array[i] < array[j])
            aux[k] = array[i++];
        else
            aux[k] = array[j++];
    }

    for (int k = 1; k < n; k++)
        array[k+p] = aux[k];

}

void sort(int* array, size_t length)
  mergeSort(array, 0, length-1);
}
