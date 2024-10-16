# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : practice
# @FileName : commit.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-10-15 17:54
# @UpdateTime : TODO

import datetime
import os
import random
import time

import click
import git
import pytz
import requests
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get_repo_list_from_restful_api():
    """
    Get the repository list from the GitHub RESTful API.

    Returns:
        list: A list of repositories. Each repository is a list of [repo_name, is_fork, is_private].
    """
    url = f"https://api.github.com/user/repos"
    params = {"visibility": "all", "sort": "updated", "per_page": 50}

    next_page = {"url": url}
    repo_list = []
    while next_page:
        response = requests.get(next_page["url"], headers=HEADERS, params=params)
        if response.status_code != 200:
            print("Error: ", response.status_code)
            break
        next_page = response.links.get("next", None)
        for repo in response.json():
            repo_name = repo["name"]
            is_fork = repo["fork"]
            is_private = repo["private"]
            repo_list.append([repo_name, is_fork, is_private])
    return repo_list


def get_repo_commits_from_restful_api(repo_name):
    """
    Get the commit list of the repository from the GitHub RESTful API.

    Args:
        repo_name (str): The name of the repository.

    Returns:
        list: A list of commits. Each commit is a list of [commit_sha, commit_date, year_month_day, commit_msg].
    """
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/commits"
    params = {"per_page": 100, "committer": USERNAME}

    next_page = {"url": url}
    commit_list = []
    while next_page:
        # sleep_time = random.uniform(0.1, 0.5)
        # time.sleep(sleep_time)
        response = requests.get(next_page["url"], headers=HEADERS, params=params)
        if response.status_code != 200:
            print("Error: ", response.status_code, repo_name)
            break
        next_page = response.links.get("next", None)
        for commit in response.json():
            commit_sha = commit["sha"]
            commit_msg = commit["commit"]["message"]
            commit_datestr = commit["commit"]["author"]["date"]
            commit_date = datetime.datetime.strptime(
                commit_datestr, "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=pytz.utc)
            commit_date = commit_date.astimezone(tz=pytz.timezone("Asia/Shanghai"))
            year_month_day = commit_date.strftime("%Y-%m-%d")
            commit_list.append([commit_sha, commit_date, year_month_day, commit_msg])
    return commit_list


def save_commit_date():
    """
    Save the commit date to the output directory.
    """
    public_commit_date_list = []
    private_commit_date_list = []
    all_commit_date_list = []

    repo_list = get_repo_list_from_restful_api()
    for repo in repo_list:
        repo_name = repo[0]
        is_fork = repo[1]
        is_private = repo[2]
        if is_fork:
            continue
        commit_list = get_repo_commits_from_restful_api(repo_name)
        commit_date_list = [commit[2] for commit in commit_list]
        commit_msg_list = [commit[3] for commit in commit_list]

        commit_info_list = []
        for commit_date, commit_msg in zip(commit_date_list, commit_msg_list):
            commit_info_list.append(f"{commit_date}\t{repo_name}\t{commit_msg}")
        if not is_private:
            public_commit_date_list.extend(commit_info_list)
        else:
            private_commit_date_list.extend(commit_info_list)
        all_commit_date_list.extend(commit_info_list)

    public_commit_date_list = sorted(list(set(public_commit_date_list)))
    private_commit_date_list = sorted(list(set(private_commit_date_list)))
    all_commit_date_list = sorted(list(set(all_commit_date_list)))

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "public_commit_date.txt"), "w") as f:
        f.write("\n".join(public_commit_date_list))
    with open(os.path.join(OUTPUT_DIR, "private_commit_date.txt"), "w") as f:
        f.write("\n".join(private_commit_date_list))
    with open(os.path.join(OUTPUT_DIR, "all_commit_date.txt"), "w") as f:
        f.write("\n".join(all_commit_date_list))


def get_commit_date_list(repo_type="all"):
    """
    Get the commit date list from the output directory.

    Args:
        repo_type (str): The type of the repository. Must be one of "public", "private", or "all".

    Returns:
        list: A list of commit dates in the format of "YYYY-MM-DD".
    """
    file_path = os.path.join(OUTPUT_DIR, f"{repo_type}_commit_date.txt")
    with open(file_path, "r") as f:
        commit_date_list = f.read().splitlines()
    commit_date_list = [line.split("\t")[0] for line in commit_date_list]
    return commit_date_list


def get_git_latest_commit(repo_path):
    """
    Get the latest commit date of the git repository.

    Args:
        repo_path (str): The path of the git repository. Must be a valid git repository.

    Returns:
        str: The latest commit date in the format of "YYYY-MM-DD".
    """

    repo = git.Repo(repo_path, search_parent_directories=True)
    latest_commit = repo.head.commit
    latest_commit_date = latest_commit.authored_datetime
    return latest_commit_date.strftime("%Y-%m-%d")


def find_next_non_overlapping_dates(current_date, date_list, limit=7):
    """
    Find the next non-overlapping dates starting from the current date.

    Args:
        current_date (str): The current date in the format of "YYYY-MM-DD".
        date_list (list): A list of dates in the format of "YYYY-MM-DD".
        limit (int): The number of dates to find.

    Returns:
        list: A list of the next non-overlapping dates.
    """
    date_format = "%Y-%m-%d"
    current_date = datetime.datetime.strptime(current_date, date_format)
    date_list = [datetime.datetime.strptime(date, date_format) for date in date_list]
    date_list = sorted(date_list)

    next_dates = []
    while len(next_dates) < limit:
        current_date += datetime.timedelta(days=1)
        if current_date not in date_list:
            next_dates.append(current_date.strftime(date_format))
    return next_dates


@click.command()
@click.option(
    "--refresh-commit-date",
    default=False,
    is_flag=True,
    help="Refresh the commit date and save them to the output directory.",
)
@click.option(
    "--get-next-dates",
    default=False,
    is_flag=True,
    help="Get the next non-overlapping dates.",
)
@click.option(
    "--repo-type",
    default="all",
    help="The type of the repository. Must be one of 'public', 'private', or 'all'.",
)
def main(refresh_commit_date, get_next_dates, repo_type):
    if refresh_commit_date:
        save_commit_date()
    if get_next_dates:
        current_date = get_git_latest_commit(repo_path=os.getcwd())
        date_list = get_commit_date_list(repo_type=repo_type)
        next_dates = find_next_non_overlapping_dates(current_date, date_list)
        print(next_dates)


if __name__ == "__main__":
    main()
