#define _GNU_SOURCE

#include <stdio.h>
#include <dlfcn.h>
#include <unistd.h>
#include <stdio.h>
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
 
#include <execinfo.h>
#include <signal.h>
#include <bfd.h>
#include <unistd.h>
 
/* globals retained across calls to resolve. */
static bfd* abfd = 0;
static asymbol **syms = 0;
static asection *text = 0;

static void* (*real_malloc)(size_t)=NULL;
void (*real_free)(void *ptr)=NULL;


struct stack_frame {
        struct stack_frame *prev;
        void *return_addr;
} __attribute__((packed));
typedef struct stack_frame stack_frame;

static int backtrace_from_fp(void **buf, int size)
{
        //buf[0] = __builtin_return_address (0);

        stack_frame *fp;
        __asm__("movq %%rbp, %[fp]" :  /* output */ [fp] "=r" (fp));
        int count = 0;
	int i;
        for(i = 0; i < size && fp != NULL; fp = fp->prev, i++)
        { 
	    printf("%d fp=%p\n", i, fp ); 
            buf[i] = fp->return_addr;
	    if( buf[i] == (void*)0x2000200020002) break;
            count ++; 
	    printf("\t%d fp=%p\n", i, buf[i] ); 
         }
        return count;
}

static void mtrace_init(void)
{
    if (NULL == real_malloc) {
       real_malloc = dlsym(RTLD_NEXT, "malloc");
       if (NULL == real_malloc) {
          fprintf(stderr, "Error in `dlsym`: %s\n", dlerror());
       }
    }
    if(real_free == NULL)
    {
       real_free = dlsym(RTLD_NEXT, "free");

	}
}

void free(void* ptr)
{
    if(real_free==NULL) {
        mtrace_init();
    }
    real_free(ptr);
    //fprintf(stderr, "free(%p) \n", ptr);
}
static void resolve(char *address) {
    if (!abfd) {
 	  char ename[1024];
 	  int l = readlink("/proc/self/exe",ename,sizeof(ename));
 	  if (l == -1) {
 	    perror("failed to find executable\n");
 	    return;
 	  }
 	  ename[l] = 0;
 
 	  bfd_init();
 
 	  abfd = bfd_openr(ename, 0);
 	  if (!abfd) {
 	      perror("bfd_openr failed: ");
 	      return;
 	  }
 
 	  /* oddly, this is required for it to work... */
 	  bfd_check_format(abfd,bfd_object);
 
 	  unsigned storage_needed = bfd_get_symtab_upper_bound(abfd);
 	  syms = (asymbol **) malloc(storage_needed);
 	  unsigned cSymbols = bfd_canonicalize_symtab(abfd, syms);
 
 	  text = bfd_get_section_by_name(abfd, ".text");
    }
 
    long offset = ((long)address) - text->vma;
    if (offset > 0) {
        const char *file;
        const char *func;
        unsigned line;
        if (bfd_find_nearest_line(abfd, text, syms, offset, &file, &func, &line) && file)
            printf("file: %s, line: %u, func %s\n",file,line,func);
        else

            fprintf(stderr, "%p\n", address);
    }
    else
    {
            fprintf(stderr, "%p\n", address);
    }
}
 __thread int i;
void *malloc(size_t size)
{
    if(real_malloc==NULL) {
        mtrace_init();
    }
i ++;
    void *p = NULL;
    p = real_malloc(size);
    //fprintf(stderr, "malloc(%d) %p (%i)\n", size, p, i);
    //fprintf(stderr, "%p\n", p);
    //size_t s =  backtrace_from_fp(array,10);
    //backtrace_symbols_fd(array, s, STDERR_FILENO);
    if( i == 1 )
    {
        void *array[10];
         size_t s = backtrace(array, 10);
         //backtrace_symbols_fd(array, s, STDERR_FILENO);

        int x=0;
    //fprintf(stderr, "stack size %d\n", s);
        for(x=0;x < s; x++)
           resolve(array[x]);
    }
    //fprintf(stderr, "\n");
    //bt();
i--;
    return p;
}
