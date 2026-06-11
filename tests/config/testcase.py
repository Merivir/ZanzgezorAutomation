import pytest


def testcase(testlink_id, title):
    """Attach TestLink metadata to a pytest test."""
    def decorator(test_func):
        test_func.testlink_id = testlink_id
        test_func.testcase_title = title
        return pytest.mark.testlink(testlink_id, title)(test_func)

    return decorator


testcase.__test__ = False
