# GitHub Copy

## Repository contents

The `github_copy.py` tool allows syncing of files from one GitHub repository to another. It also allows calling another script to perform transformations on the files before creating a pull request to send the changes to thier new location.

## Installation

Currently supports Linux and Windows Subsystem for Linux (WSL).

1. Install your [GitHub ssh key](https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) under `~/.ssh/.id_rsa`
2. Set your [GitHub token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line) with `export GITHUB_TOKEN=[YOUR_GITHUB_TOKEN]`

## Examples

Example of copying the magefile from "g-\*" to "grace-customer\*":

```
python3 github_copy.py --source-prefix=g- --destination-prefix=grace-customer --destination-branch="master" --source-branch="master" --transformer=prefix --transformer-args="--file-prefix=magefile"
```

Dry-run mode allows viewing what changes would occur without actually changing the remote repositories.

<pre>
python3 github_copy.py <b>--dry-run</b> --source-prefix=g- --destination-prefix=grace-customer --destination-branch="master" --source-branch="master" --transformer=prefix --transformer-args="--file-prefix=magefile"
</pre>

The github_copy tool is also capable from running actions from the "/actions" folder in [grace-actions](https://github.com/GSA/grace-actions) (super cool private repository for team members) by specifying the template_transformer.py script and using grace-actions as the source repository.

```
python3 github_copy.py --source-prefix=grace-actions --destination-prefix=g- --destination-branch="development" --source-branch="master" --transformer=action --transformer-args="--action=ec2 --request-file=request.json"
```



## Public domain

This project is in the worldwide [public domain](LICENSE.md). As stated in [CONTRIBUTING](CONTRIBUTING.md):

> This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
>
> All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.
>
