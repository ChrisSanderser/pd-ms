import argparse
import sys
import textwrap
from shutil import get_terminal_size

from pkg_resources import safe_name

from pdm.cli.commands.base import BaseCommand
from pdm.iostream import stream
from pdm.project import Project
from pdm.utils import highest_version


def print_results(hits, working_set, terminal_width=None):
    if not hits:
        return
    name_column_width = (
        max(
            [
                len(hit["name"]) + len(highest_version(hit.get("versions", ["-"])))
                for hit in hits
            ]
        )
        + 4
    )

    for hit in hits:
        name = hit["name"]
        summary = hit["summary"] or ""
        latest = highest_version(hit.get("versions", ["-"]))
        if terminal_width is not None:
            target_width = terminal_width - name_column_width - 5
            if target_width > 10:
                # wrap and indent summary to fit terminal
                summary = textwrap.wrap(summary, target_width)
                summary = ("\n" + " " * (name_column_width + 2)).join(summary)
        current_width = len(name) + len(latest) + 4
        spaces = " " * (name_column_width - current_width)
        line = "{name} ({latest}){spaces} - {summary}".format(
            name=stream.green(name, bold=True),
            latest=stream.yellow(latest),
            spaces=spaces,
            summary=summary,
        )
        try:
            stream.echo(line)
            if safe_name(name).lower() in working_set:
                dist = working_set[safe_name(name).lower()]
                if dist.version == latest:
                    stream.echo("  INSTALLED: %s (latest)" % dist.version)
                else:
                    stream.echo("  INSTALLED: %s" % dist.version)
                    stream.echo("  LATEST:    %s" % latest)
        except UnicodeEncodeError:
            pass


class Command(BaseCommand):
    """Search for PyPI packages"""

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("query")

    def handle(self, project: Project, options: argparse.Namespace) -> None:
        result = project.get_repository().search(options.query)
        terminal_width = None
        if sys.stdout.isatty():
            terminal_width = get_terminal_size()[0]
        print_results(result, project.environment.get_working_set(), terminal_width)
