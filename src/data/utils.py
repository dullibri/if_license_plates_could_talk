def fix_key(ser):
    return ser.astype(int).astype(str).str.zfill(5)