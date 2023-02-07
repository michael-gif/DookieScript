import subprocess
import os

from typing import List, Any
from token import Token


def translate_to_python(tokens: List[Token], destination: str) -> str:
    """
    | Convert a tree of tokens into python code
    :param tokens:
    :return:
    """
    print("[INFO] Translating doodooscript into python")
    lines = []
    for t in tokens:
        lines += convert_token(t)
    print(lines)
    with open(destination, 'w') as f:
        for line in lines:
            f.write(line + "\n")
    print("[INFO] Executing python code\n")
    subprocess.call(["python", "-m", destination[:-3]], shell=True)
    #os.remove(destination)


def convert_token(token: Token) -> list:
    """
    | Identify what the token type is, then use the relevant converter
    :param token:
    :return:
    """
    python_strings = []
    converters = {
        'include': convert_import,
        'reusable': convert_function,
        'container': convert_variable,
        'call': convert_call,
        'repeat': convert_for,
        'repeat_query': convert_while,
        'query': convert_query,
        'return': convert_return
    }
    if token.name in ["string", "int", "float", "boolean", "shit"]:
        python_strings += [token.attributes["value"]]
    else:
        python_strings += converters[token.name](token)
    return python_strings


def convert_import(token: Token) -> list[str]:
    """
    | Convert a module name into an import
    :param token:
    :return:
    """
    return ["import " + token.attributes["module_name"]]


def convert_function(token: Token) -> list[str]:
    """
    | Convert a function into it's definition and code block
    :param token:
    :return:
    """
    lines = []
    declaration = ""
    function_name = token.attributes["function_name"]
    declaration += "def " + function_name + "("
    parameters = token.attributes["parameters"]
    parameters_string = [p_name for p_name, p_type in parameters]
    declaration += ', '.join(parameters_string) + "):"
    lines.append(declaration)

    function_body = token.attributes["code_block"]
    code_block = []
    if function_body:
        for t in function_body:
            python_lines = convert_token(t)
            for line in python_lines:
                code_block.append("    " + line)
    else:
        code_block.append("    pass")
    lines += code_block
    return lines


def convert_variable(token: Token) -> list:
    """
    | Convert variable name and value into a python variable
    :param token:
    :return:
    """
    python_string = token.attributes["variable_name"] + " = " + convert_token(token.attributes["variable_value"])[0]
    return [python_string]


def convert_call(token: Token) -> list[str]:
    """
    | Convert a function call into python code
    :param token:
    :return:
    """
    parameters = token.attributes["parameters"]
    function_call = f"{token.attributes['function_name']}({','.join(parameters)})"
    return [function_call]


def convert_for(token: Token) -> list[str]:
    values = token.attributes["start_stop_step"]
    if values[3] == "++":
        values[3] = 1
    if values[3] == "--":
        values[3] = -1
    lines = [f"for {values[0]} in range({values[1]}, {values[2]}, {values[3]}):"]
    for t in token.attributes["code_block"]:
        lines += ["    " + line for line in convert_token(t)]
    return lines


def convert_while(token: Token) -> list[str]:
    """
    | Convert a while loop into python code
    :param token:
    :return:
    """
    if token.attributes["condition"] in ["true", "false"]:
        token.attributes["condition"] = token.attributes["condition"].capitalize()
    lines = ["while " + token.attributes["condition"] + ":"]
    for t in token.attributes["code_block"]:
        lines += ["    " + line for line in convert_token(t)]
    return lines


def convert_query(token: Token) -> list[str]:
    """
    | Convert an if statement into python code
    :param token:
    :return:
    """
    if token.attributes["condition"] in ["true", "false"]:
        token.attributes["condition"] = token.attributes["condition"].capitalize()
    lines = ["if " + token.attributes["condition"] + ":"]
    for t in token.attributes["code_block"]:
        if type(t) != Token:
            lines.append("    " + t)
        else:
            lines += ["    " + line for line in convert_token(t)]
    return lines


def convert_return(token: Token) -> list[str]:
    """
    | Convert return statement
    :param token:
    :return:
    """
    return_value = token.attributes["return_value"]
    if return_value:
        return ["return " + convert_token(return_value[0])[0]]
    else:
        return ["return"]