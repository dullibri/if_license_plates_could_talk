import os


def fix_key(ser):
    """ Transform int to 5-digit str, padded with zeros. Ex: 101 -> 00101
        This is the proper format for regional keys.
    """
    return ser.astype(int).astype(str).str.zfill(5)


def path_to_data_dir():
    """Returns absolute path to data directory"""
    return os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
