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

def parse_clause(clause_str: list[str]) -> dict[str, str | int | bool]:
    result = {}
    if not clause_str:
        return result
    for i in clause_str:
        i = i.strip()
        i = re.sub(r"\s*=\s*", "=", i)
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
                raise ValueError(f"Некорректное значение: {val}. Ожидалось"
                                 " str (в кавычках), int или bool (true/false).")
    return result

    
