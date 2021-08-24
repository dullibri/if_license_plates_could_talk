class DataException(Exception):
    """Base class for data exceptions"""
    pass


class RawDataMissingException(DataException):
    pass


class PreprocessedDataMissingException(DataException):
    pass


class UnexpectedDatatypeException(DataException):
    pass
