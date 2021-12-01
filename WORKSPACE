load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "rules_python",
    sha256 = "cd6730ed53a002c56ce4e2f396ba3b3be262fd7cb68339f0377a45e8227fe332",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.5.0/rules_python-0.5.0.tar.gz",
)

load("@rules_python//python:pip.bzl", "pip_install")

# Create a central external repo, @logger_deps, that contains Bazel targets for all the
# third-party packages specified in the requirements.txt file.
# TODO: Move to lazy installation:
#  https://github.com/bazelbuild/rules_python#fetch-pip-dependencies-lazily
pip_install(
    name = "logger_deps",
    python_interpreter = "python3.10",
    requirements = "//logger:requirements.txt",
)
