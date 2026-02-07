from AlgorithmImports import *
from DFLoggerLib import DFLogger


class DFLoggerSmokeTest(QCAlgorithm):
    """
    Strategy ini hanya untuk TESTING DFLoggerLib
    - Tidak melakukan trading sungguhan
    - Fokus memastikan semua endpoint terpanggil dengan payload benar
    """

    def Initialize(self):
        # ===============================
        # BASIC CONFIG
        # ===============================
        self.SetStartDate(2024, 1, 1)
        self.SetEndDate(2024, 1, 3)
        self.SetCash(1000)

        # Dummy asset (tidak dipakai trading)
        self.symbol = self.AddCrypto("BTCUSDT", Resolution.HOUR).Symbol

        # ===============================
        # INIT LOGGER PROD
        # Uncomment bagian ini maka otomatis akan terintegrasi dengan dragonfortune.ai versi prod
        # ===============================
        # self.strategy_id = 9999 #tanya strategy_id prod nya ke tim programmer dulu
        # self.logger_base_url = "https://test.dragonfortune.ai"

        # self.logger = DFLogger.init(
        #     algo=self,
        #     strategy_id=self.strategy_id,
        #     base_url=self.logger_base_url,
        #     is_backtest= False
        # )

        # ===============================
        # INIT LOGGER DEV
        # Wajib di coba dulu sebelum live
        # ===============================
        self.strategy_id = 999 
        self.logger_base_url = "https://dev.dragonfortune.ai"

        self.logger = DFLogger.init(
            algo=self,
            strategy_id=self.strategy_id,
            base_url=self.logger_base_url,
            is_backtest= True
        )

        # ===============================
        # SCHEDULE TEST
        # ===============================
        self.Schedule.On(
            self.DateRules.Today,
            self.TimeRules.At(0, 1),
            self.logger.heartbeat
        )

        # Heartbeat
        # self.Schedule.On(
        #     self.DateRules.EveryDay(),
        #     self.TimeRules.Every(timedelta(hours=3)),
        #     self.logger.heartbeat()
        # )

        self.Debug("DFLogger smoke test initialized")

    # run_tests adalah contoh fungsi log library
    def run_tests(self):
        """
        Jalankan semua test endpoint 1x
        """
        price = self.Securities[self.symbol].Price or 30000

        # ======================================================
        # 1. LOGS
        # ======================================================
        self.logger.log(
            message="[TEST] Logger log endpoint OK"
        )

        # ======================================================
        # 2. SIGNALS (ENTRY)
        # ======================================================
        self.logger.send_signal(
            type="entry",
            jenis="entry_long",
            price_entry=price,
            price_exit=0,
            target_tp=price * 1.02,
            target_sl=price * 0.98,
            real_tp=0,
            real_sl=0,
            leverage=10,
            quantity=0.01,
            ratio=2.0,
            message="[TEST] Signal entry sent"
        )

        # ======================================================
        # 3. SIGNALS (EXIT)
        # ======================================================
        self.logger.send_signal(
            type="exit",
            jenis="exit_long",
            price_entry=price,
            price_exit=price * 1.01,
            target_tp=price * 1.02,
            target_sl=price * 0.98,
            real_tp=price * 1.01,
            real_sl=0,
            leverage=10,
            quantity=0.01,
            ratio=2.0,
            message="[TEST] Signal exit sent"
        )

        # ======================================================
        # 4. ORDERS (ENTRY FILLED)
        # ======================================================
        self.logger.send_order(
            type="entry",
            jenis="entry_long",
            price=price,
            quantity=0.01,
            balance=self.Portfolio.Cash,
            message="[TEST] Order entry filled"
        )

        # ======================================================
        # 5. ORDERS (EXIT FILLED)
        # ======================================================
        self.logger.send_order(
            type="exit",
            jenis="exit_long",
            price=price * 1.01,
            quantity=0.01,
            balance=self.Portfolio.Cash,
            message="[TEST] Order exit filled"
        )

        # ======================================================
        # 6. REMINDER
        # ======================================================
        self.logger.send_reminder(
            message="[TEST] Reminder endpoint OK"
        )

        # ======================================================
        # 7. HEARTBEAT
        # ======================================================
        self.logger.heartbeat()

        self.Debug("DFLogger smoke test finished")

    def OnData(self, data: Slice):

        # pass

        if self.IsWarmingUp:
            return

        self.logger.heartbeat()
