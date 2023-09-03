class ProcessingException(Exception):
    def __init__(self, exception: Exception, source_file: str, destination_file: str):
        super().__init__(exception)
        self.exception = exception
        self.source_file = source_file
        self.destination_file = destination_file
