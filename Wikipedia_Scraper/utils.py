import os
import re
from shutil import copyfile
import csv

def sanitize_text(d):
    RE = re.compile(r"""\[\[(File|Category):[\s\S]+\]\]|
        \[\[[^|^\]]+\||
        \[\[|
        \]\]|
        \'{2,5}|
        (<s>|<!--)[\s\S]+(</s>|-->)|
        {{[\s\S\n]+?}}|
        <ref>[\s\S]+</ref>|
        ={1,6}""", re.VERBOSE)
    x = RE.sub('', d)
    while '[' in x:
        startidx = x.index('[')
        endidx = x.rindex(']')
        x = x[:startidx] + x[endidx + 1:]
    x = x.replace('†', "").strip()
    return x


def sanitize_digit(d):
    try:
        x = ''.join(c for c in d if c.isdigit())
        if x:
            return str(int(x))
        else:
            return "0"
    except:
        return "0"


def move_to_final(filename):
    file_name = filename.split('/')[-1]
    parent_dir_path = os.path.dirname(os.path.realpath(__file__))
    if '/var/task' in parent_dir_path:
        parent_dir_path = os.getcwd()
    output_file_path = os.path.join(parent_dir_path, "output", file_name)
    final_file_path = os.path.join(parent_dir_path, "final", file_name)
    output_size = os.path.getsize(output_file_path)
    if os.path.exists(final_file_path):
        final_size = os.path.getsize(final_file_path)
        if output_size > 0.9 * final_size:
            copyfile(output_file_path, final_file_path)
            print(f"File exists. Updated {file_name}.")
    else:
        copyfile(output_file_path, final_file_path)
        print(f"File doesn't exist. Created {file_name}.")


def cleanup(filename):
    parent_dir_path = os.path.dirname(os.path.realpath(__file__))
    if '/var/task' in parent_dir_path:
        parent_dir_path = os.getcwd()
    filepath = os.path.join(parent_dir_path, filename)
    if os.path.exists(filepath):
        os.remove(filepath)


def write_record_to_output(record, filename):
    fields = record.keys()
    parent_dir_path = os.path.dirname(os.path.realpath(__file__))
    if '/var/task' in parent_dir_path:
        parent_dir_path = os.getcwd()
    filepath = os.path.join(parent_dir_path, filename)
    mode = 'a' if os.path.exists(filepath) else "w"
    with open(filepath, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore', quoting=csv.QUOTE_ALL)
        if mode == "w":
            writer.writeheader()
        writer.writerow(record)
