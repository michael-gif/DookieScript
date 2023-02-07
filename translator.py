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
    python_code = [convert_token(t) for t in tokens]
    print(python_code)
    with open(destination, 'w') as f:
        for code in python_code:
            python_string = '\n'.join(code)
            f.write(python_string + "\n")
    print("[INFO] Executing python code\n")
    #subprocess.call(["python", "-m", destination[:-3]], shell=True)
    #os.remove(destination)


def convert_token(token: Token) -> list:
    """
    | Identify what the token type is, then use the relevant converter
    :param token:
    :return:
    """
    python_strings = []
    if token.name == "reusable":
        python_strings += convert_function(token)
    if token.name == "container":
        python_strings += convert_variable(token)
    if token.name == "call":
        python_strings += convert_call(token)
    if token.name == "repeat":
        python_strings += convert_for(token)
    if token.name == "repeat_query":
        python_strings += convert_while(token)
    if token.name == "query":
        python_strings += convert_query(token)
    if token.name in ["string", "int", "float", "boolean", "shit"]:
        python_strings += [token.attributes["value"]]
    return python_strings


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
    lines += ["", ""]
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