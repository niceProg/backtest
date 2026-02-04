from AlgorithmImports import *


class CheckBybitFutures(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2024, 1, 1)
        self.SetEndDate(2024, 1, 2)
        self.SetCash(10000)

        has_bybit_futures = hasattr(BrokerageName, "BybitFutures")
        self.Debug(f"Has BybitFutures: {has_bybit_futures}")

        if has_bybit_futures:
            self.SetBrokerageModel(BrokerageName.BybitFutures)
        else:
            self.Debug("BybitFutures not available in this environment.")
