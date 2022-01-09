"""Wrap pytest with an own rule."""

load("@rules_python//python:defs.bzl", "py_test")

# TODO: Make this independend of logger
load("@logger_deps//:dependencies.bzl", "dependency")

def py_pytest(name, srcs, deps = [], args = [], **kwargs):
    """Call pytest wiht additional args."""
    py_test(
        name = name,
        srcs = [
            "//tools/pytest:pytest_wrapper.py",
        ] + srcs,
        main = "//tools/pytest:pytest_wrapper.py",
        args = [
            "--capture=no",
        ] + args + ["$(location :%s)" % x for x in srcs],
        python_version = "PY3",
        srcs_version = "PY3",
        deps = deps + [
            dependency("pytest"),
        ],
        **kwargs
    )
