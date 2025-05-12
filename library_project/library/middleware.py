import logging
import time
from django.db import transaction
from django.db.utils import OperationalError, DatabaseError

logger = logging.getLogger(__name__)

class DeadlockRetryMiddleware:
    """
    Middleware to handle MySQL database deadlocks and lock‐timeout errors by retrying transactions.
    
    Catches MySQL deadlock (error 1213) and lock‐wait timeout (error 1205) exceptions,
    then retries the request with exponential backoff.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_retries = 3     # Maximum retry attempts
        self.initial_delay = 0.1 # Seconds before first retry
    
    def __call__(self, request):
        retries = 0
        delay = self.initial_delay

        while True:
            try:
                with transaction.atomic():
                    response = self.get_response(request)
                return response

            except (OperationalError, DatabaseError) as e:
                error_code = self._get_mysql_error_code(e)

                # MySQL retriable errors:
                # 1213: Deadlock found when trying to get lock
                # 1205: Lock wait timeout exceeded
                retriable_errors = [1213, 1205]

                if error_code in retriable_errors and retries < self.max_retries:
                    retries += 1
                    logger.warning(
                        f"MySQL error {error_code} detected. "
                        f"Retrying request (attempt {retries}/{self.max_retries}) "
                        f"after {delay:.2f}s backoff."
                    )
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    logger.error(
                        f"MySQL error {error_code or 'Unknown'}: {e}. "
                        "Maximum retries exceeded or non-retriable error."
                    )
                    raise

    def _get_mysql_error_code(self, exception):
        """
        Extract the MySQL error code from a Django OperationalError/DatabaseError.
        MySQLdb/pymysql normally populates exception.args[0] with the numeric code.
        """
        if hasattr(exception, 'args') and exception.args:
            code = exception.args[0]
            try:
                return int(code)
            except (TypeError, ValueError):
                pass
        return None
