Examples
========
Once installed, run `local_moss --language c --short_output --reference Sort.h */*.c` 
from this directory.

This will consider the `.c` files to form the softwares, with one software per folder.
Alternatively, the softwares can be supplied manually: 
`local_moss --language c --short_output --reference Sort.h insertionsort/Sort.c mergesort_on_heap/Sort.c mergesort_on_stack/Sort.c`

Observe how both implementation of merge sort are found to be much more similar 
to the other pairings, even though the function signatures (names and number  
of arguments) are different, as is the tabulation, ordering, variable names, 
etc.

To get a longer output, with code comparison, remove the `--short_output` flag.
Consider redirecting the output to a file for more readability and easier 
navigation (thanks to the anchors).

See `local_moss -h` for more options.

