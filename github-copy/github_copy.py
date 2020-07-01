#!/usr/bin/env python3

import os
import subprocess
import sys
import tempfile
from os import path
from pathlib import Path

import termcolor
from dulwich import porcelain
from github import Github
import argparse
import operator
import shutil

SEPARATOR = os.sep
REPOS = "repos"


def fatal_error(error):
    os.system("color")
    sys.exit(termcolor.colored("ERROR: " + error, "red"))


def get_repos(prefix, operation, num_repos, org):
    repos = []
    for repo in g.get_organization(org).get_repos(type="private"):
        if repo.name.startswith(prefix):
            repos.append(repo)

    matcher = "exactly"
    if operation == operator.gt:
        matcher = "at least"

    if not operation(len(repos), num_repos):
        fatal_error(
            f'prefix "{prefix}" must match {matcher} {num_repos} repositories, but matches {repos}'
        )

    return repos


def switch_branch(dulwich_repo, branch_name):
    """ Switch current branch to branch_name """
    branch = bytes("refs" + SEPARATOR + "heads/" + branch_name, encoding="utf8")
    if branch in dulwich_repo:
        dulwich_repo.reset_index(dulwich_repo[branch].tree)
    else:
        raise Exception(
            'branch "'
            + branch_name
            + '" does not exist for repo "'
            + dulwich_repo.path
            + '"'
        )
    dulwich_repo.refs.set_symbolic_ref(b"HEAD", branch)


def safe_push(github_repo, dulwich_repo, branch):
    """ Push if branch doesn't already exist in remote """
    if any(b.name == branch for b in github_repo.get_branches()):
        fatal_error(
            'Branch "'
            + branch
            + '" already exists for '
            + REPOS
            + 'itory "'
            + github_repo.name
            + '"'
        )
    try:
        # Force push seems to be required by dulwich, but we check for the branch existing beforehand
        porcelain.push(dulwich_repo, refspecs=branch, force=True)
    except AttributeError as e:
        # Ignore failed push
        if e.__str__() != "'NoneType' object has no attribute 'encode'":
            fatal_error(e)
    except Exception as e:
        fatal_error(e)


parser = argparse.ArgumentParser(
    description="Copy files from one GitHub repo to other(s). Allows for transforming the files using a script during the copy process."
)
parser.add_argument(
    "--source-prefix",
    "-sp",
    dest="sourcePrefix",
    type=str,
    help="The name of the source repository to take changes from",
)
parser.add_argument(
    "--source-directory",
    "-sd",
    dest="sourceDirectory",
    type=str,
    help="The source directory to take changes from",
)
parser.add_argument(
    "--source-branch",
    "-sb",
    dest="sourceBranch",
    type=str,
    help="The branch to use in the source repository",
    default="master",
)
parser.add_argument(
    "--destination-prefix",
    "-dp",
    dest="destinationPrefix",
    type=str,
    help="The prefix to use to filter destination repositories where changes will be merged to",
)
parser.add_argument(
    "--destination-branch",
    "-db",
    dest="destinationBranch",
    type=str,
    help="The branch to modify in the destination repositories",
    default="development",
)
parser.add_argument(
    "--temporary-branch",
    "-tb",
    dest="temporaryBranch",
    type=str,
    help="The branch to use for the pull request we will create",
    default="temporary-automated-branch",
)
parser.add_argument(
    "--file-prefix",
    dest="filePrefix",
    type=str,
    help="The file prefix to filter by when copying files",
    default="",
)
parser.add_argument(
    "--transformer",
    dest="script",
    type=str,
    help=(
        "The transformation script to use to convert the files to a new format before copying"
    ),
    default="development",
)
parser.add_argument(
    "--transformer-args",
    dest="scriptParameters",
    type=str,
    help="The arguments to the transformation script",
    default="development",
)
parser.add_argument(
    "--source-org",
    dest="sourceOrg",
    type=str,
    help="The GitHub org for the source repository",
    default="GSA",
)
parser.add_argument(
    "--destination-org",
    dest="destinationOrg",
    type=str,
    help="The GitHub org for the destination repositories",
    default="GSA",
)
parser.add_argument(
    "--dry-run",
    action="store_true",
    dest="dryRun",
    help="Indicates no changes should be made, but should only print what changes would be made",
    default=False,
)

args = parser.parse_args()

if args.sourceDirectory is not None and args.sourcePrefix is not None:
    fatal_error("cannot specify both a source-directory and a source-prefix")

if "GITHUB_TOKEN" not in os.environ:
    fatal_error("you must specify a GITHUB_TOKEN environment variable")
g = Github(os.environ["GITHUB_TOKEN"])
destinationRepositories = get_repos(
    args.destinationPrefix, operator.ge, 1, args.destinationOrg
)

temp_dir = tempfile.gettempdir() + SEPARATOR + REPOS + SEPARATOR
shutil.rmtree(temp_dir, ignore_errors=True)
Path(temp_dir).mkdir(parents=True, exist_ok=True)

if args.sourceDirectory is None:
    sourceRepositories = get_repos(args.sourcePrefix, operator.eq, 1, args.sourceOrg)
    source_path = temp_dir + sourceRepositories[0].name
    dulwich_repo = porcelain.clone(sourceRepositories[0].ssh_url, source_path)
    switch_branch(dulwich_repo, args.sourceBranch)
else:
    source_path = args.sourceDirectory

for github_repo in destinationRepositories:
    destination_path = temp_dir + github_repo.name
    dulwich_repo = porcelain.clone(github_repo.ssh_url, destination_path)

    porcelain.branch_create(destination_path, args.temporaryBranch)
    switch_branch(dulwich_repo, args.temporaryBranch)

    if not path.exists(args.script):
        args.script = path.join("transformers", args.script + ".py")

    process = subprocess.Popen(
        [
            "python3 "
            + os.getcwd()
            + SEPARATOR
            + args.script
            + " "
            + args.scriptParameters
            + " --source-directory="
            + source_path
            + " --destination-directory="
            + destination_path
        ],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    output, err = process.communicate()
    sys.stdout.write(output)
    sys.stderr.write(err)

    status = porcelain.status(dulwich_repo)

    for untracked in status.untracked:
        porcelain.add(dulwich_repo, destination_path + SEPARATOR + untracked)

    for unstaged in status.unstaged:
        porcelain.add(dulwich_repo, destination_path + SEPARATOR + unstaged)

    porcelain.commit(
        dulwich_repo,
        "automated change",
        "grace-production <cloud.services.support+github_production@gsa.gov>",
    )

    logging_verb1 = "Would copy"
    logging_verb2 = "would be"
    logging_color = "yellow"
    if not args.dryRun:
        logging_verb1 = "Copied"
        logging_verb2 = "were"
        logging_color = "green"
        safe_push(github_repo, dulwich_repo, args.temporaryBranch)
        print(
            termcolor.colored("Successfully pushed to " + github_repo.ssh_url, "green")
        )

        github_repo.create_pull(
            title="automated change",
            body="automated change",
            head=args.temporaryBranch,
            base=args.destinationBranch,
        )

    for file in status.unstaged + status.untracked:
        print(
            termcolor.colored(
                f"{logging_verb1} '{file}' from '{source_path}' to '{destination_path}'",
                logging_color,
            )
        )

    if len(status.untracked + status.unstaged) == 0:
        print(termcolor.colored("No changes " + logging_verb2 + " made", logging_color))
