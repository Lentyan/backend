class ReportGenerationError(Exception):
    """Custom exception for report generation errors."""

    def __init__(self, message, status_code):
        """Exception initialization."""
        super().__init__(message)
        self.status_code = status_code
