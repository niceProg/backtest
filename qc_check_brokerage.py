from AlgorithmImports import *


class CheckBrokerage(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2024, 1, 1)
        self.SetEndDate(2024, 1, 2)
        self.SetCash(10000)

        names = [n for n in dir(BrokerageName) if not n.startswith("_")]
        bybit = [n for n in names if "Bybit" in n]
        binance = [n for n in names if "Binance" in n]

        self.Debug(f"BrokerageName has {len(names)} entries")
        self.Debug(f"Bybit-related: {bybit}")
        self.Debug(f"Binance-related: {binance}")
