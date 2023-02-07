from token import Token
from typing import Tuple, List


def include_parser(raw_text: str) -> Tuple[str, Token]:
    """
    | Parses imports
    :param raw_text:
    :return:
    """
    if raw_text.lstrip().startswith("include "):
        raw_text = raw_text.lstrip().split("include ", 1)[1]
    else:
        return "", None
    token = Token("include")
    attribs = {}
    index = 0
    scanned = ""
    while index < len(raw_text):
        char = raw_text[index]
        scanned += char
        if scanned.endswith("\n") and "module_name" not in attribs:
            attribs["module_name"] = scanned[:-1]
            break
        index += 1

    token.attributes = attribs
    remaining_text = raw_text[index + 1:]
    return remaining_text, token


def reusable_parser(raw_text: str) -> Tuple[str, Token]:
    """
    | Parses function declarations
    :param raw_text:
    :return:
    """
    if raw_text.lstrip().startswith("reusable "):
        raw_text = raw_text.lstrip().split("reusable ", 1)[1]
    else:
        return "", None
    token = Token("reusable")
    attribs = {}
    index = 0
    scanned = ""
    bracket_counter = 0
    found_code_block = False
    while index < len(raw_text):
        char = raw_text[index]
        scanned += char
        if scanned.endswith("(") and not "function_name" in attribs:
            attribs["function_name"] = scanned[:-1]
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
        if scanned.endswith("{"):
            if "return_type" not in attribs:
                return_type = scanned.strip().split(" ")[1]
                attribs["return_type"] = return_type
                scanned = ""
            found_code_block = True
            bracket_counter += 1
        if scanned.endswith("}"):
            bracket_counter -= 1
        if found_code_block and not bracket_counter and not "code_block" in attribs:
            code_block = scanned[:-1].lstrip()
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
    if raw_text.lstrip().startswith("call "):
        raw_text = raw_text.lstrip().split("call ", 1)[1]
    else:
        return "", None
    token = Token("call")
    attribs = {}
    index = 0
    scanned = ""
    bracket_counter = 0
    found_bracket = False
    while index < len(raw_text):
        char = raw_text[index]
        scanned += char
        if scanned.endswith("("):
            if not found_bracket:
                function_name = scanned[:-1].strip()
                attribs["function_name"] = function_name
                scanned = ""
            bracket_counter += 1
            found_bracket = True
        if scanned.endswith(")"):
            bracket_counter -= 1
        if found_bracket and not bracket_counter:
            found_bracket = False
            attribs["parameters"] = []
            params_string = scanned[:-1]
            if not params_string:
                index += 1
                continue
            params = [p.strip() for p in params_string.split(",")]
            for param in params:
                attribs["parameters"].append(param)
        if scanned.endswith("\n"):
            break
        index += 1

    token.attributes = attribs
    remaining_text = raw_text[index + 1:]
    return remaining_text, token


def query_parser(raw_text: str) -> Tuple[str, Token]:
    """
    | Parses if statements
    :param raw_text:
    :return:
    """
    if raw_text.lstrip().startswith("query "):
        raw_text = raw_text.lstrip().split("query ", 1)[1]
    else:
        return "", None
    token = Token("query")
    attribs = {}
    index = 0
    scanned = ""
    found_code_block = False
    bracket_counter = 0
    while index < len(raw_text):
        char = raw_text[index]
        scanned += char
        scanned = scanned.lstrip()
        if scanned.endswith(")") and not "condition" in attribs:
            condition = scanned[1:-1]
            attribs["condition"] = condition
            scanned = ""
        if scanned.endswith("executes {"):
            scanned = ""
            found_code_block = True
            bracket_counter += 1
        if scanned.endswith("{"):
            bracket_counter += 1
        if scanned.endswith("}"):
            bracket_counter -= 1
        if found_code_block and not bracket_counter:
            code_block = scanned[:-1]
            attribs["code_block"] = code_block
            scanned = ""
            break
        index += 1

    result = tokenize(attribs["code_block"])
    if result:
        attribs["code_block"] = result
    else:
        attribs["code_block"] = [attribs["code_block"]]
    token.attributes = attribs
    remaining_text = raw_text[index + 1:]
    return remaining_text, token


def repeat_parser(raw_text: str) -> Tuple[str, Token]:
    """
    | Parses for loops
    :param raw_text:
    :return:
    """
    if raw_text.lstrip().startswith("repeat "):
        raw_text = raw_text.lstrip().split("repeat ", 1)[1]
    else:
        return "", None

    if raw_text.startswith("query "):
        text, token = repeat_query_parser("repeat " + raw_text)
        return text, token

    token = Token("repeat")
    attribs = {}
    index = 0
    scanned = ""
    found_code_block = False
    bracket_counter = 0
    while index < len(raw_text):
        char = raw_text[index]
        scanned += char
        scanned = scanned.lstrip()
        if scanned.startswith("(") and scanned.endswith(")") and not "start_stop_step" in attribs:
            start_stop_step = scanned[:-1]
            parts = [p.strip() for p in start_stop_step.split(",")]
            start = parts[0].split(">")[1].strip()
            stop = parts[1].split(">")[1].strip()
            step = parts[2]
            iterator_name, iterator_start_value = [i.strip() for i in start.split("=")]
            iterator_stop_value = stop.split("=")[1].strip()
            iterator_step_value = step.split(iterator_name)[1].strip()
            attribs["start_stop_step"] = [iterator_name, iterator_start_value, iterator_stop_value, iterator_step_value]
            scanned = ""
        if scanned.endswith("{"):
            bracket_counter += 1
            found_code_block = True
        if scanned.endswith("}"):
            bracket_counter -= 1
        if found_code_block and not bracket_counter:
            code_block = scanned[:-1]
            attribs["code_block"] = code_block
            break
        index += 1

    attribs["code_block"] = tokenize(attribs["code_block"])
    token.attributes = attribs
    remaining_text = raw_text[index + 1:]
    return remaining_text, token


def repeat_query_parser(raw_text: str) -> Tuple[str, Token]:
    """
    | Parses while loops
    :param raw_text:
    :return:
    """
    if raw_text.lstrip().startswith("repeat query "):
        raw_text = raw_text.lstrip().split("query ", 1)[1]
    else:
        return "", None
    token = Token("repeat_query")
    attribs = {}
    index = 0
    scanned = ""
    found_code_block = False
    bracket_counter = 0
    while index < len(raw_text):
        char = raw_text[index]
        scanned += char
        scanned = scanned.lstrip()
        if scanned.startswith("(") and scanned.endswith(")") and not "condition" in attribs:
            condition = scanned[1:-1]
            attribs["condition"] = condition
            scanned = ""
        if scanned.endswith("{"):
            bracket_counter += 1
            found_code_block = True
        if scanned.endswith("}"):
            bracket_counter -= 1
        if found_code_block and not bracket_counter:
            code_block = scanned[:-1]
            attribs["code_block"] = code_block
            break
        index += 1

    attribs["code_block"] = tokenize(attribs["code_block"])
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
        token.attributes["value"] = f'"{raw_text[1:-1]}"'
        return token
    if raw_text in ["true", "false"]:
        token = Token("boolean")
        token.attributes["value"] = raw_text
        return token
    if raw_text.startswith("call "):
        text, token = call_parser(raw_text)
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

        if scanned.endswith("\n"):
            variable_value = scanned[:-1].strip()
            tokenized_value = value_parser(variable_value)
            attribs["variable_value"] = tokenized_value
            break

        index += 1

    token.attributes = attribs
    remaining_text = raw_text[index + 1:]
    return remaining_text, token


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
    if raw_text.lstrip().startswith("static "):
        raw_text = raw_text.lstrip().split("static ", 1)[1]
    else:
        return "", None
    data_structure, text = raw_text.split(" ", 1)
    token: Token = None
    if data_structure == "container":
        remaining_text, token = container_parser(raw_text)
    if data_structure == "multipart":
        remaining_text, token = multipart_parser(raw_text)
    token.attributes["static"] = True
    return remaining_text, token


def return_parser(raw_text: str) -> Tuple[str, Token]:
    """
    | Parses return statements
    :param raw_text:
    :return:
    """
    if raw_text.lstrip().startswith("return "):
        raw_text = raw_text.lstrip().split("return ", 1)[1]
    else:
        return "", None

    token = Token("return")
    attribs = {}
    index = 0
    scanned = ""
    while index < len(raw_text):
        char = raw_text[index]
        scanned += char
        if scanned.endswith("\n") and not "return_value" in attribs:
            attribs["return_value"] = scanned[:-1]
            break
        index += 1

    attribs["return_value"] = tokenize(attribs["return_value"])
    token.attributes = attribs
    remaining_text = raw_text[index + 1:]
    return remaining_text, token


def tokenize(content: str) -> List[Token]:
    """
    | Tokenizes a code block
    | Explanation:
    | Loop through each character of the given string, adding every character to a variable called 'scanned'. When the
    | variable contains a recognisable keyword such as 'reusable', 'static' etc, get the appropiate parser for that
    | keyword, and give the parser the rest of the string from the current index to the end. The parser then parses the
    | content, and returns the token it generated.
    :param content:
    :return:
    """
    tokens = []
    parsers = {
        'include ': include_parser,
        'reusable ': reusable_parser,
        'call ': call_parser,
        'static ': static_parser,
        'repeat ': repeat_parser,
        'query ': query_parser,
        'return ': return_parser
    }
    parser_keys = list(parsers.keys())

    # parse text
    scanned = ""
    index = 0
    found_comment = False
    found_multiline_comment = False
    found_docstring = False

    while index < len(content):

        char = content[index]
        scanned += char
        scanned = scanned.lstrip()  # remove tabs and spaces before the text

        # identify comments
        if scanned.startswith("//") and not found_comment:
            found_comment = True
            index += 1
            continue

        # skip over characters until end of the comment
        if found_comment:
            if scanned.endswith("\n"):
                found_comment = False
                scanned = ""
            index += 1
            continue

        # identify multiline comments
        if scanned.startswith("/*") and not found_multiline_comment:
            found_multiline_comment = True
            index += 1
            continue

        # skip over characters until end of multiline comment
        if found_multiline_comment:
            if scanned.endswith("*/\n"):
                found_multiline_comment = False
                scanned = ""
            index += 1
            continue

        # identify docstrings
        if scanned.startswith("'''") and not found_docstring:
            found_docstring = True
            # account for both single and multiline docstrings.
            # if the docstring is multiline, then remove the \n after the first '''.
            if content[index + 1] == '\n':
                index += 1
            index += 1
            continue

        # skip over characters until end of docstring
        if found_docstring:
            if len(scanned) > 3 and scanned.endswith("'''\n"):
                found_docstring = False
                scanned = ""
            index += 1
            continue

        if scanned.endswith("return;\n") or scanned.endswith("return\n"):
            text, token = parsers["return "]("return \n")
            if token:
                content = text
                tokens.append(token)
                scanned = ""
                index = 0
                continue

        # if the end of a line is found, reset the scanned variable and continue
        if scanned.endswith("\n"):
            scanned = ""
            index += 1
            continue

        # check the characters already scanned to see if they match a keyword, if they do, call the relevant parser
        for key in parser_keys:
            if scanned.startswith(key):
                text, token = parsers[key](key + content[index + 1:])
                if token:
                    content = text
                    tokens.append(token)
                    scanned = ""
                    index = 0
                    continue

        index += 1

    return tokens
