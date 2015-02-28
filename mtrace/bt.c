//#define _GNU_SOURCE

#include <stdio.h>
#include <dlfcn.h>
#include <execinfo.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>


struct stack_frame {
        struct stack_frame *prev;
        void *return_addr;
} __attribute__((packed));
typedef struct stack_frame stack_frame;

int backtrace_from_fp(void **buf, int size)
{
        int i;
        stack_frame *fp;

        __asm__("movq %%rbp, %[fp]" :  /* output */ [fp] "=r" (fp));
        int count = 0;
        for(i = 0; i < size && fp != NULL; fp = fp->prev, i++)
	{ count ++; buf[i] = fp->return_addr; }
	return count;
}
void bt()
{
  void *array[10];
  size_t size =  backtrace_from_fp(array,10);
  // get void*'s for all entries on the stack
  //size_t size = backtrace(array, 10);
  //
  //     // print out all the frames to stderr
  fprintf(stderr, "backtrace:\n");
  backtrace_symbols_fd(array, size, STDERR_FILENO);
}

extern int some()
{
	bt();
}
int main()
{
	malloc(12);
	some();
}
