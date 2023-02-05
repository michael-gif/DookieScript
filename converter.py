import subprocess

from typing import List
from token import Token


def convert2py(tokens: List[Token], destination: str) -> str:
    """
    | Convert a tree of tokens into python code
    :param tokens:
    :return:
    """
    print("[INFO] Translating doodooscript into python")
    python_code = [convert_token(t) for t in tokens]
    with open(destination, 'w') as f:
        for code in python_code:
            f.write(code)
    print("[INFO] Executing python code")
    subprocess.call(["python", "-m", destination.split('.py')[0]], shell=True)


def convert_token(token: Token) -> str:
    """
    | Identify what the token type is, then use the relevant converter
    :param token:
    :return:
    """
    python_strings = []
    if token.name == "reusable":
        python_strings.append(convert_function(token))
    if token.name == "container":
        python_strings.append(convert_variable(token))
    if token.name == "call":
        python_strings.append(convert_call(token))
    if token.name in ["string", "int", "float", "boolean", "shit"]:
        python_strings.append(token.attributes["value"])
    return '\n'.join(python_strings)


def convert_function(token: Token) -> str:
    """
    | Convert a function into it's definition and code block
    :param token:
    :return:
    """
    declaration = ""
    function_name = token.attributes["function_name"]
    declaration += "def " + function_name + "("
    parameters = token.attributes["parameters"]
    parameters_string = [p_name for p_name, p_type in parameters]
    declaration += ', '.join(parameters_string) + "):"

    function_body = token.attributes["code_block"]
    if function_body:
        python_code = [convert_token(t) for t in function_body]
        code_block = '\n'.join(["    " + code for code in python_code])
    else:
        code_block = "    pass\n"
    return declaration + "\n" + code_block + "\n"


def convert_variable(token: Token) -> str:
    """
    | Convert variable name and value into a python variable
    :param token:
    :return:
    """
    python_string = token.attributes["variable_name"] + " = " + convert_token(token.attributes["variable_value"])
    return python_string


def convert_call(token: Token) -> str:
    """
    | Convert a function call into python code
    :param token:
    :return:
    """
    parameters = token.attributes["parameters"]
    parameters_string = [p_name for p_name, p_type in parameters]
    function_call = f"{token.attributes['function_name']}({','.join(parameters_string)})"
    return function_call
