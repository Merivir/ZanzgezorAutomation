class AutomationTestError(AssertionError):
    """Base class for readable automation failures."""


class TestStepError(AutomationTestError):
    def __init__(self, step_name, original_error):
        self.step_name = step_name
        self.original_error = original_error
        original_type = original_error.__class__.__name__
        super().__init__(f"Step failed: {step_name}. {original_type}: {original_error}")