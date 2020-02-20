import subprocess
import pytest

from pipfile2req.requirements import requirement_from_pipfile


def compare_requirements(left, right):
    return len(set(left.splitlines()) - set(right.splitlines())) == 0


@pytest.mark.parametrize(
    "command,golden_file",
    [
        ("pipfile2req -p tests", "tests/requirements.txt"),
        ("cd tests && pipfile2req", "tests/requirements.txt"),
        ("pipfile2req -p tests -d", "tests/dev-requirements.txt"),
        ("pipfile2req -p tests Pipfile", "tests/requirements-pipfile.txt"),
        ("pipfile2req -d tests/Pipfile", "tests/dev-requirements-pipfile.txt"),
        ("pipfile2req -d tests/Pipfile.lock", "tests/dev-requirements.txt"),
        ("pipfile2req -p tests --sources", "tests/requirements-sources.txt"),
        ("pipfile2req -p tests Pipfile --sources", "tests/requirements-pipfile-sources.txt"),
    ],
)
def test_convert_pipfile(command, golden_file):
    proc = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, err = proc.communicate()
    with open(golden_file) as f:
        assert compare_requirements(
            output.decode("utf-8").strip().replace("\r\n", "\n"),
            f.read().strip().replace("\r\n", "\n"),
        )


def test_convert_include_hash():
    command = "pipfile2req -p tests --hashes"
    proc = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    _, err = proc.communicate()
    print(err)
    assert proc.returncode == 0


@pytest.mark.parametrize("name,package,req", [
    ("foo", "*", "foo"),
    ("foo", {"version": "*"}, "foo"),
    ("foo", {"version": ">=1.0", "extras": ["test", "sec"]}, "foo[test,sec]>=1.0"),
    ("foo", {"file": "file:///data/demo-0.0.1.tar.gz"}, "foo @ file:///data/demo-0.0.1.tar.gz"),
    ("foo", {"file": "file:///data/demo-0.0.1.tar.gz", "extras": ["test", "sec"]}, "foo[test,sec] @ file:///data/demo-0.0.1.tar.gz"),
    ("foo", {"path": ".", "editable": True, "extras": ["test", "sec"]}, "-e .[test,sec]"),
    ("foo", {"version": ">=1.0", "markers": "os_name=='nt'", "python_version": "~='3.7'"}, 'foo>=1.0; os_name == "nt" and python_version ~= "3.7"'),
    ("foo", {"git": "https://github.com/foo/foo.git", "ref": "master", "subdirectory": "sub"}, "git+https://github.com/foo/foo.git@master#egg=foo&subdirectory=sub")
])
def test_convert_requirement(name, package, req):
    result = requirement_from_pipfile(name, package)
    assert result == req
