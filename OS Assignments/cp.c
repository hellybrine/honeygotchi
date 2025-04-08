#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s source_file destination_file\n", argv[0]);
        return 1;
    }

    FILE *source = fopen(argv[1], "rb");
    FILE *destination = fopen(argv[2], "wb");

    if (!source || !destination) {
        perror("Error");
        return 2;
    }

    char buffer[1024];
    size_t bytesRead;

    while ((bytesRead = fread(buffer, 1, sizeof(buffer), source)) > 0) {
        fwrite(buffer, 1, bytesRead, destination);
    }

    fclose(source);
    fclose(destination);

    return 0;
}
