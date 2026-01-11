import re
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

def parse_clause(clause_str: str) -> dict[str, str | int | bool]:
    result = {}
    if not clause_str:
        return result
    clause_str = clause_str.strip()
    clause_str = re.sub(r"\s*=\s*", "=", clause_str)
    for i in clause_str.split(" "):

        if "=" not in i:
            raise ValueError(f"Некорректное значение: {i}. Ожидалось"
                             " 'столбец=значение'.")
        col, val = i.split("=", 1)
        if '""' in val or "''" in val:
            val = val.replace('""', '').replace("''", "")
            result[col] = val
        elif val.lower() == "true":
            result[col] = True
        elif val.lower() == "false":
            result[col] = False
        else:
            try:
                result[col] = int(val)
            except ValueError:
                result[col] = val
    return result

    
