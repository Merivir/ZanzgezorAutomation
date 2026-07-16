from contextlib import contextmanager
from functools import wraps

from tests.helpers.exceptions import TestStepError
from tests.helpers.log_colors import cyan_text, green_text, red_text


__test__ = False


def _step_title(name):
    return str(name).replace("_", " ").strip().capitalize()


def _logger_from(args, kwargs):
    candidates = list(args) + list(kwargs.values())
    for candidate in candidates:
        if hasattr(candidate, "log_action"):
            return candidate.log_action
    return lambda message: print(message, flush=True)


@contextmanager
def test_step_context(step_name, logger=None):
    logger = logger or (lambda message: print(message, flush=True))
    logger(cyan_text("=" * 90))
    logger(cyan_text(f"START STEP: {step_name}"))
    try:
        yield
    except TestStepError:
        raise
    except Exception as error:
        logger(red_text("!" * 90))
        logger(red_text(f"FAILED STEP: {step_name}"))
        logger(red_text(f"ERROR TYPE: {error.__class__.__name__}"))
        logger(red_text(f"ERROR MESSAGE: {error}"))
        logger(red_text("!" * 90))
        raise TestStepError(step_name, error) from error
    else:
        logger(green_text(f"PASSED STEP: {step_name}"))
        logger(cyan_text("=" * 90))


def test_step(step_name=None):
    def decorator(func):
        title = step_name or _step_title(func.__name__)

        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = _logger_from(args, kwargs)
            with test_step_context(title, logger):
                return func(*args, **kwargs)

        return wrapper

    return decorator