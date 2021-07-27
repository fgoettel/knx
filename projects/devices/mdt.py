"""Container for MDT devices."""
# pylint: disable=too-many-locals

import logging
import re
from dataclasses import dataclass
from re import Pattern
from typing import List

from projects.topology import Device

from .devices import Switch


@dataclass
class BE4(Switch):
    """MDT Tasterschnittstelle."""

    def __init__(self, project_ga_list: List, *args, **kwargs):
        """Create a MDT binary interface."""
        super().__init__(*args, **kwargs)
        self.project_ga_list = project_ga_list

    @classmethod
    def from_device(cls, device: Device, *args, **kwargs):
        """Create a MDT Glastaster 2 from a generic device."""

        return cls(project_ga_list=kwargs["project_ga_list"], **vars(device))

    def find_ga(self, id_: str):
        """Find the complete GA to a given id."""
        for groupaddress in self.project_ga_list:
            if groupaddress.id_str == id_:
                return groupaddress
        raise ValueError("Unknown ga id_.")

    def doc(self):
        """Document connected GAs."""
        hline = self.border * self.width
        hline_small = self.hsep * self.width

        gas = []
        for connected_ga_id in self.groupaddress_list:
            gas.append("=> " + connected_ga_id + self.find_ga(connected_ga_id).name)

        conns = (hline_small + "\n").join(gas)

        switch = f"""
{self.name}
{hline}
{conns}
{hline}
"""
        print(switch)


class GT2(Switch):
    """MDT Glastaster 2."""

    line0_re = re.compile(
        r"^(?P<nr>T1|T2|T1/2)(\s?(?P<duration>kurz|lang))?:\s(?P<description>.*)$"
    )
    line1_re = re.compile(
        r"^(?P<nr>T3|T4|T3/4)(\s?(?P<duration>kurz|lang))?:\s(?P<description>.*)$"
    )
    line2_re = re.compile(
        r"^(?P<nr>T5|T6|T5/6)(\s?(?P<duration>kurz|lang))?:\s(?P<description>.*)$"
    )
    line3_re = re.compile(
        r"^(?P<nr>T7|T8|T7/8)(\s?(?P<duration>kurz|lang))?:\s(?P<description>.*)$"
    )
    line4_re = re.compile(
        r"^(?P<nr>T9|T10|T9/10)(\s?(?P<duration>kurz|lang))?:\s(?P<description>.*)$"
    )
    line5_re = re.compile(
        r"^(?P<nr>T11|T12|T11/12)(\s?(?P<duration>kurz|lang))?:\s(?P<description>.*)$"
    )

    status_re = re.compile(r"^(?P<description>(Statustext|Statuswert|Meldung)\s.+)$")
    led_re = re.compile(
        r"^(?P<description>Status LED)$"
    )  # Not inside ComObjectInstanceRefs, but GroupObjectTree

    def __init__(self, texts, *args, **kwargs):
        """Create a MDT GT2."""
        super().__init__(*args, **kwargs)
        self.texts = texts

    @classmethod
    def from_device(cls, device: Device, *args, **kwargs):
        """Create a MDT Glastaster 2 from a generic device."""

        return cls(texts=kwargs["texts"], **vars(device))

    def doc(self):
        """Show all pages from a GT2."""

        def _match_line(lines: set, expr: Pattern) -> str:
            sep = 5 * " "
            result = []
            for line in lines.copy():
                match = expr.match(line)

                if match is None:
                    continue

                lines.remove(line)

                description = match.group("description").strip()

                result.append(description)
            return sep.join(result)

        # Match the lines of the text
        lines = set(self.texts)

        # TODO: Switch w.r.t. layout (2 or 3 per page)
        line0 = [_match_line(lines, self.line0_re), _match_line(lines, self.line3_re)]
        line1 = [_match_line(lines, self.line1_re), _match_line(lines, self.line4_re)]
        line2 = [_match_line(lines, self.line2_re), _match_line(lines, self.line5_re)]

        line_status = _match_line(lines, self.status_re)
        if line_status:
            logging.info("%s has statustext/warnings activated.", self.name)
        line_led = _match_line(lines, self.led_re)
        # TODO: check if the leds are covered
        if line_led:
            logging.info("%s has led feedback activated.", self.name)

        # Assert there are no leftovers
        if lines:
            raise Exception(lines)

        # Formatting
        button_space = "    "
        button_l = self.vsep + button_space + self.vsep + " "
        button_r = " " + self.vsep + button_space + self.vsep
        hline = (self.width + len(button_l) + len(button_r)) * self.border
        hline_small = len(hline) * self.hsep

        # Count pages
        def page_count_fcn(line_x):
            return len([x for x in line_x if x])

        page_count = max(map(page_count_fcn, (line0, line1, line2)))

        # Create pages
        for idx in range(page_count):
            name = f"{self.name} {idx+1}/{page_count}"
            switch = f"""
{name}
{hline}
{button_l}{line0[idx].center(self.width)}{button_r}
{hline_small}
{button_l}{line1[idx].center(self.width)}{button_r}
{hline_small}
{button_l}{line2[idx].center(self.width)}{button_r}
{hline}
"""
            print(switch)
