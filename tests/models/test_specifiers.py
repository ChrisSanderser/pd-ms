import pytest

from pdm.models.specifiers import PySpecSet


@pytest.mark.parametrize(
    "original,normalized",
    [
        (">=3.6", ">=3.6"),
        ("<3.8", "<3.8"),
        ("~=2.7.0", ">=2.7,<2.8"),
        ("", ""),
        (">=3.6,<3.8", ">=3.6,<3.8"),
        (">3.6", ">=3.6.1"),
        ("<=3.7", "<3.7.1"),
        ("<3.3,!=3.4.*,!=3.5.*", "<3.3"),
        (">=3.6,!=3.4.*", ">=3.6"),
        (">=3.6,!=3.6.*", ">=3.7"),
        (">=3.6,<3.8,!=3.8.*", ">=3.6,<3.8"),
        (">=2.7,<3.2,!=3.0.*,!=3.1.*", ">=2.7,<3.0"),
        ("!=3.0.*,!=3.0.2", "!=3.0.*"),
        (">=3.4.*", ">=3.4"),
        (">3.4.*", ">=3.5"),
        ("<=3.4.*", "<3.4"),
        ("<3.4.*", "<3.4"),
    ],
)
def test_normalize_pyspec(original: str, normalized: str) -> None:
    spec = PySpecSet(original)
    assert str(spec) == normalized


@pytest.mark.parametrize(
    "left,right,result",
    [
        (">=3.6", ">=3.0", ">=3.6"),
        (">=3.6", "<3.8", ">=3.6,<3.8"),
        ("", ">=3.6", ">=3.6"),
        (">=3.6", "<3.2", "impossible"),
        (">=2.7,!=3.0.*", "!=3.1.*", ">=2.7,!=3.0.*,!=3.1.*"),
    ],
)
def test_pyspec_and_op(left: str, right: str, result: str) -> None:
    left = PySpecSet(left)
    right = PySpecSet(right)
    assert str(left & right) == result


@pytest.mark.parametrize(
    "left,right,result",
    [
        (">=3.6", ">=3.0", ">=3.0"),
        ("", ">=3.6", ""),
        (">=3.6", "<3.7", ""),
        (">=3.6,<3.8", ">=3.4,<3.7", ">=3.4,<3.8"),
        ("~=2.7", ">=3.6", ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*"),
        ("<2.7.15", ">=3.0", "!=2.7.15,!=2.7.16,!=2.7.17,!=2.7.18"),
    ],
)
def test_pyspec_or_op(left: str, right: str, result: str) -> None:
    left = PySpecSet(left)
    right = PySpecSet(right)
    assert str(left | right) == result


def test_impossible_pyspec() -> None:
    spec = PySpecSet(">=3.6,<3.4")
    a = PySpecSet(">=2.7")
    assert spec.is_impossible
    assert (spec & a).is_impossible
    assert spec | a == a
    spec_copy = spec.copy()
    assert spec_copy.is_impossible
    assert str(spec_copy) == "impossible"


@pytest.mark.parametrize(
    "left,right",
    [
        ("~=2.7", ">=2.7"),
        (">=3.6", ""),
        (">=3.7", ">=3.6,<4.0"),
        (">=2.7,<3.0", ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*"),
        (">=3.6", ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*"),
        (
            ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*",
            ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*",
        ),
    ],
)
def test_pyspec_is_subset_superset(left: str, right: str) -> None:
    left = PySpecSet(left)
    right = PySpecSet(right)
    assert left.is_subset(right), f"{left}, {right}"
    assert right.is_superset(left), f"{left}, {right}"


@pytest.mark.parametrize(
    "left,right",
    [
        ("~=2.7", ">=2.6,<2.7.15"),
        (">=3.7", ">=3.6,<3.9"),
        (">=3.7,<3.6", "==2.7"),
        (">=3.0,!=3.4.*", ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*"),
    ],
)
def test_pyspec_isnot_subset_superset(left: str, right: str) -> None:
    left = PySpecSet(left)
    right = PySpecSet(right)
    assert not left.is_subset(right), f"{left}, {right}"
    assert not left.is_superset(right), f"{left}, {right}"
