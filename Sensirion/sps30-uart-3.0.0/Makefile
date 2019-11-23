# See user_config.inc for build customizations
-include user_config.inc
include default_config.inc

.PHONY: all clean

all: sps30-json-output

sps30-json-output: clean
	$(CC) $(CFLAGS) -o $@ ${sps30_uart_sources} ${uart_sources} ${sps30_uart_dir}/sps30-json-output.c

clean:
	$(RM) sps30-json-output
