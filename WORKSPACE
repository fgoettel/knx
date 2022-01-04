load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "rules_python",
    sha256 = "cd6730ed53a002c56ce4e2f396ba3b3be262fd7cb68339f0377a45e8227fe332",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.5.0/rules_python-0.5.0.tar.gz",
)

# Poetry rules for managing Python dependencies

http_archive(
    name = "com_sonia_rules_poetry",
    sha256 = "88a849dcece2fb81c803d6d73ee5f6788edfc78f4e9a805d7d9f22fb1e5015ea",
    strip_prefix = "rules_poetry-a662e29a344b7762ab68e3ae44fc3aef333fe5ff",
    urls = ["https://github.com/soniaai/rules_poetry/archive/a662e29a344b7762ab68e3ae44fc3aef333fe5ff.tar.gz"],
)

load("@com_sonia_rules_poetry//rules_poetry:defs.bzl", "poetry_deps")

poetry_deps()

load("@com_sonia_rules_poetry//rules_poetry:poetry.bzl", "poetry")

poetry(
    name = "logger_deps",
    lockfile = "//logger:poetry.lock",
    pyproject = "//logger:pyproject.toml",
    # optional, if you would like to pull from pip instead of a Bazel cache
    #tags = ["no-remote-cache"],
)
