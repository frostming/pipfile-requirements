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
import tomlkit
import warnings

from vistir.compat import Path
from requirementslib import Lockfile, Requirement

if sys.version_info[:2] == (2, 7):

    class FileNotFoundError(OSError):
        pass


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--project", default=".", type=Path, help="Specify another project root"
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


def _convert_pipfile(pipfile, dev=False, sources=False):
    section = "dev-packages" if dev else "packages"
    with io.open(pipfile, encoding="utf-8") as f:
        pipfile = tomlkit.loads(f.read())

    reqs = [Requirement.from_pipfile(k, v) for k, v in pipfile[section].items()]

    data = [req.as_line() for req in reqs]

    if sources:
        for source in pipfile.get('source', []):
            if source.get('name') == 'pypi':
                data.append("--index-url={}".format(source.get('url')))
            else:
                data.append("--extra-index-url={}".format(source.get('url')))

    return data


def _convert_pipfile_lock(pipfile, hashes=False, dev=False, sources=False):
    lockfile = Lockfile.load(pipfile)

    data = lockfile.as_requirements(hashes, dev=dev)

    if sources:
        for source in lockfile.lockfile.meta.sources:
            if source.name == 'pypi':
                data.append("--index-url={}".format(source.url_expanded))
            else:
                data.append("--extra-index-url={}".format(source.url_expanded))

    return data


def convert_pipfile_or_lock(project, pipfile=None, hashes=False, dev=False, sources=False):
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
        if project.joinpath("Pipfile.lock").exists():
            pipfile = "Pipfile.lock"
        elif project.joinpath("Pipfile").exists():
            pipfile = "Pipfile"
    if pipfile and not Path(pipfile).is_absolute():
        full_path = project.joinpath(pipfile).as_posix()
    else:
        full_path = pipfile
    if pipfile is None or not os.path.exists(full_path):
        raise FileNotFoundError("No Pipfile* is found.")
    try:
        with io.open(full_path, encoding="utf-8") as f:
            json.load(f)
    except Exception:
        if hashes:
            warnings.warn(
                "Pipfile is given, the hashes flag won't take effect.", UserWarning
            )
        return _convert_pipfile(full_path, dev, sources)
    else:
        return _convert_pipfile_lock(full_path, hashes, dev, sources)


def main():
    args = parse_args()
    lines = convert_pipfile_or_lock(args.project, args.file, args.hashes, args.dev, args.sources)
    for line in lines:
        print(line)


if __name__ == "__main__":
    main()
