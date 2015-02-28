#define _GNU_SOURCE

#include <stdio.h>
#include <dlfcn.h>
#include <sys/types.h>
       #include <sys/stat.h>
//       #include <fcntl.h>


static void* (*real_malloc)(size_t)=NULL;
static int (*real_open)(const char*, int, mode_t mode)=NULL;
static FILE *(*real_fopen)(const char *path, const char *mode)=NULL;

FILE* fp=NULL;

static void mtrace_init(void)
{
#if  0
    real_malloc = dlsym(RTLD_NEXT, "malloc");
    if (NULL == real_malloc) {
        fprintf(stderr, "Error in `dlsym`: %s\n", dlerror());
    }
#endif
    if(real_open == NULL)
    {
       real_open = dlsym(RTLD_NEXT, "open");
    }
    if(real_fopen != NULL) return;
    //fprintf(stderr, "real_fopen: %p\n", real_fopen );
    real_fopen = dlsym(RTLD_NEXT, "fopen");
    //fprintf(stderr, "got real_fopen: %p\n", real_fopen );
    if (NULL == real_fopen)
    {
        fprintf(stderr, "Error in %p `dlsym`: %s\n", real_fopen, dlerror());
        void* libc_handle = dlopen("libc.so.6", RTLD_LAZY);
        real_fopen = dlsym(libc_handle,"fopen");
        fprintf(stderr, "and now Error in %p `dlsym`: %s\n", real_fopen, dlerror());
    }
    if(fp == NULL)
    {
       fp = fopen("test.data", "rw");
    }
    //fprintf(stderr, "mtrace_init done: %p\n", real_fopen );
}

void *xx_malloc(size_t size)
{
    if(real_malloc==NULL) {
        mtrace_init();
    }

    void *p = NULL;
    fprintf(stderr, "malloc(%d) = ", size);
    p = real_malloc(size);
    fprintf(stderr, "%p\n", p);
    return p;
}

FILE *xxfopen(const char *path, const char *mode)
{
    if(real_fopen==NULL) {
        mtrace_init();
    }

//    fprintf(stderr, "fopen(%s) = ", path);

    FILE* p = real_fopen(path, mode );
 //   fprintf(stderr, "%d\n", p);
    return p;
}
void format_flags(size_t s, char*ptr, mode )
{
    ptr[0]=0;
    if(mode&O_CREAT)
    {
       strcat(ptr, "|O_CREAT");
    }
    if(mode&O_EXCL)
    {
       strcat(ptr, "|O_EXCL");
    }
    if(mode&O_NOCTTY)
    {
       strcat(ptr, "|O_NOCTTY");
    }
    if(mode&O_TRUNC)
    {
       strcat(ptr, "|O_TRUNC.");
    }
}

int open(const char*path, int flags, mode_t mode)
{
     if(real_open==NULL) {
        mtrace_init();
    }
    int p = real_open(path, flags, mode );
    fprintf(stderr, "****mtrace*** :open(%s, %d, %d) = %d\n", path,flags, mode, p);

//    fwrite( path, strlen(path), 1, fp);

    //fwrite("\n", strlen("\n"), 1, fp );
    return p;
}
