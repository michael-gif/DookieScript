from typing import Tuple, List
from token import Token


def function_parser(raw_text: str) -> Tuple[str, Token]:
    """
    | Parses function declarations
    :param raw_text:
    :return:
    """
    token = Token("reusable")
    attribs = {}
    index = 0
    scanned = ""
    while index < len(raw_text):
        char = raw_text[index]
        scanned += char
        if scanned.endswith("(") and not "function_name" in attribs:
            attribs["function_name"] = scanned.split("reusable ")[1][:-1]
            scanned = ""
        if scanned.endswith(")") and not "parameters" in attribs:
            attribs["parameters"] = []
            params_string = scanned[:-1].strip()
            if not params_string:
                scanned = ""
                index += 1
                continue
            params = [p.strip() for p in params_string.split(",")]
            for param in params:
                param_type, param_name = param.split(" ")
                attribs["parameters"].append((param_name, param_type))
            scanned = ""
        if scanned.endswith("{") and not "return_type" in attribs:
            return_type = scanned.strip().split(" ")[1]
            attribs["return_type"] = return_type
            scanned = ""
        if scanned.endswith("}") and not "code_block" in attribs:
            code_block = scanned[:-1].lstrip().rstrip()
            attribs["code_block"] = code_block
            break
        index += 1

    attribs["code_block"] = tokenize(attribs["code_block"])

    token.attributes = attribs
    remaining_text = raw_text[index + 1:]
    return remaining_text, token


def call_parser(raw_text: str) -> Tuple[str, Token]:
    """
    | Parses function calls
    :param raw_text:
    :return:
    """
    token = Token("call")
    attribs = {}
    index = 0
    scanned = ""
    while index < len(raw_text):
        char = raw_text[index]
        scanned += char
        if scanned.endswith("("):
            function_name = scanned[:-1].strip().split("call ")[1]
            attribs["function_name"] = function_name
            scanned = ""
        if scanned.endswith(")"):
            attribs["parameters"] = []
            params_string = scanned[:-1]
            if not params_string:
                index += 1
                break
            params = [p.strip() for p in params_string.split(" ")]
            for param in params:
                param_type, param_name = param.split(" ")
                attribs["parameters"] = (param_name, param_type)
            break
        index += 1

    token.attributes = attribs
    remaining_text = raw_text[index + 1:]
    return remaining_text, token


def container_parser(raw_text: str) -> Tuple[str, Token]:
    """
    | Parses variables
    :param raw_text:
    :return:
    """
    raw_text = raw_text.split("container ", 1)[1]

    token = Token("container")
    attribs = {}
    index = 0
    scanned = ""
    while index < len(raw_text):
        char = raw_text[index]
        scanned += char

        if scanned.endswith(">"):
            attribs["datatype"] = scanned.strip()
            scanned = ""

        if scanned.endswith("="):
            variable_name = scanned[:-1].strip()
            attribs["variable_name"] = variable_name
            scanned = ""

        if scanned.endswith("<<"):
            variable_name = scanned[:-2].strip()
            attribs["variable_name"] = variable_name
            scanned = ""

        if scanned.endswith(";"):
            variable_value = scanned[:-1].strip()
            tokenized_value = value_parser(variable_value)
            attribs["variable_value"] = tokenized_value
            break

        index += 1

    token.attributes = attribs
    remaining_text = raw_text[index + 1:]
    return remaining_text, token


def value_parser(raw_text: str) -> Token:
    """
    | Parses variable values
    :param raw_text:
    :return:
    """
    if raw_text.startswith('"') and raw_text.endswith('"'):
        token = Token("string")
        token.attributes["value"] = raw_text[1:-1]
        return token
    if raw_text in ["true", "false"]:
        token = Token("boolean")
        token.attributes["value"] = raw_text
        return token
    if raw_text.startswith("call "):
        token = Token("shit")
        token.attributes["value"] = raw_text.split("call ")[1]
        return token
    try:
        int(raw_text)
        token = Token("int")
        token.attributes["value"] = raw_text
        return token
    except ValueError:
        float(raw_text)
        token = Token("float")
        token.attributes["value"] = raw_text
        return token


def multipart_parser(raw_text: str) -> Tuple[str, Token]:
    """
    | Parses arrays
    :param raw_text:
    :return:
    """
    raw_text = raw_text.split("multipart ", 1)[1]

    token = Token("multipart")
    attribs = {}
    index = 0
    scanned = ""
    while index < len(raw_text):
        char = raw_text[index]
        scanned += char

        if scanned.endswith(">"):
            attribs["datatype"] = scanned.strip()
            scanned = ""

        if scanned.endswith("="):
            variable_name = scanned[:-1].strip()
            attribs["array_name"] = variable_name
            scanned = ""

        if scanned.endswith("{"):
            scanned = ""

        if scanned.endswith("}"):
            contents_string = scanned[:-1].strip()
            elements = [e.strip() for e in contents_string.split(",")]
            attribs["array_values"] = elements
            break

        index += 1

    token.attributes = attribs
    remaining_text = raw_text[index + 1:]
    return remaining_text, token


def static_parser(raw_text: str) -> Tuple[str, Token]:
    """
    | Parses constant variables and arrays, prefixed with 'static'
    :param raw_text:
    :return:
    """
    raw_text = raw_text.split("static ", 1)[1]
    data_structure, text = raw_text.split(" ", 1)
    token: Token = None
    if data_structure == "container":
        remaining_text, token = container_parser(raw_text)
    if data_structure == "multipart":
        remaining_text, token = multipart_parser(raw_text)
    token.attributes["static"] = True
    return remaining_text, token


def tokenize(content: str) -> List[Token]:
    """
    | Tokenizes a string
    :param content:
    :return:
    """
    tokens = []

    # parse text
    read = ""
    index = 0
    current_token: Token = None
    found_comment = False
    found_multiline_comment = False
    found_docstring = False

    while index < len(content):

        char = content[index]

        read += char
        read = read.lstrip()

        # identify comments
        if read.startswith("//") and not found_comment:
            found_comment = True
            index += 1
            continue

        # skip over characters until end of the comment
        if found_comment:
            if read.endswith("\n"):
                found_comment = False
                read = ""
            index += 1
            continue

        # identify multiline comments
        if read.startswith("/*") and not found_multiline_comment:
            found_multiline_comment = True
            index += 1
            continue

        # skip over characters until end of multiline comment
        if found_multiline_comment:
            if read.endswith("*/\n"):
                found_multiline_comment = False
                read = ""
            index += 1
            continue

        # identify docstrings
        if read.startswith("'''") and not found_docstring:
            found_docstring = True
            # account for both single and multiline docstrings.
            # if the docstring is multiline, then remove the \n after the first '''.
            if content[index + 1] == '\n':
                index += 1
            index += 1
            continue

        # skip over characters until end of docstring
        if found_docstring:
            if len(read) > 3 and read.endswith("'''\n"):
                found_docstring = False
                read = ""
            index += 1
            continue

        if read.endswith("\n") and not current_token:
            read = ""
            index += 1
            continue

        if read.startswith("reusable"):
            content, token = function_parser(content[index - 7:])
            tokens.append(token)
            read = ""
            index = 0
            continue

        if read.startswith("call"):
            content, token = call_parser(content[index - 3:])
            tokens.append(token)
            read = ""
            index = 0
            continue

        if read.startswith("static"):
            content, token = static_parser(content[index - 5:])
            tokens.append(token)
            read = ""
            index = 0
            continue

        index += 1

    return tokens


with open('numbergame.shit') as f:
    content = f.read()
tokens = tokenize(content)
for t in tokens:
    t.info()

print()
from converter import convert2py
convert2py(tokens)