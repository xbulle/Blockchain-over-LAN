import sys


def progress(progress_slice, re=False):
    prc = int(100 / progress_slice)
    prc = prc if prc > 0 else 100
    p = '[' + ''.join(['#' for i in range(0, int(50 / progress_slice))]) + ''.join(
        [' ' for i in range(0, (50 - int(50 / progress_slice)))] if progress_slice > 1 else '') + '] ' + str(prc) + '%'
    end = '\n' if re else ''
    print('\r    ' + str(p), end=end)


def resolve_program_mode():
    if '--enable-debug' in sys.argv:
        return True
    else:
        return False


def print_usage_prompt():
    print(
        '\r\nUSAGE: [option] [parameters]\n\nOptions:\n\n\ttransact\tPerforms transaction.\t\t\t\t\tParameters: ['
        'amount] [target name]\n\tname\t\tUpdates or displays invoker\'s name.\t\t\tParameters: [new name | <no '
        'param>]\n\tpeers\t\tDisplays a list of connected peers.\t\t\tParameters: <no param>\n\tclose\t\tTerminates '
        'all active connections and safely exit.\tParameters: <no param>\n\tstatus\t\tPrints status of current peers '
        'wallet.\t\t\tParameters: <no param>\n')
