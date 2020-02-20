from packaging.specifiers import SpecifierSet
from packaging.markers import default_environment, Marker

VCS_SCHEME = ("git", "svn", "hg", "bzr")
MARKER_KEYS = list(default_environment().keys())


def requirement_from_pipfile(name, package, include_hashes=False):
    """Convert a Pipfile entry to PEP 508 dependency line."""
    return Requirement.parse(name, package).as_line(include_hashes)


def _merge_markers(markers):
    result = Marker(markers[0])
    for m in markers[1:]:
        marker = Marker(m)
        if "or" in marker._markers and "or" not in result._markers:
            result._markers.extend(["and", marker._markers])
        elif "or" not in marker._markers and "or" in result._markers:
            result._markers[:] = [result._markers, 'and'] + marker._markers
        else:
            result._markers.extend(['and'] + marker._markers)
    return str(result)


class Requirement:
    """A class representing a requirement specification"""
    def __init__(
        self, name=None, specifier=None, extras=None, markers=None, url=None,
        path=None, vcs=None, repo=None, subdirectory=None, ref=None, hashes=None,
        editable=False, **kwargs
    ):
        self.name = name
        self.specifier = specifier
        self.extras = extras
        self.markers = markers
        self.editable = editable

        self._url = url
        self.path = path
        self.vcs = vcs
        self.repo = repo
        self.subdirectory = subdirectory
        self.ref = ref
        self.hashes = hashes or []

    @property
    def url(self):
        if self._url is not None:
            return self._url
        if self.vcs:
            return "{vcs}+{repo}{ref}#egg={name}{sub}".format(
                vcs=self.vcs,
                repo=self.repo,
                ref="@{}".format(self.ref) if self.ref else "",
                name=self.name_with_extras,
                sub="&subdirectory={}".format(
                    self.subdirectory
                ) if self.subdirectory else ""
            )
        if self.path:
            # Use the path directly as req line
            return self.path

    @property
    def name_with_extras(self):
        extras = "[{}]".format(",".join(self.extras)) if self.extras else ""
        return self.name + extras

    @classmethod
    def parse(cls, name, package):
        if not getattr(package, "items", None):
            kwargs = {"version": package}
        else:
            kwargs = package.copy()
        kwargs["name"] = name
        if "extras" in kwargs:
            kwargs["extras"] = tuple(kwargs["extras"])
        if "version" in kwargs:
            version = kwargs.pop("version")
            if version == "*":
                version = ""
            kwargs["specifier"] = SpecifierSet(version)
        vcs = next((scheme for scheme in VCS_SCHEME if scheme in kwargs), None)
        if vcs:
            kwargs["vcs"] = vcs
            kwargs["repo"] = kwargs.pop(vcs)
        if "file" in kwargs:
            kwargs["url"] = kwargs.pop("file")
        markers = []
        if "markers" in kwargs:
            markers.append(kwargs.pop("markers"))
        for key in MARKER_KEYS:
            if key in kwargs:
                markers.append("{}{}".format(key, kwargs.pop(key)))
        if markers:
            kwargs["markers"] = _merge_markers(markers)

        return cls(**kwargs)

    def as_line(self, include_hashes=False):
        if self.path:
            main_line = self.path
            if self.extras:
                main_line += "[{}]".format(",".join(self.extras))
        elif self.vcs:
            main_line = self.url
        elif self.url:
            main_line = "{} @ {}".format(self.name_with_extras, self.url)
        else:
            main_line = "{}{}".format(self.name_with_extras, self.specifier)
        editable = "-e " if self.editable else ""
        marker = "; {}".format(self.markers) if self.markers else ""
        hashes = (
            "".join(" --hash={}".format(h) for h in self.hashes)
            if include_hashes else ""
        )
        return "{}{}{}{}".format(editable, main_line, marker, hashes)
