#-------------------------------------------------------------------------------
#  licensetag.py - this file is part of licensetag: add/update licence script
#-------------------------------------------------------------------------------
#  Author:        Marco Giorgini, marco.giorgini@gmail.com
#  Creation date: 2025-07
#  Last Modified: 2025-07-22 23:23:44
#-------------------------------------------------------------------------------
#  Version:       0.7.5
#-------------------------------------------------------------------------------
#  MIT License
#
#  Copyright (c) 2025 Marco Giorgini
#  
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#  
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#-------------------------------------------------------------------------------

import os
import re
import argparse
from pathlib import Path
from string import Template
from datetime import datetime, timedelta
from collections import Counter

EXCLUDED_DIRS = {"templates", "build", ".git"}

def get_template_for_extension(base, ext, tail=False):
    suffix = "_tail" if tail else ""
    template_path = Path(f"{base}{suffix}{ext}")
    if template_path.exists():
        return template_path
    fallback = Path(f"{base}{suffix}.txt")
    if fallback.exists():
        return fallback
    if not tail:
        fallback = Path(f"generic{suffix}.txt")
        if fallback.exists():
            return fallback
    template_path = Path(f"templates/{base}{suffix}{ext}")
    if template_path.exists():
        return template_path
    fallback = Path(f"templates/{base}{suffix}.txt")
    if fallback.exists():
        return fallback
    if not tail:
        fallback = Path(f"templates/generic{suffix}.txt")
        if fallback.exists():
            return fallback
    return None  # Tail template is optional

def load_template(template_path, name, substitutions):
    with open(template_path) as f:
        content = Template(f.read())
    substitutions["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    substitutions["filename"] = name
    str = content.safe_substitute(substitutions)
    if template_path.suffix == ".txt":
        if name.endswith(".py"):
            return str.replace("//","#").replace("http:#","http://")
    return str

def update_version(file_path, new_version):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for i, line in enumerate(lines[:20]): 
        if "Version:" in line:
            indent = line[:line.index("Version")]
            match = re.search(r"Version:\s*([\d.]+)", line)
            if match:
                current_version = match.group(1).strip()
                if current_version != new_version:
                    new_line = re.sub(
                        r"(Version:\s*)[\d.]+",
                        lambda m: m.group(1) + new_version,
                        line
                    )
                    lines[i] = new_line
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(lines)
                    return True
            break
    return False  # no changes

def update_last_modified(file_path, max_age_minutes=10):
    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
    now = datetime.now()

    if now - mtime > timedelta(minutes=max_age_minutes):
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines[:20]):
        if "Last Modified:" in line:
            indent = line[:line.index("Last Modified:")]
            new_line = f"{indent}Last Modified: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            if lines[i] != new_line:
                lines[i] = new_line
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                return True
            break

    return False

def is_comment_line(line):
    stripped = line.strip()
    return any(stripped.startswith(prefix) for prefix in ("#", "//", "--", ";"))

def has_license_check(line):
    if(("LICENSE" in line.upper()) or ("COPYRIGHT" in line.upper())):
        return True
    return False

def has_license(lines):
    for line in lines[:20]:  # look only at the top section
        if is_comment_line(line) and has_license_check(line):
            return True
        if line.strip() and not is_comment_line(line):
            break  # stop at first non-comment line
    return False

def add_or_update_footer(file_path, footer_text, update=False):
    if footer_text is None:
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find the footer block (from end) if present
    footer_start = None
    commented = False
    footer_license_found = False
    for i in reversed(range(len(lines))):
        if not commented and lines[i].strip() == "":
            continue
        elif is_comment_line(lines[i]):
            commented = True
            if has_license_check(lines[i]):
                footer_license_found = True                
            continue
        elif footer_license_found:
            if commented:
                footer_start = i+1
            break

    changed = False
    if footer_start is not None and update:
        # Remove existing footer block
        i = footer_start
        while i < len(lines) and is_comment_line(lines[i]):
            i += 1
        lines = lines[:footer_start-1] + lines[i:]
        changed = True

    if footer_start is None or update:
        # Add new footer block
        if not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        if footer_text.strip() != "":
            lines.append("\n" + footer_text.strip() + "\n")
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True

    return False
    
def add_or_update_license(file_path, license_text, update=False):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    changed = False

    if has_license(lines) and update:
        new_lines = []
        in_header = True
        license_found = False

        for i, line in enumerate(lines):
            if in_header and is_comment_line(line):
                if has_license_check(line):
                    license_found = True
                continue
            else:
                if in_header:
                    in_header = False
                    new_lines = lines[i+1:]
                    break

        if license_found:
            lines = new_lines
            changed = True

    if not has_license(lines) or changed:        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(license_text.strip() + "\n\n" + "".join(lines))
        return True

    return False

def process_folder(folder, template_base, extensions, substitutions, update, verbose):
    files_changed = 0
    change_counter = Counter()
    if verbose:
        print("Scanning:")
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for name in files:
            for ext in extensions:
                if name.endswith(ext):
                    head_template = get_template_for_extension(template_base, ext)
                    tail_template = get_template_for_extension(template_base, ext, tail=True)
                    if head_template is None:
                        continue 
                    license_text = load_template(head_template, name, substitutions)
                    footer_text = load_template(tail_template, name, substitutions) if tail_template else None
                    
                    file_path = os.path.join(root, name)
                    
                    changed_head = False
                    changed_tail = False
                    updated = False
                    if license_text and add_or_update_license(file_path, license_text, update):
                        changed_head = True
                    if tail_template and add_or_update_footer(file_path, footer_text, update):
                        changed_tail = True
                    if update_last_modified(file_path, max_age_minutes=10):
                        updated = True
                    if not changed_head and not changed_tail:
                        if update_version(file_path, substitutions["version"]):
                            updated_version = True
                    
                    if changed_head or changed_head or updated or updated_version:
                        if verbose:
                            if changed_head or changed_tail:
                                print(f"{file_path} modified")
                            else:
                                if updated or updated_version:
                                    print(f"{file_path} updated")                                   
                        change_counter[ext] += 1
                    break  
    print("Summary:")
    if change_counter:
        for ext, count in change_counter.items():
            print(f"  {count} file(s) updated with extension '{ext}'")
    else:
        print("  No files were updated.")

def main():
    parser = argparse.ArgumentParser(description="Add or update license headers.")
    
    parser.add_argument("-f","--folder", help="source files folder",required=True)
    
    parser.add_argument("-t","--template", help="base name of the template, e.g. 'mit' -> mit.py, mit.c etc.", required=True)
    
    parser.add_argument("-a","--author", help="$author variable in template",required=True)
    parser.add_argument("-m","--authoremail", help="$authoremail variable in template")
    parser.add_argument("-v","--version", help="$version variable in template", default="1.0")
    parser.add_argument("-p","--project", help="$project variable in template")
    parser.add_argument("-u","--projecturl", help="$projecturl variable in template")

    parser.add_argument("-y","--year",help="$year variable in template", default=datetime.now().strftime("%Y"))
    parser.add_argument("-cd","--creationdate",help="$creationdate variable in template", default=datetime.now().strftime("%Y-%m"))
    
    parser.add_argument("-x","--extensions",help="source file extension to consider", nargs="+", default=[".c",".h",".cc",".cpp",".py"])
    
    parser.add_argument("-d","--exclude-dirs", nargs="+", default=[], help="subdirectories to exclude from recursion")
    
    parser.add_argument("--verbose", help="show changed file names", action="store_true")
    parser.add_argument("--update", help="update files with a previous license", action="store_true")
    args = parser.parse_args()

    substitutions = {
        "author": args.author,
        "authoremail": args.authoremail,
        "project": args.project,
        "projecturl": args.projecturl,
        "year": args.year,
        "version": args.version,
        "creationdate": args.creationdate
    }
    
    if args.exclude_dirs:
        EXCLUDED_DIRS = set(args.exclude_dirs)

    process_folder(args.folder, args.template, args.extensions, substitutions, args.update, args.verbose)

if __name__ == "__main__":
    main()
