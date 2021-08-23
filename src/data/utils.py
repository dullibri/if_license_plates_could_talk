def fix_key(ser):
    """Transform int to 5-digit str, padded with zeros. Ex: 101 -> 00101"""
    return ser.astype(int).astype(str).str.zfill(5)
