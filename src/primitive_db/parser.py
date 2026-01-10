import shlex


def parse_command(command_str):
    args = shlex.split(command_str)
    if not args:
        return "", []
    return args[0], args[1:]

def parse_pairs(pairs):
    invalid = ""
    for pair in pairs:
        if pair.count(":") != 1 or pair.startswith(":") or pair.endswith(":"):
            invalid = pair
            break
        
    return invalid
