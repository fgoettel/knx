"""Module to read a GIRA .gpa project."""

import logging
import re
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

from .groupaddresses import GroupAddress
from .util import FinderXml


@dataclass
class GpaLoader:
    """Extra a .gpa project and read GA information."""

    finder = FinderXml("gpa")
    gpa_path: Path

    def run(self):
        """Extract all knx datapoints from a gpa project."""
        project_list, ga_list = self._unzip()
        assert len(project_list) == 1  # We only expect one project right now
        self._project(project_list[0])
        return self._gas(ga_list)

    def _unzip(self):
        re_project = re.compile(r"^(projects/)((\$[\w|-]*).xml)$")
        # re_ga = re.compile();
        print(self.gpa_path.resolve())
        unzip_folder = Path(tempfile.gettempdir()).joinpath("gpa_unzipped")
        ga_list = []
        project_list = []
        with ZipFile(self.gpa_path, "r") as zip_:
            files = zip_.namelist()
            for file_ in files:
                if not file_.endswith(".xml"):
                    continue
                if re_project.match(file_):
                    unzipped = zip_.extract(file_, unzip_folder)
                    project_list.append(Path(unzipped).absolute())
                elif "knxgroupaddressinformations" in file_:
                    # Copied info from ETS
                    continue
                elif "knxdatapoints" in file_:
                    unzipped = zip_.extract(file_, unzip_folder)
                    ga_list.append(Path(unzipped).absolute())
        return (project_list, ga_list)

    def _project(self, project_xml):
        root = ET.parse(str(project_xml)).getroot()
        author = self.finder(root, "Author", 1).text
        name = self.finder(root, "EntityName", 1).text
        changed = self.finder(root, "LastModified", 1).text
        logging.info(
            "Project '%s', created by '%s', last changed on '%s'.",
            name,
            author,
            changed,
        )

    def _gas(self, ga_list):
        gas = []
        for ga_xml in ga_list:
            root = ET.parse(str(ga_xml)).getroot()
            assert "KnxDataPoint" in root.tag
            id_ = self.finder(root, "EntityId", 1).text
            ga_rx = int(self.finder(root, "ReadGroupAddress", 1).text)
            ga_tx = int(self.finder(root, "WriteGroupAddress", 1).text)
            name = self.finder(root, "EntityName", 1).text
            dtype = self.finder(root, "DataTypeKnx", 1).text
            tmp = dtype.split(".")
            dtype_main = tmp[0]
            dtype_sub = tmp[1].lstrip("0")
            if dtype_sub == "":
                dtype_sub = "0"
            dtype_str = "-".join(("DPST", dtype_main, dtype_sub))
            if ga_rx != 0:
                gas.append(
                    GroupAddress(id_str=id_, name=name, address=ga_rx, dtype=dtype_str)
                )
            if ga_rx not in (0, ga_rx):
                gas.append(
                    GroupAddress(id_str=id_, name=name, address=ga_tx, dtype=dtype_str)
                )
        return gas
