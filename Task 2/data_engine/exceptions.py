class DataEngineError(Exception): pass
class ValidationError(DataEngineError): pass
class DuplicateRecordError(DataEngineError): pass
class RecordNotFoundError(DataEngineError): pass
class EnrollmentError(DataEngineError): pass
class StorageError(DataEngineError): pass
