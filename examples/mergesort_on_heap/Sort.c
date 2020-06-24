/* ========================================================================= *
 * InsertionSort
 * Implementation of the InsertionSort algorithm.
 * ========================================================================= */

#include <stdio.h>
#include <stdlib.h>

static void merge(int tab[], int lo, int mid, int hi, int aux[]);
static void mergeSortAux(int tab[], int lo, int hi, int aux[]);

static void merge(int tab[], int lo, int mid, int hi, int aux[]) {
  int i = lo, j = mid;

  for (int k = lo; k <= hi; k++)
    if (i == mid)
      aux[k] = tab[j++];
    else if (j == hi + 1)
      aux[k] = tab[i++];
    else if (tab[i] < tab[j])
      aux[k] = tab[i++];
    else
      aux[k] = tab[j++];

  for (int k = lo; k <= hi; k++)
    tab[k] = aux[k];

}

static void mergeSortAux(int tab[], int lo, int hi, int aux[]) {
  int n = hi - lo + 1;
  if (n <= 1)
    return;
  int mid = lo + (n + 1) / 2;
  mergeSortAux(tab, lo, mid - 1, aux);
  mergeSortAux(tab, mid, hi, aux);
  merge(tab, lo, mid, hi, aux);
}

void sort(int* array, size_t length)
  int *aux = malloc(length*sizeof(int));
  mergeSortAux(array, 0, length-1, aux);
  free(aux);
}
