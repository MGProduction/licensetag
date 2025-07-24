# licensetag
a python script to add/update license/version/last modified and other info to a set of source files

it's possible to provide a different version of the same template based on source file extension creating different files with each extension (while the .txt is the catchall)

```
options:
  -h, --help            show this help message and exit
  -f FOLDER, --folder FOLDER
                        source files folder
  -t TEMPLATE, --template TEMPLATE
                        base name of the template, e.g. 'mit' -> mit.py, mit.c etc.
  -a AUTHOR, --author AUTHOR
                        $author variable in template
  -m AUTHOREMAIL, --authoremail AUTHOREMAIL
                        $authoremail variable in template
  -v VERSION, --version VERSION
                        $version variable in template
  -p PROJECT, --project PROJECT
                        $project variable in template
  --verbose             show changed file names
  -u PROJECTURL, --projecturl PROJECTURL
                        $projecturl variable in template
  -y YEAR, --year YEAR  $year variable in template
  -cd CREATIONDATE, --creationdate CREATIONDATE
                        $creationdate variable in template
  -x EXTENSIONS [EXTENSIONS ...], --extensions EXTENSIONS [EXTENSIONS ...]
                        source file extension to consider
  -d EXCLUDE_DIRS [EXCLUDE_DIRS ...], --exclude-dirs EXCLUDE_DIRS [EXCLUDE_DIRS ...]
                        subdirectories to exclude from recursion
  --update              update files with a previous license
```

- you can have a template file or a template file AND a template_tail file (to have license splitted in two parts)
- you can update just Last Modified: / Version parts (using this tool again on the same source codes. Last Modified will be changed only on recent modified file in folders)
- header / footer of source codes are scanned to seek (in starting/ending position - with comments) **license** or **copyright** keywords

**use at your own risk** - backup your code before playing with this tool
