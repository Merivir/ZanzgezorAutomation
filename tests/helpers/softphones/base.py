class SoftphoneClient:
    provider_name = "base"

    def log_action(self, message):
        print(f"[{self.provider_name}] {message}", flush=True)

    def missing_setup_reason(self):
        return ""

    def configure_account(self, extension, password):
        raise NotImplementedError

    def configure_call_control(self, mode=None):
        raise NotImplementedError

    def start(self):
        return self.restart()

    def stop(self):
        raise NotImplementedError

    def restart(self):
        raise NotImplementedError

    def restore_config_backup(self):
        return self

    def wait_for_incoming_call(self, marker=None, timeout=30):
        raise NotImplementedError

    def decline_incoming_call(self):
        raise NotImplementedError

    def call_succeeds(self, number=None, extension=None, password=None):
        raise NotImplementedError

    def call_is_declined(self, number=None, extension=None, password=None):
        return not self.call_succeeds(number=number, extension=extension, password=password)
