import os

import pytest

from pdm.models.requirements import Requirement
from pdm.models.requirements import RequirementError
from tests import FIXTURES


FILE_PREFIX = "{FILE_PREFIX}" if os.name == "nt" else "file://"

REQUIREMENTS = [
    ("requests", ("requests", "*"), None),
    ("requests<2.21.0,>=2.20.0", ("requests", "<2.21.0,>=2.20.0"), None),
    (
        'requests==2.19.0; os_name == "nt"',
        ("requests", {"version": "==2.19.0", "marker": 'os_name == "nt"'}),
        None,
    ),
    (
        'requests[security,tests]==2.8.*,>=2.8.1; python_version < "2.7"',
        (
            "requests",
            {
                "version": "==2.8.*,>=2.8.1",
                "marker": 'python_version < "2.7"',
                "extras": ["security", "tests"],
            },
        ),
        None,
    ),
    (
        "pip @ https://github.com/pypa/pip/archive/1.3.1.zip",
        ("pip", {"url": "https://github.com/pypa/pip/archive/1.3.1.zip"}),
        None,
    ),
    (
        "-e git+http://git.example.com/MyProject#egg=MyProject",
        ("MyProject", {"editable": True, "git": "http://git.example.com/MyProject"}),
        None,
    ),
    (
        "git+http://git.example.com/MyProject#egg=MyProject",
        ("MyProject", {"git": "http://git.example.com/MyProject"}),
        None,
    ),
    (
        "https://github.com/pypa/pip/archive/1.3.1.zip",
        (None, {"url": "https://github.com/pypa/pip/archive/1.3.1.zip"}),
        None,
    ),
    (
        (FIXTURES / "projects/demo").as_posix(),
        ("demo", {"path": (FIXTURES / "projects/demo").as_posix()}),
        f"demo @ {FILE_PREFIX}" + (FIXTURES / "projects/demo").as_posix(),
    ),
    (
        (FIXTURES / "artifacts/demo-0.0.1-py2.py3-none-any.whl").as_posix(),
        (
            "demo",
            {
                "url": FILE_PREFIX
                + (FIXTURES / "artifacts/demo-0.0.1-py2.py3-none-any.whl").as_posix()
            },
        ),
        f"demo @ {FILE_PREFIX}"
        + (FIXTURES / "artifacts/demo-0.0.1-py2.py3-none-any.whl").as_posix(),
    ),
]


@pytest.mark.parametrize("req, req_dict, result", REQUIREMENTS)
def test_convert_req_dict_to_req_line(req, req_dict, result):
    r = Requirement.from_line(req)
    assert r.as_req_dict() == req_dict
    assert r.as_ireq()
    r = Requirement.from_req_dict(*req_dict)
    result = result or req
    assert r.as_line() == result


@pytest.mark.parametrize(
    "line,expected",
    [
        (
            "-e https://github.com/pypa/pip/archive/1.3.1.zip",
            "Editable requirement is only supported",
        ),
        ("requests; os_name=>'nt'", "Parse error at \"'; os_nam"),
        ("./nonexist", r"The local path (.+)? does not exist"),
        ("./tests", r"The local path (.+)? is not installable"),
    ],
)
def test_illegal_requirement_line(line, expected):
    with pytest.raises(RequirementError, match=expected):
        Requirement.from_line(line)
