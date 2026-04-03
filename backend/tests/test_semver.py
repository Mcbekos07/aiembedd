from app.services.versioning.semver_service import SemverService


def test_semver_patch() -> None:
    assert SemverService.bump('1.2.3', 'patch') == '1.2.4'


def test_semver_minor() -> None:
    assert SemverService.bump('1.2.3', 'minor') == '1.3.0'


def test_semver_major() -> None:
    assert SemverService.bump('1.2.3', 'major') == '2.0.0'
