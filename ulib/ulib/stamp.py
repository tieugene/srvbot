"""Handle backup stamps"""

# 1. std
from typing import Optional
import logging
import os.path
import urllib.error
import urllib.request
import http.client
# 3. local
from . import exc


# TODO: split into critical and skipable errors
class UlibGetStampError(exc.UlibTextError):
    """Stamp loading exceptions."""
    name = "GetStamp"


class UlibSetStampError(exc.UlibTextError):
    """Stamp saving exceptions."""
    name = "SetStamp"


def get_stamp(path: str) -> Optional[int]:
    """Ask local/remote stamp.
    :return: stamp content or None if not exists
    """
    if path.startswith('/'):  # file
        if os.path.exists(path):
            try:
                return int(open(path, 'rt').read())
            except (IsADirectoryError, PermissionError, ValueError) as e:  # !file, !permit, !int
                # TODO: handle open(), read()
                msg = f"'{path}': str{e}"
                logging.error(msg)
                raise UlibGetStampError(msg)
        else:
            logging.debug(f"'{path}' not exists")
    elif path.startswith('http://'):  # remote
        try:
            rsp: http.client.HTTPResponse = urllib.request.urlopen(path, timeout=10)
        except urllib.error.URLError as e:  # !network, !VPN
            msg = f"'{path}': urllib: {str(e)}"
            logging.warning(msg)
            raise UlibGetStampError(msg)
        if rsp.status == http.client.NOT_FOUND:  # busy (no stamp yet)
            logging.debug(f"'{path}' not exists")
            return
        elif rsp.status == http.client.OK:
            try:
                return int(rsp.read().decode())
            except ValueError as e:
                msg = f"'{path}': {str(e)}"
                logging.error(msg)
                raise UlibGetStampError(msg)
        else:
            msg = f"'{path}': Response {rsp.status} ({rsp.reason})"
            logging.error(msg)
            raise UlibGetStampError(msg)
    else:
        msg = f"'{path}': unknown scheme"
        logging.error(msg)
        raise UlibGetStampError(msg)
    # default = None (stamp is absent)


def set_stamp(path: str, stamp: int):
    try:
        open(path, 'wt').write(str(stamp))
    except (OSError, PermissionError) as e:
        msg = f"'{path}': {str(e)}"
        logging.error(msg)
        raise UlibSetStampError(msg)
