"""Pre-work jobs - handle config and/or CLI"""
import json
import os.path
# 3. local
from typing import Optional

from . import exc


class UlibCfgLoadError(exc.UlibTextError):
    """Config loading exceptions."""
    name = "CfgLoad"


def cli():
    """Handle CLI"""
    ...


def load_cfg(fname: str) -> Optional[dict]:
    """Load config (near > ~ > /etc)
    :return: Config loaded
    """
    for d in ('.', os.path.expanduser('~/.config'), '/etc'):
        fpath = os.path.join(d, fname)
        if not os.path.exists(fpath):  # or handle FileNotFoundError
            continue
        try:
            return json.load(open(fpath))
        except (IsADirectoryError, PermissionError, json.decoder.JSONDecodeError) as e:
            raise UlibCfgLoadError(f"'{fpath}': {str(e)}")
    return