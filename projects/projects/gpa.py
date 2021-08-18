"""Module to read a GIRA .gpa project."""

import logging
import re
import tempfile
import xml.etree.ElementTree as ET
from collections import namedtuple
from pathlib import Path
from typing import List
from zipfile import ZipFile

from .groupaddresses import GroupAddress
from .util import FinderXml

ProjectFiles = namedtuple(
    "ProjectFiles",
    (
        "project",
        "knxdatapoints",
        "internaldatapoints",
        "devicedatapoints",
        "logicnodes",
    ),
)
InternalDataPoint = namedtuple("InternalDataPoint", ("name", "knx", "id", "type"))


class Gpa:
    """Extra a .gpa project and read GA information."""

    def __init__(self, gpa_path: Path) -> None:
        """Set up a basic Gpa instance."""
        self.findall = FinderXml("gpa").findall
        self.files = self._unzip(gpa_path=gpa_path)

    def display_infos(self) -> None:
        """Display otherwise unused information.

        Parameters
        ----------
        gpa_path
            Path to the ".gpa" file.

        Returns
        -------
        ga_list
            A list with `GroupAdress` items.

        """
        self._display_project_info()
        self._display_device_datapoints()
        self._display_internal_datapoints()
        # TODO: Utilize files.logicnodes - or switch to logic pages

    @staticmethod
    def _unzip(gpa_path: Path) -> ProjectFiles:
        """Unzip a .gpa project into list of projects paths and group address path.

        Parameters
        ----------
        gpa_path
            Path to the ".gpa" file.

        Returns
        -------
        ProjectFiles
            A named tuple with list of related files.

        """
        logging.info("Extracting: %s", gpa_path.resolve())

        re_project = re.compile(r"^(projects/)((\$[\w|-]*).xml)$")

        unzip_folder = Path(tempfile.gettempdir()).joinpath("gpa_unzipped")

        knxdatapoints = []
        project_list = []
        internaldatapoints = []
        devicedatapoints = []
        logicnodes = []
        with ZipFile(gpa_path, "r") as zip_:
            # Check all files if they belong to a specifc dir of interest
            # The file/folder names can be validated in the project.xml
            #    Entitycollection -> projectparts ->
            for file_ in zip_.namelist():
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
                    knxdatapoints.append(Path(unzipped).absolute())
                elif "internaldatapoints" in file_:
                    unzipped = zip_.extract(file_, unzip_folder)
                    internaldatapoints.append(Path(unzipped).absolute())
                    # TODO: use this
                elif "devicedatapoints" in file_:
                    unzipped = zip_.extract(file_, unzip_folder)
                    devicedatapoints.append(Path(unzipped).absolute())
                    # TODO: use this
                elif "logicnodes" in file_:
                    unzipped = zip_.extract(file_, unzip_folder)
                    logicnodes.append(Path(unzipped).absolute())
                    # TODO: use this
                else:
                    logging.debug("Skipping %s", file_)

        assert len(project_list) == 1  # We only expect one project right now

        return ProjectFiles(
            project=project_list[0],
            knxdatapoints=knxdatapoints,
            internaldatapoints=internaldatapoints,
            devicedatapoints=devicedatapoints,
            logicnodes=logicnodes,
        )

    def _display_project_info(self) -> None:
        """Display meta information about the given project.

        Parameters
        ----------
        project_xml
            Path to a project xml

        """
        root = ET.parse(str(self.files.project)).getroot()
        author = self.findall(root, "Author")[0].text
        name = self.findall(root, "EntityName")[0].text
        changed = self.findall(root, "LastModified")[0].text
        logging.info(
            "Project '%s', created by '%s', last changed on '%s'.",
            name,
            author,
            changed,
        )

    def _display_device_datapoints(self) -> None:
        """Ensure that the internal/device datapoints are not used."""
        ddp_counter = 0
        for dp_xml in self.files.devicedatapoints:
            root = ET.parse(str(dp_xml)).getroot()
            assert "DeviceDataPoint" in root.tag
            enabled = self.findall(root, "Enabled")[0].text == "true"
            used = self.findall(root, "KnxIntegration")[0].text == "true"
            if enabled and used:
                ddp_counter += 1

        logging.info("%i device datapoints are existent.", ddp_counter)

    def _display_internal_datapoints(self) -> None:
        """Display all internal datapoints."""

        internal_dp = []
        for dp_xml in self.files.internaldatapoints:
            root = ET.parse(str(dp_xml)).getroot()
            assert "InternalDataPoint" in root.tag
            try:
                if self.findall(root, "Enabled")[0].text == "false":
                    continue
            except IndexError:
                pass

            internal_dp.append(
                InternalDataPoint(
                    name=self.findall(root, "EntityName")[0].text,
                    knx=self.findall(root, "KnxIntegration")[0].text,
                    id=self.findall(root, "EntityId")[0].text,
                    type=getattr(self.findall(root, "ValueTypeUrn")[0], "text").split(
                        "."
                    )[-1],
                )
            )

        if internal_dp:
            logging.info("%i internal datapoints are existent.", len(internal_dp))
            for datapoint in internal_dp:
                logging.info("\t%s", datapoint)

    @property
    def groupaddresses(self) -> List[GroupAddress]:
        """From a list of paths to group addresses extract the GA information."""
        ga_list = []
        for ga_xml in self.files.knxdatapoints:
            root = ET.parse(str(ga_xml)).getroot()
            assert "KnxDataPoint" in root.tag
            id_ = getattr(self.findall(root, "EntityId")[0], "text")
            ga_rx = int(getattr(self.findall(root, "ReadGroupAddress")[0], "text"))
            ga_tx = int(getattr(self.findall(root, "WriteGroupAddress")[0], "text"))
            name = getattr(self.findall(root, "EntityName")[0], "text")

            dtype = getattr(self.findall(root, "DataTypeKnx")[0], "text")
            tmp = dtype.split(".")
            dtype_main = tmp[0]
            dtype_sub = tmp[1].lstrip("0")

            if dtype_sub == "":
                dtype_sub = "0"
            dtype_str = "-".join(("DPST", dtype_main, dtype_sub))
            if ga_rx != 0:
                ga_list.append(
                    GroupAddress(id_str=id_, name=name, address=ga_rx, dtype=dtype_str)
                )
            if ga_rx not in (0, ga_rx):
                ga_list.append(
                    GroupAddress(id_str=id_, name=name, address=ga_tx, dtype=dtype_str)
                )
        return ga_list
