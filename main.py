import argparse

from translator import translate_to_python
from tokenizer import tokenize

parser = argparse.ArgumentParser()
parser.add_argument('-dds', '--dds_file', required=True)
args = vars(parser.parse_args())

dds_file = args['dds_file']
if not dds_file.endswith(".dds"):
    print(f"[ERROR] The specified file '{dds_file}' is not a doodooscript file")
    quit()

try:
    with open(args['dds_file']) as f:
        content = f.read()
    if not content.endswith("\n"):
        content = content + "\n"
    tokens = tokenize(content)
    # for t in tokens:
    #     t.info()
    # print(tokens[1].attributes["code_block"][0].info())
    translate_to_python(tokens, dds_file[:-4] + ".py")
except FileNotFoundError:
    print(f"[INFO] Could not find dds file '{dds_file}'")
