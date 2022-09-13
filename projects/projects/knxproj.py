"""Module to read a knx project."""

import logging
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple, Type
from zipfile import ZipFile

from .groupaddresses import Factory as GAFactory
from .groupaddresses import GroupAddress
from .topology import Device
from .topology import Factory as TOFactory
from .util import FinderXml


class Knxproj:
    """Extract a .knxproj and read project information."""

    project_file_name = "0.xml"  # TODO: Check if this is always true
    meta_file_name = "project.xml"

    def __init__(self, knxproj_path: Path) -> None:
        """Set up a basic knxproj instance.

        During creation the meta information is already extracted.

        Args:
            knxproj_path: Path to the ".knxproj" file.

        Raises:
            RuntimeError: If the poject id is inconsistent.
        """
        self.xml_meta_path, self.xml_project_path = self._unzip(
            knxproj_path=knxproj_path,
        )
        self.ets_version = self._extract_ets_version()
        self.findall = FinderXml(self.ets_version).findall

        project_id = self._extract_project_id()
        if project_id not in str(self.xml_project_path) or project_id not in str(
            self.xml_meta_path
        ):
            raise RuntimeError("Inconsistent project id found.")
        self.project_prefix = (
            project_id + "-" + self.project_file_name.split(".", maxsplit=1)[0]
        )

    @classmethod
    def _unzip(cls: Type["Knxproj"], knxproj_path: Path) -> Tuple[Path, Path]:
        """Unzip the knx project.

        Unzip the knxproj and extract the path to the meta information and project information.

        Args:
            knxproj_path: Path to the ".knxproj",

        Returns:
            meta_path: Path to the "meta" xml file.
            project_path: Path to the "project" xml file.
        """
        unzip_folder = Path(tempfile.gettempdir()).joinpath("knxproj_unzipped")
        with ZipFile(knxproj_path, "r") as zip_:
            xml_files = list(
                filter(lambda x: x.endswith(".xml"), zip_.namelist())
            )  # Only introduced for debugging

            # TODO: check "0.xml"
            project_path = Path(
                zip_.extract(
                    list(
                        filter(lambda x: x.endswith(cls.project_file_name), xml_files)
                    )[0],
                    unzip_folder,
                )
            )
            meta_path = Path(
                zip_.extract(
                    list(filter(lambda x: x.endswith(cls.meta_file_name), xml_files))[
                        0
                    ],
                    unzip_folder,
                )
            )

        logging.info("knxproj xmls extracted:\n\t%s\n\t%s", meta_path, project_path)
        return (meta_path, project_path)

    def _extract_ets_version(self) -> str:
        """Read ets version from the meta xml.

        Returns:
            ets_version
                A String containing info about the ets version. E.g. "ets57".
                This is important to deal with the xml namespaces.
        """
        root = ET.parse(str(self.xml_meta_path)).getroot()
        ets_version = (
            root.attrib["CreatedBy"].lower() + root.attrib["ToolVersion"].split(".")[1]
        )
        return ets_version

    def _extract_project_id(self) -> str:
        """Get the project id.

        Returns:
            The project id.
        """
        root = ET.parse(str(self.xml_meta_path)).getroot()
        return self.findall(root, "Project")[0].attrib["Id"]

    def _find_item_in_project(self, keyword: str) -> ET.Element:
        """Find an item in the xml project.

        Finds _exactly_ one item in the flattened project.

        Args:
            keyword: The keyword of interest

        Returns:
            element: The matching element

        Raises:
            RuntimeError: In case != 1 item is found.
        """
        root = ET.parse(str(self.xml_project_path)).getroot()

        findings = []
        for elem in root.iter():
            if match := self.findall(elem, keyword):
                findings.extend(match)
        if len(findings) != 1:
            raise RuntimeError("Not exactly one finding...")
        return findings[0]

    def display_meta_information(self) -> None:
        """Extract and log meta information from project.xml file."""
        root = ET.parse(str(self.xml_meta_path)).getroot()

        # Initialize meta with the root data
        meta = {**root.attrib}

        # Get Project
        project = self.findall(root, "Project")[0]
        meta.update(**project.attrib)

        # Get ProjectInformation
        projectinfo = self.findall(project, "ProjectInformation")[0]
        meta.update(**projectinfo.attrib)

        # Display meta information
        logging.info("Project meta information:")
        for key, value in meta.items():
            logging.info("\t%s: %s", key, value)

    @property
    def groupaddresses(
        self,
    ) -> List[GroupAddress]:
        """Get group addresses from project.

        Returns:
            A list of group addresses.
        """
        ga_factory = GAFactory(self.project_prefix)
        gruppenaddress_list = []

        # We expect only one grouprange
        groups_xml = self._find_item_in_project("GroupAddresses")
        grs_xml = self.findall(groups_xml, "GroupRanges")[0]

        # Extract group ranges
        for hg_xml in self.findall(grs_xml, "GroupRange"):
            # Hauptgruppen

            for mg_xml in self.findall(hg_xml, "GroupRange"):
                # Mittelgruppen

                for ga_xml in self.findall(mg_xml, "GroupAddress"):
                    gruppenaddresse = ga_factory.groupaddress(ga_xml)
                    gruppenaddress_list.append(gruppenaddresse)
                    logging.debug("GA\t\t\t%s", gruppenaddresse)

        gruppenaddress_list.sort(key=lambda x: x.id_str)
        for addr in gruppenaddress_list:
            logging.debug(addr)

        return gruppenaddress_list

    @property
    def topology(
        self,
    ) -> dict:
        """Get topology from xml.

        Returns:
            A dict representing the topology.
        """
        topo_xml = self._find_item_in_project("Topology")
        topo_factory = TOFactory(prefix=self.project_prefix, finder=self.findall)
        topo_items = defaultdict(list)

        for area_xml in self.findall(topo_xml, "Area"):
            area = topo_factory.area(area_xml)
            topo_items["area"].append(area)

            for line_xml in self.findall(area_xml, "Line"):
                line = topo_factory.line(line_xml, area)
                topo_items["line"].append(line)  # type: ignore

                for device_xml in self.findall(line_xml, "DeviceInstance"):
                    topo_items["device"].append(topo_factory.device(device_xml, line))  # type: ignore

        # attrib links
        topo_items["device"] = sorted(topo_items["device"], key=lambda x: x.address)
        return topo_items

    @property
    def devices(self) -> List[Device]:
        """Get all devices.

        Returns:
            List of Devices.
        """
        return self.topology["device"]
