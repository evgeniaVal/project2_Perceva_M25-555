import shlex

import prompt


def parse_command(command_str):
    args = shlex.split(command_str)
    if not args:
        return None, []
    return args[0], args[1:]

def get_input(prompt_msg=">>>Введите команду: "):
    try:
        input_str = prompt.string(prompt_msg).strip().lower() # type: ignore
        cmd, args = parse_command(input_str)
    except (KeyboardInterrupt, EOFError):
        cmd, args = "exit", []
    return cmd, args

def parse_pairs(pairs):
    invalid = ""
    for pair in pairs:
        if pair.count(":") != 1 or pair.startswith(":") or pair.endswith(":"):
            invalid = pair
            break
        
    return invalid
