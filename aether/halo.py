"""HALO - Terminal dashboard (no curses dependency)."""
from __future__ import annotations
import os, shutil, time
from dataclasses import dataclass


@dataclass
class Panel:
    title: str
    lines: list


class Halo:
    def __init__(self, title="AETHER"):
        self.title = title

    def _width(self):
        return min(shutil.get_terminal_size((80, 24)).columns, 100)

    @staticmethod
    def clear():
        os.system("clear" if os.name != "nt" else "cls")

    def _box(self, panel, width):
        top = "+" + "-" * (width - 2) + "+"
        title = f" {panel.title} "
        pad = width - 2 - len(title)
        head = "+" + title + "-" * max(pad, 0) + "+"
        body = []
        for line in panel.lines:
            body.append("| " + line[:width - 4].ljust(width - 4) + " |")
        return [head] + body + [top]

    def render(self, panels):
        self.clear()
        w = self._width()
        print(f"\n  {self.title}  |  {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        for p in panels:
            for line in self._box(p, w):
                print(line)
            print()

    def live(self, panels_fn, interval=2, duration=None):
        start = time.time()
        try:
            while True:
                self.render(panels_fn())
                if duration and (time.time() - start) >= duration:
                    break
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopped.")

    def bar(self, value, max_value, width=30):
        if max_value <= 0: return "[" + " " * width + "]"
        filled = int(width * min(value, max_value) / max_value)
        return "[" + "#" * filled + "-" * (width - filled) + "]"
