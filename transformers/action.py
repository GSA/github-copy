import argparse
import json
import os
from os import path
from jinja2 import Template

TRANSFORM_SETTINGS_FILE = "transform-settings.j2"

parser = argparse.ArgumentParser(
    description="Copy j2 files and transform them to tf files."
)
parser.add_argument(
    "--source-directory",
    "-src",
    dest="sourceDirectory",
    type=str,
    help="The name of the source directory to take changes from",
)
parser.add_argument(
    "--destination-directory",
    "-dst",
    dest="destinationDirectory",
    type=str,
    help="The name of the destination directory to move changes to",
)
parser.add_argument("--action", dest="action", type=str, help="The action to execute")
parser.add_argument(
    "--request-file",
    "-req",
    dest="requestFile",
    type=str,
    help="The file containing metadata about this particular request such as which service now ticket it corresponds to",
)

args = parser.parse_args()

action_dir = path.join(args.sourceDirectory, "actions", args.action)
request = json.loads(open(args.requestFile).read())
for file in os.listdir(action_dir):
    transform_settings_json = open(
        path.join(action_dir, TRANSFORM_SETTINGS_FILE)
    ).read()
    transform_settings_template = Template(transform_settings_json)
    transform_settings_file = transform_settings_template.render(request)
    if file.endswith(".j2") and file != TRANSFORM_SETTINGS_FILE:
        template = Template(open(path.join(action_dir, file), "r").read())

        assert "TICKET_NUMBER" in request
        # check if the transform-settings.js file indicates the file should be renamed
        if file in transform_settings_file:
            transform_settings = json.loads(transform_settings_file)
            new_file_name = transform_settings[file]
        # by default append the ticket number to the file name
        else:
            new_file_name = (
                path.splitext(file)[0] + "_" + request["TICKET_NUMBER"] + ".tf"
            )

        to_path = path.join(args.destinationDirectory, new_file_name)
        rendered_template = template.render(request)
        open(to_path, "w").write(rendered_template)
