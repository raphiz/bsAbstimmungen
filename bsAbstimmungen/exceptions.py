class BSAbstimmungenException(Exception):
    '''root for bsAbstimmungen  Exceptions, only used to except any
        bsAbstimmungen error, never raised'''
    pass


class ImporterException(BSAbstimmungenException):
    pass


class ParserException(ImporterException):
    pass


class AlreadyImportedException(ImporterException):
    pass


class DownloadException(ImporterException):
    pass
