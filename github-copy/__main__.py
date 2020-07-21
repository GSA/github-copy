#!/usr/bin/env python3

import os
import subprocess
import sys
import tempfile
from os import path
from pathlib import Path

import termcolor
from dulwich import porcelain, index
from dulwich.client import (
    HttpGitClient,
    SSHGitClient,
    LocalGitClient,
    get_transport_and_path,
)
from dulwich.repo import Repo
from github import Github
import operator
import shutil
from .arg_parser import ArgParser

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
    branch = bytes("refs/heads/" + branch_name, encoding="utf8")
    if branch in dulwich_repo:
        dulwich_repo.reset_index(dulwich_repo[branch].tree)
    else:
        raise Exception(
            f'branch "{branch_name}" does not exist for repo "{dulwich_repo.path}"'
        )
    dulwich_repo.refs.set_symbolic_ref(b"HEAD", branch)


def safe_push(github_repo, dulwich_repo, branch):
    """ Push if branch doesn't already exist in remote """
    # TODO check if to branch already exists
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


args = ArgParser().parse_github_copy_args().parse_args()

if args.sourceDirectory is not None and args.sourcePrefix is not None:
    fatal_error("cannot specify both a source-directory and a source-prefix")

if "GITHUB_TOKEN" not in os.environ:
    fatal_error("you must specify a GITHUB_TOKEN environment variable")
g = Github(os.environ["GITHUB_TOKEN"])
destinationRepositories = get_repos(
    args.destinationPrefix, operator.ge, 1, args.destinationOrg
)

if args.sourcePrefix == "grace-actions" and args.actionType == "":
    fatal_error("action-type parameter is required when running grace-actions")


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

    os.system("pushd " + destination_path) 
    os.system("git fetch origin " + args.destinationBranch)
    os.system("git checkout " + args.destinationBranch)
    os.system("popd")
    
    porcelain.branch_create(destination_path, args.temporaryBranch)
    switch_branch(dulwich_repo, args.temporaryBranch)

    if args.sourcePrefix == "grace-actions":
        args.script = "python3 " + path.join(source_path, "actions", "run.py")

        # TODO allow relative paths for the request.json file
        args.scriptParameters = args.scriptParameters + f" --action {args.actionType}"
    else:
        args.script = path.join("~/.local/bin", args.script + ".py")

    command = f"{args.script} {args.scriptParameters} --src-dir={source_path} --dst-dir={destination_path}"
    # FIXME fix race condition with transformer for print statements
    termcolor.colored(f"Running transformer with command '{command}'", "yellow")
    process = subprocess.Popen(
        [command],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    output, err = process.communicate()
    sys.stdout.write(output)
    sys.stderr.write(err)

    status = porcelain.status(dulwich_repo)

    dulwich_repo.stage(status.untracked)
    dulwich_repo.stage(status.unstaged)

    porcelain.commit(
        dulwich_repo,
        args.pullRequestName,
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
            termcolor.colored(f"Successfully pushed to {github_repo.ssh_url}", "green")
        )

        github_repo.create_pull(
            title=args.pullRequestName,
            body=args.pullRequestName,
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
        print(termcolor.colored(f"No changes {logging_verb2} made", logging_color))
