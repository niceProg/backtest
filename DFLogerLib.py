from AlgorithmImports import *
import json


# =========================================================
# PAYLOAD CONTRACTS
# =========================================================

class SignalPayloadContract:
    REQUIRED = {
        "id_method",
        "datetime",
        "type",
        "jenis",
        "price_entry",
        "price_exit",
        "target_tp",
        "target_sl",
        "real_tp",
        "real_sl",
        "leverage",
        "quantity",
        "ratio",
        "message",
    }

    @staticmethod
    def validate(data: dict):
        missing = SignalPayloadContract.REQUIRED - data.keys()
        if missing:
            raise ValueError(f"Missing SIGNAL payload fields: {missing}")


class OrderPayloadContract:
    REQUIRED = {
        "id_method",
        "datetime",
        "type",
        "jenis",
        "price",
        "quantity",
        "balance",
        "message",
    }

    @staticmethod
    def validate(data: dict):
        missing = OrderPayloadContract.REQUIRED - data.keys()
        if missing:
            raise ValueError(f"Missing ORDER payload fields: {missing}")


class LogPayloadContract:
    REQUIRED = {
        "id_method",
        "datetime",
        "message",
    }

    @staticmethod
    def validate(data: dict):
        missing = LogPayloadContract.REQUIRED - data.keys()
        if missing:
            raise ValueError(f"Missing LOG payload fields: {missing}")


class ReminderPayloadContract:
    REQUIRED = {
        "id_method",
        "datetime",
        "message",
    }

    @staticmethod
    def validate(data: dict):
        missing = ReminderPayloadContract.REQUIRED - data.keys()
        if missing:
            raise ValueError(f"Missing REMINDER payload fields: {missing}")


# =========================================================
# DF LOGGER
# =========================================================

class DFLogger:
    """
    DFLoggerLib
    """

    # =========================
    # INIT
    # =========================
    @staticmethod
    def init(algo, strategy_id, base_url, is_backtest):
        return DFLogger(
            algo=algo,
            strategy_id=strategy_id,
            base_url=base_url.rstrip("/"),
            is_backtest=is_backtest
        )

    def __init__(self, algo, strategy_id, base_url, is_backtest):
        self.algo = algo
        self.strategy_id = strategy_id
        self.base_url = base_url
        self.is_backtest = is_backtest

    # =========================
    # ENDPOINT RESOLVER
    # =========================
    def _endpoint(self, name: str) -> str:
        """
        name:
        - signals
        - orders
        - logs
        - reminders
        - heartbeat
        """
        if self.is_backtest:
            return f"/backtest-{name}"
        return f"/{name}"

    def _url(self, name: str) -> str:
        return self.base_url + self._endpoint(name)

    # =========================
    # CORE SEND 
    # =========================
    def _send(self, endpoint: str, payload: dict):
        try:
            self.algo.Notify.Web(
                self._url(endpoint),
                json.dumps(payload, separators=(",", ":"))
            )
            self.algo.Debug(f"[DFLogger] POST {self._url(endpoint)}")
            return True
        except Exception as e:
            self.algo.Debug(f"[DFLogger][SEND ERROR] {e}")
            return False

    # =========================
    # BUILDERS (ANTI TYPO)
    # =========================
    def build_signal_payload(
        self,
        *,
        type,
        jenis,
        price_entry,
        price_exit,
        target_tp,
        target_sl,
        real_tp,
        real_sl,
        leverage,
        quantity,
        ratio,
        message,
    ):
        data = {
            "id_method": self.strategy_id,
            "datetime": self.algo.Time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": type,
            "jenis": jenis,
            "price_entry": float(price_entry),
            "price_exit": float(price_exit),
            "target_tp": float(target_tp),
            "target_sl": float(target_sl),
            "real_tp": float(real_tp),
            "real_sl": float(real_sl),
            "leverage": float(leverage),
            "quantity": float(quantity),
            "ratio": float(ratio),
            "message": message,
        }

        SignalPayloadContract.validate(data)
        return data

    def build_order_payload(
        self,
        *,
        type,
        jenis,
        price,
        quantity,
        balance,
        message,
    ):
        data = {
            "id_method": self.strategy_id,
            "datetime": self.algo.Time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": type,
            "jenis": jenis,
            "price": float(price),
            "quantity": float(quantity),
            "balance": float(balance),
            "message": message,
        }

        OrderPayloadContract.validate(data)
        return data

    def build_log_payload(self, *, message):
        data = {
            "id_method": self.strategy_id,
            "datetime": self.algo.Time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": message,
        }

        LogPayloadContract.validate(data)
        return data

    def build_reminder_payload(self, *, message):
        data = {
            "id_method": self.strategy_id,
            "datetime": self.algo.Time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": message,
        }

        ReminderPayloadContract.validate(data)
        return data

    # =========================
    # PUBLIC SEND METHODS
    # =========================
    def send_signal(self, **kwargs):
        try:
            payload = self.build_signal_payload(**kwargs)
            json_string = json.dumps(payload)
            self.algo.Debug(f"[DFLogger][SEND SIGNAL] {json_string}")
            return self._send("signals", payload)
        except Exception as e:
            self.algo.Debug(f"[DFLogger][SIGNAL PAYLOAD ERROR] {e}")
            return False

    def send_order(self, **kwargs):
        try:
            payload = self.build_order_payload(**kwargs)
            json_string = json.dumps(payload)
            self.algo.Debug(f"[DFLogger][SEND ORDER] {json_string}")
            return self._send("orders", payload)
        except Exception as e:
            self.algo.Debug(f"[DFLogger][ORDER PAYLOAD ERROR] {e}")
            return False

    def log(self, message: str):
        try:
            payload = self.build_log_payload(message=message)
            json_string = json.dumps(payload)
            self.algo.Debug(f"[DFLogger][SEND LOG] {json_string}")
            return self._send("logs", payload)
        except Exception as e:
            self.algo.Debug(f"[DFLogger][LOG ERROR] {e}")
            return False

    def send_reminder(self, message: str):
        try:
            payload = self.build_reminder_payload(message=message)
            json_string = json.dumps(payload)
            self.algo.Debug(f"[DFLogger][SEND REMINDER] {json_string}")
            return self._send("reminders", payload)
        except Exception as e:
            self.algo.Debug(f"[DFLogger][REMINDER ERROR] {e}")
            return False

    def heartbeat(self):
        payload = {
            "id_method": self.strategy_id,
            "datetime": self.algo.Time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": "running",
        }
        return self._send("logs", payload)
