"""
    pipfile_requirements.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    :author: frostming <mianghong@gmail.com>
    :license: MIT
"""
import io
import os
import sys
import json
import argparse
import toml
import warnings

from .requirements import requirement_from_pipfile

if sys.version_info[:2] == (2, 7):

    class FileNotFoundError(OSError):
        pass


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--project", default=".", help="Specify another project root"
    )
    parser.add_argument(
        "--hashes",
        default=False,
        action="store_true",
        help="whether to include the hashes",
    )
    parser.add_argument(
        "-d",
        "--dev",
        default=False,
        action="store_true",
        help="whether to choose the dev-dependencies section",
    )
    parser.add_argument(
        "-s",
        "--sources",
        default=False,
        action="store_true",
        help="whether to include extra PyPi indexes",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="The file path to covert, support both Pipfile and Pipfile.lock. "
        "If it isn't given, will try Pipfile.lock first then Pipfile.",
    )
    return parser.parse_args()


def convert_pipfile_or_lock(
    project, pipfile=None, hashes=False, dev=False, sources=False
):
    """Convert given Pipfile/Pipfile.lock to requirements.txt content.

    :param project: the project path, default to `pwd`.
    :param pipfile: the path of Pipfile or Pipfile.lock. If it isn't given, will try
                    Pipfile.lock first then Pipfile.
    :param hashes: whether to include hashes
    :param dev: whether to choose the dev-dependencies section.
    :param sources: whether to include extra PyPi indexes
    :returns: the content of requirements.txt
    """
    if pipfile is None:
        if os.path.exists(os.path.join(project, "Pipfile.lock")):
            full_path = os.path.join(project, "Pipfile.lock")
        else:
            full_path = os.path.join(project, "Pipfile")
    else:
        full_path = os.path.abspath(pipfile)
    if not os.path.exists(full_path):
        raise FileNotFoundError("No Pipfile* is found.")
    try:
        with io.open(full_path, encoding="utf-8") as f:
            data = json.load(f)
        packages = data["develop"] if dev else data["default"]
        sources_data = data["_meta"].get("sources", [])
    except Exception:
        if hashes:
            warnings.warn(
                "Pipfile is given, the hashes flag won't take effect.", UserWarning
            )
        with io.open(full_path, encoding="utf-8") as f:
            data = toml.load(f)
        packages = data["dev-packages"] if dev else data["packages"]
        hashes = False
        sources_data = data.get("source", [])
    lines = [
        requirement_from_pipfile(name, package, hashes)
        for name, package in packages.items()
    ]

    if sources:
        for source in sources_data:
            if source.get('name') == 'pypi':
                lines.append("--index-url={}".format(source.get('url')))
            else:
                lines.append("--extra-index-url={}".format(source.get('url')))
    return lines


def main():
    args = parse_args()
    lines = convert_pipfile_or_lock(
        args.project, args.file, args.hashes, args.dev, args.sources
    )
    for line in lines:
        print(line)
