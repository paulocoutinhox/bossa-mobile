extern "C" {
    #include <string>
    
    __attribute__((visibility("default"))) __attribute__((used))
    int tokeniseToArgcArgv(char *buffer, int *argc, char *argv[], const int argv_length)
    {
        int i = 0;

        for (i = 0; i < argv_length; i++) 
        {
            if (NULL == (argv[i] = strtok_r(NULL, " ", &buffer))) 
            {
                break;
            }
        }

        *argc = i;

        return i;
    }

    __attribute__((visibility("default"))) __attribute__((used))
    void test_flutter_void() 
    {
        fprintf(stdout, "Function [test_flutter_void] was called\n");
    }

    __attribute__((visibility("default"))) __attribute__((used))
    char * test_flutter_pointer(int argc, char* args) 
    {
        fprintf(stdout, "Function [test_flutter_pointer] was called\n");
        fprintf(stdout, "Function [test_flutter_pointer] Value send: %d | %s\n", argc, args);

        return args;
    }

    __attribute__((visibility("default"))) __attribute__((used))
    int bossa_main(int argc, char* args)
    {
        fprintf(stdout, "Function [bossa_main] was called\n");
        fprintf(stdout, "Function [bossa_main] Value send: %d | %s\n", argc, args);

        // convert string to array of params
        int nargc = 0;
        char *nargv[255] = {0};

        tokeniseToArgcArgv(args, &nargc, nargv, sizeof(nargv));

        // check converted array
        int i = 0;

        for (i = 0; i < nargc; i++) 
        {
            fprintf(stdout, "Function [bossa_main] Value %d parsed: %s\n", (i + 1), nargv[i]);
        }
        
        // call main with new params
        return main(nargc, nargv);
    }
}