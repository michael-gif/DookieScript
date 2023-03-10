import argparse

from translator import translate_to_python
from tokenizer import tokenize

parser = argparse.ArgumentParser()
parser.add_argument('-dks', '--dks_file', metavar='<path>', required=True)
parser.add_argument('-out', '--out_file', metavar='<path>')
args = vars(parser.parse_args())

dks_file = args['dks_file']
if not dks_file.endswith(".dks"):
    print(f"[ERROR] The specified file '{dks_file}' is not a dookiescript file")
    quit()

try:
    with open(args['dks_file']) as f:
        content = f.read()
    if not content.endswith("\n"):
        content = content + "\n"
    tokens = tokenize(content)
    if args['out_file']:
        translate_to_python(tokens, args['out_file'])
    else:
        translate_to_python(tokens, dks_file[:-4] + ".py")
except FileNotFoundError:
    print(f"[INFO] Could not find dks file '{dks_file}'")
