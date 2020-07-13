import argparse


class ArgParser:
    def parse_github_copy_args(self):
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
        parser.add_argument(
            "--pull-request-name",
            dest="pullRequestName",
            type=str,
            help="Indicates how pull requests will be named",
            default="automated change",
        )
        parser.add_argument(
            "--action-type",
            dest="actionType",
            type=str,
            help="Indicates what type of grace action to take",
            default="",
        )
        return parser
