# -*- coding: utf-8 -*-

"""Module wrapping the visdom dashboard initialization."""

import inspect
import os
import subprocess
import time
from typing import Optional

from visdom import Visdom

CUR_PATH = inspect.getfile(inspect.currentframe())
CUR_DIR = os.path.dirname(CUR_PATH)


class Dashboard(object):
    """Visdom dashboard base class."""

    def __init__(self,
                 visdom_addr: str = "localhost",
                 visdom_port: int = 8097,
                 env_name: Optional[str] = None):
        """Initialize the dashboard."""
        self._proc = None  # type: Optional[subprocess.Popen]
        self.viz = None  # type: Optional[Visdom]
        self.visdom_addr = visdom_addr
        self.visdom_port = visdom_port
        self.env_name = env_name if env_name is not None else "default_env"

    def _is_running(self):
        return self.viz is not None

    def start(self):
        """Start the dashboard."""
        self.viz = Visdom(server=self.visdom_addr, port=self.visdom_port, env=self.env_name)

    def stop(self):
        """Stop the dashboard."""
        self.viz = None


def start_visdom_server() -> subprocess.Popen:
    """Start the visdom server."""
    visdom_server_args = ["python", "-m", "visdom.server", "-env_path", os.path.join(CUR_DIR, "..", ".visdom_env")]
    print(" ".join(visdom_server_args))
    prog = subprocess.Popen(visdom_server_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    print("Visdom server running at http://localhost:8097")
    return prog