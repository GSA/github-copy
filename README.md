# GitHub Copy

## Repository contents

The `github_copy.py` tool allows copying of files from one GitHub repository to another. It also allows calling another script to perform transformations on the files before creating a pull request to send the changes to their new location.

## Installation

Currently supports Linux and Windows Subsystem for Linux (WSL).

1. Install Python 3
2. Install your [GitHub ssh key](https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) under `~/.ssh/id_rsa`
3. Set your [GitHub token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line) with `export GITHUB_TOKEN=[YOUR_GITHUB_TOKEN]`
4. Run `make install`
5. Add `~/.local/bin` to your PATH environment variable: `export PATH=~/.local/bin:$PATH`

## Installation without Internet

#### On another machine with internet:
Build a bundled version to `bundle/github-copy.tar.gz` using: `make bundle`

#### On target machine:
Extract the tar file and install.
```
tar zxvf github-copy.tar.gz
cd github-copy/dependencies
pip install * -f ./ --no-index
cd ..
make install
export PATH=~/.local/bin:$PATH
``` 

## Examples

Example of copying the magefile from "g-\*" to "grace-customer\*":

```
python3 -m github-copy --source-prefix=g- --destination-prefix=grace-customer --destination-branch="master" --source-branch="master" --transformer=prefix --transformer-args="--file-prefix=magefile"
```

Dry-run mode allows viewing what changes would occur without actually changing the remote repositories.

<pre>
python3 -m github-copy <b>--dry-run</b> --source-prefix=g- --destination-prefix=grace-customer --destination-branch="master" --source-branch="master" --transformer=prefix --transformer-args="--file-prefix=magefile"
</pre>

The github_copy tool is also capable of running actions from the "/actions" folder in [grace-actions](https://github.com/GSA/grace-actions) (super cool private repository for team members) by specifying the "action" transformer and using grace-actions as the source repository.

```
python3 -m github-copy --dry-run --source-prefix=grace-actions --destination-prefix=g-grace --destination-branch="development" --source-branch="master" --transformer-args="--request-file ~/request.json" --action-type=ec2
```



## Public domain

This project is in the worldwide [public domain](LICENSE.md). As stated in [CONTRIBUTING](CONTRIBUTING.md):

> This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
>
> All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.
>
