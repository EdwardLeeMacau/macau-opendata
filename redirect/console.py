import sys
from io import StringIO


class ConsoleOutputRedirect:
    """ Wrapper to redirect stdout or stderr """
    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(s)

    def writelines(self, lines):
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()


if __name__ == "__main__":
    
    def block_output():
        # Block Console stdout
        stdout_redirect = ConsoleOutputRedirect(sys.stdout)
        stdout_redirect.fp = StringIO()
        temp_stdout, sys.stdout = sys.stdout, stdout_redirect

        # Core Method
        print("Hello World")

        # Swap sys.stdout
        sys.stdout = temp_stdout

        # Block output
        print("Today is Good Weather, {}".format(stdout_redirect.fp.getvalue()), end='')
    
    block_output()