import logging
import os

import structlog
from structlog.contextvars import merge_contextvars


def setup_logging(log_file_name="app.log", logger_name="BackendApp"):
    """
    Configures logging using structlog with file output.

    Args:
        log_file_name: Name of the log file (default: app.log)
        logger_name: Name for the logger (default: BackendApp)
    """
    # Get the directory where this config file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up to the backend directory
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    logs_dir = os.path.join(backend_dir, "logs")

    # Create logs directory if it doesn't exist
    os.makedirs(logs_dir, exist_ok=True)

    # Use absolute path for log file
    log_file_path = os.path.join(logs_dir, log_file_name)

    # Ensure the logs directory has write permissions
    try:
        # Test write access
        with open(log_file_path, "a") as f:
            pass
    except PermissionError:
        print(f"Warning: No write permission to {log_file_path}")
        # Fallback to current directory
        log_file_path = log_file_name

    # Configure basic logging
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
        filemode="a",  # Append mode
    )

    # Log where the log file is being created
    print(f"Logging configured for {logger_name}. Log file: {log_file_path}")

    # Test logging to ensure it's working
    test_logger = logging.getLogger("LoggingTest")
    test_logger.info(
        f"Logging system initialized for {logger_name}. Log file: {log_file_path}"
    )

    def rename_fields(_, __, event_dict):
        if "event" in event_dict:
            event_dict["message"] = event_dict.pop("event")
        if "logger" in event_dict:
            event_dict["Module"] = event_dict.pop("logger")
        return event_dict

    structlog.configure(
        processors=[
            merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=True),
            rename_fields,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger(logger_name)


# Default logger for backward compatibility
logger = setup_logging()
