from AlgorithmImports import *


class CheckBybit(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2024, 1, 1)
        self.SetEndDate(2024, 1, 2)
        self.SetCash(10000)

        has_bybit = hasattr(BrokerageName, "Bybit")
        self.Debug(f"Has Bybit: {has_bybit}")

        if has_bybit:
            self.SetBrokerageModel(BrokerageName.Bybit)
        else:
            self.Debug("Bybit not available in this environment.")
