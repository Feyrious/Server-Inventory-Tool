import sys

import envconfig


def print_system_info(code: int, message: str = ""):
    if envconfig.IS_VERBOSE:
        if len(message) > 0:
            print(message)

        print(f"Process finished with exit code {code}")

def status_ok():
    print_system_info(0)
    sys.exit(0)

def error_read_file(file_name):
    print_system_info(1, "Error reading file " + file_name)
    sys.exit(1)