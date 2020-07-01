import argparse
import os
from os import path
from shutil import copyfile

parser = argparse.ArgumentParser(
    description="Copy files with only the specified prefix."
)
parser.add_argument(
    "--source-directory",
    dest="sourceDirectory",
    type=str,
    help="The name of the source repository to take changes from",
)
parser.add_argument(
    "--destination-directory",
    dest="destinationDirectory",
    type=str,
    help="The branch to use in the source repository",
)
parser.add_argument(
    "--file-prefix",
    dest="filePrefix",
    type=str,
    help="The branch to use in the source repository",
)

args = parser.parse_args()
for subdir, dirs, files in os.walk(args.sourceDirectory):
    for file in files:
        from_path = os.path.join(subdir, file)
        if file.startswith(args.filePrefix):
            commonPath = path.commonprefix([from_path, args.destinationDirectory])
            additionalPath = from_path.replace(commonPath, "")
            to_repo = args.destinationDirectory.split("/")[3]
            to_path = (
                "/tmp/repos/"
                + to_repo
                + "/"
                + "/".join(from_path.split("/")[4:-1])
                + "/"
            )
            os.makedirs(to_path, exist_ok=True)
            copyfile(from_path, to_path + file)
