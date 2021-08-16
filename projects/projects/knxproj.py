"""Module to read a knx project."""

import logging
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Tuple
from zipfile import ZipFile

from .groupaddresses import Factory as GAFactory
from .groupaddresses import GroupAddress
from .topology import Area, Device
from .topology import Factory as TOFactory
from .topology import Line
from .util import FinderXml


@dataclass
class KnxprojLoader:
    """Extract a .knxproj and read project information."""

    # Without defaults
    knxproj_path: Path

    # With defaults
    project_file: str = "0"

    # Non-initialized values
    findall: Callable = field(init=False)
    project_prefix: str = field(init=False)

    def run(self) -> Tuple[List[GroupAddress], List[Device]]:
        """Extract groupaddresses and devices from knxproj."""
        xml_meta_path, xml_project_path = self._unzip()
        self._setup_findall(xml_meta_path)
        self._meta(xml_meta_path)
        return self._extract_project(xml_project_path)

    def _unzip(self) -> Tuple[Path, Path]:
        """Unzip the knx project."""
        unzip_folder = Path(tempfile.gettempdir()).joinpath("knxproj_unzipped")
        project_file = ".".join((self.project_file, "xml"))
        with ZipFile(self.knxproj_path, "r") as zip_:
            files = zip_.namelist()
            for file_ in files:
                # Fast track -> skip non-xmls and elements not in the project dir
                if not file_.endswith(".xml") or not file_.startswith("P-"):
                    continue
                # We need the project.xml and the ones defined in 'project_file'
                if file_.endswith("project.xml"):
                    unzipped = zip_.extract(file_, unzip_folder)  # type: ignore
                    xml_meta_path = Path(unzipped).absolute()
                    logging.debug("Meta xml unzipped to %s.", xml_meta_path)
                elif file_.endswith(project_file):
                    unzipped = zip_.extract(file_, unzip_folder)  # type: ignore
                    xml_project_path = Path(unzipped).absolute()
                    logging.debug("Project xml unzipped to %s.", xml_project_path)
        logging.info("knxproj xmls extracted.")
        return (xml_meta_path, xml_project_path)

    def _setup_findall(self, xml_meta_path: Path) -> None:
        """Set a finder for the correct namespace."""
        root = ET.parse(str(xml_meta_path)).getroot()
        ets_version = (
            root.attrib["CreatedBy"].lower() + root.attrib["ToolVersion"].split(".")[1]
        )
        self.findall = FinderXml(ets_version).findall

    def _meta(self, xml_meta_path: Path) -> None:
        """Extract and log meta information from project.xml file.

        Side effect: Update self.project_prefix
        """
        root = ET.parse(str(xml_meta_path)).getroot()

        # Initialize meta with the root data
        meta = {**root.attrib}

        # Get Project
        project = self.findall(root, "Project", 1)
        meta.update(**project.attrib)

        # Get ProjectInformation
        projectinfo = self.findall(project, "ProjectInformation", 1)
        meta.update(**projectinfo.attrib)

        # Store project id and the prefix used for GAs etc.
        self.project_prefix = "-".join((meta["Id"], self.project_file))

        # Display meta information
        logging.info("Project meta information:")
        for key, value in meta.items():
            logging.info("\t%s: %s", key, value)

    def _extract_project(
        self, xml_project_path: Path
    ) -> Tuple[List[GroupAddress], List[Device]]:
        """Extract the project information from the xml."""

        def get_xml() -> Tuple[ET.Element, ET.Element]:
            """Get xml elements for topology and group addresses."""
            root = ET.parse(str(xml_project_path)).getroot()

            project_xml = self.findall(root, "Project")[0]
            installation_xml_list = self.findall(project_xml, "Installations")[0]
            installation_xml = self.findall(installation_xml_list, "Installation")[0]
            topology_xml = self.findall(installation_xml, "Topology")[0]

            # Special treatment for gas
            groupaddress_xml_list = self.findall(installation_xml, "GroupAddresses")
            if not groupaddress_xml_list:
                groupaddress_xml = ET.Element("")  # Default element
            elif len(groupaddress_xml_list) == 1:
                groupaddress_xml = groupaddress_xml_list[0]
            else:
                logging.warning(
                    "Unusual case! More than 1 ga xml object. Defaulting to the first."
                )
                groupaddress_xml = groupaddress_xml_list[0]

            return (topology_xml, groupaddress_xml)

        def groupaddresses(
            groups_xml: ET.Element,
        ) -> List[GroupAddress]:
            """Get group addresses from xml."""
            ga_factory = GAFactory(self.project_prefix)

            gruppenaddresse_all = []

            # We expect only one grouprange
            grs_xml = self.findall(groups_xml, "GroupRanges", 1)

            # Extract group ranges
            for hg_xml in self.findall(grs_xml, "GroupRange"):
                # Hauptgruppen

                for mg_xml in self.findall(hg_xml, "GroupRange"):
                    # Mittelgruppen

                    for ga_xml in self.findall(mg_xml, "GroupAddress"):
                        gruppenaddresse = ga_factory.groupaddress(ga_xml)
                        gruppenaddresse_all.append(gruppenaddresse)
                        logging.debug("GA\t\t\t%s", gruppenaddresse)

            gruppenaddresse_all.sort(key=lambda x: x.id_str)
            for addr in gruppenaddresse_all:
                logging.debug(addr)

            return gruppenaddresse_all

        def topology(
            topo_xml: ET.Element,
        ) -> Tuple[List[Area], List[Line], List[Device]]:
            """Get topology from xml."""
            topo_factory = TOFactory(prefix=self.project_prefix, finder=self.findall)

            area_list = []
            line_list = []
            device_list = []

            area_xml_list = self.findall(topo_xml, "Area")
            for area_xml in area_xml_list:
                area = topo_factory.area(area_xml)
                area_list.append(area)
                logging.debug(area)

                lines_xml_list = self.findall(area_xml, "Line")
                for line_xml in lines_xml_list:
                    line = topo_factory.line(line_xml, area)
                    line_list.append(line)
                    logging.debug(line)

                    device_xml_list = self.findall(line_xml, "DeviceInstance")
                    for device_xml in device_xml_list:
                        device = topo_factory.device(device_xml, line)
                        device_list.append(device)
                        logging.debug(device)

            # attrib links
            device_list = sorted(device_list, key=lambda x: x.address)
            return (area_list, line_list, device_list)

        topo_xml, ga_xml = get_xml()
        ga_list = groupaddresses(ga_xml)
        (_, _, devices) = topology(topo_xml)
        return (ga_list, devices)
