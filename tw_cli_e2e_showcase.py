#!/usr/bin/env python3

"""
This script will automate the end-to-end creation all of the following entities in Nextflow Tower
from a YAML configuration file:
 - Organization
 - Teams
 - Workspaces
 - Participants
 - Credentials
 - Secrets
 - Compute Environments
 - Actions
 - Datasets
 - Pipelines
 - Launch
"""

import os
import sys
import argparse
import logging
import time
import yaml
from pathlib import Path
from git import Repo

## TODO: Add parameters for --git_repo, --git_branch
## TODO: Remove this cloning from within the script in the future
git_repo = 'https://github.com/ejseqera/tw-py'
git_branch = 'implement_e2e'
repo_dir = os.path.basename(git_repo)
if not os.path.exists(repo_dir):
    logging.info(msg=f"Cloning {git_repo} to {repo_dir}")
    Repo.clone_from(git_repo, repo_dir, branch=git_branch)
sys.path.append(repo_dir)

from tw_py import tower
import tower_e2e_helper as helper

logger = logging.getLogger(__name__)

# from urllib.parse import urlparse


def log_and_continue(e):
    logger.error(e)
    return


def parse_args():
    # TODO: description and usage
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, help="Config file with pipelines to run")
    parser.add_argument(
        "-l",
        "--log_level",
        default="INFO",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"),
        help="The desired log level (default: WARNING).",
    )
    # TODO: launch option? launch pipelines after adding
    # parser.add_argument("--launch", action="store_true", help="Launch the pipelines specified in config file")
    return parser.parse_args()


class BlockManager:
    """
    Manages blocks of commands defined in a configuration file.

    Attributes:
    tw: A Tower instance.
    list_for_add_method: A list of blocks that need to be handled by the 'add' method.
    """

    def __init__(self, tw, list_for_add_method):
        """
        Initializes a BlockManager instance.

        Args:
        tw: A Tower instance.
        list_for_add_method: A list of blocks that need to be handled by the 'add' method.
        """
        self.tw = tw
        self.list_for_add_method = list_for_add_method

    def handle_block(self, block, args):
        # Handles a block of commands by calling the appropriate function.
        block_handler_map = {
            "teams": helper.handle_teams,
            "participants": helper.handle_participants,
            "compute-envs": helper.handle_compute_envs,
            "pipelines": helper.handle_pipelines,
            "launch": helper.handle_launch,
        }
        if block in self.list_for_add_method:
            helper.handle_add_block(self.tw, block, args)
        elif block in block_handler_map:
            block_handler_map[block](self.tw, args)
        else:
            logger.error(f"Unrecognized block in YAML: {block}")


def main():
    options = parse_args()
    logging.basicConfig(level=options.log_level)

    if not options.config:
        logger.error("Config file is required")
        return

    tw = tower.Tower()
    block_manager = BlockManager(
        tw,
        [
            "organizations",
            "workspaces",
            "credentials",
            "secrets",
            "actions",
            "datasets",
        ],
    )
    with open(options.config, "r") as f:
        data = yaml.safe_load(f)

    # Returns a dictionary that maps block names to lists of command line
    # arguments. Each list of arguments is itself a list of arguments
    # for a single command.
    cmd_args_dict = helper.parse_all_yaml(options.config, list(data.keys()))

    # iterates over each item in cmd_args_dict. For each block,
    # calls block_manager.handle_block to handle the block of commands
    for block, args_list in cmd_args_dict.items():
        for args in args_list:
            # TODO: remove the debugger eventually
            logger.debug(f"For block '{block}', the arguments are: {args}")
            time.sleep(3)

            # Run the methods for each block
            block_manager.handle_block(block, args)


if __name__ == "__main__":
    main()
