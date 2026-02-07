--
-- Table structure for table `cg_spot_aggregated_taker_volume_history`
--

CREATE TABLE `cg_spot_aggregated_taker_volume_history` (
  `id` bigint(20) NOT NULL,
  `exchange_name` varchar(50) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `interval` varchar(10) NOT NULL,
  `unit` varchar(10) NOT NULL DEFAULT 'usd',
  `time` bigint(20) NOT NULL,
  `aggregated_buy_volume_usd` decimal(38,8) DEFAULT NULL,
  `aggregated_sell_volume_usd` decimal(38,8) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cg_spot_aggregated_taker_volume_history`
--

INSERT INTO `cg_spot_aggregated_taker_volume_history` (`id`, `exchange_name`, `symbol`, `interval`, `unit`, `time`, `aggregated_buy_volume_usd`, `aggregated_sell_volume_usd`, `created_at`, `updated_at`) VALUES
(1, 'Binance', 'BTC', '30m', 'usd', 1732145400000, 13735632.76630000, 11794309.42600000, '2025-11-15 23:26:23', '2025-11-15 23:26:23'),
(2, 'Binance', 'BTC', '30m', 'usd', 1732147200000, 52522582.45400000, 32502471.60150000, '2025-11-15 23:26:23', '2025-11-15 23:26:23'),
(3, 'Binance', 'BTC', '30m', 'usd', 1732149000000, 42831589.10720000, 39161872.71350000, '2025-11-15 23:26:23', '2025-11-15 23:26:23'),
(4, 'Binance', 'BTC', '30m', 'usd', 1732150800000, 28787962.69390000, 34578645.75150000, '2025-11-15 23:26:23', '2025-11-15 23:26:23'),
(5, 'Binance', 'BTC', '30m', 'usd', 1732152600000, 13392076.44970000, 25756765.77430000, '2025-11-15 23:26:23', '2025-11-15 23:26:23')

--
-- Table structure for table `cg_spot_price_history`
--

CREATE TABLE `cg_spot_price_history` (
  `id` bigint(20) NOT NULL,
  `exchange` varchar(50) NOT NULL,
  `symbol` varchar(50) NOT NULL,
  `interval` varchar(10) NOT NULL,
  `time` bigint(20) NOT NULL,
  `open` decimal(30,10) DEFAULT NULL,
  `high` decimal(30,10) DEFAULT NULL,
  `low` decimal(30,10) DEFAULT NULL,
  `close` decimal(30,10) DEFAULT NULL,
  `volume_usd` decimal(38,8) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cg_spot_price_history`
--

INSERT INTO `cg_spot_price_history` (`id`, `exchange`, `symbol`, `interval`, `time`, `open`, `high`, `low`, `close`, `volume_usd`, `created_at`, `updated_at`) VALUES
(1, 'Binance', 'BTCUSDT', '1m', 1763182620000, 96133.4300000000, 96146.0100000000, 96105.2100000000, 96146.0100000000, 541874.57350000, '2025-11-15 21:36:55', '2025-11-15 21:36:55'),
(2, 'Binance', 'BTCUSDT', '1m', 1763182680000, 96146.0100000000, 96169.7400000000, 96106.7500000000, 96120.9200000000, 496771.14240000, '2025-11-15 21:36:55', '2025-11-15 21:37:54'),
(3, 'Binance', 'BTCUSDT', '1m', 1763182740000, 96120.9200000000, 96120.9200000000, 96112.1300000000, 96112.1400000000, 164821.04680000, '2025-11-15 21:36:55', '2025-11-15 21:38:51'),
(4, 'Binance', 'BTCUSDT', '1m', 1763182800000, 96112.1400000000, 96130.7500000000, 96105.2200000000, 96105.2300000000, 522056.46410000, '2025-11-15 21:36:55', '2025-11-15 21:38:51'),
(5, 'Binance', 'BTCUSDT', '1m', 1763182860000, 96105.2200000000, 96146.6000000000, 96105.2200000000, 96146.6000000000, 671211.42790000, '2025-11-15 21:36:55', '2025-11-15 21:38:51')

--
-- Table structure for table `cg_spot_taker_volume_history`
--

CREATE TABLE `cg_spot_taker_volume_history` (
  `id` bigint(20) NOT NULL,
  `exchange` varchar(50) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `interval` varchar(10) NOT NULL,
  `unit` varchar(10) NOT NULL DEFAULT 'usd',
  `time` bigint(20) NOT NULL,
  `aggregated_buy_volume_usd` decimal(38,8) DEFAULT NULL,
  `aggregated_sell_volume_usd` decimal(38,8) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cg_spot_taker_volume_history`
--

INSERT INTO `cg_spot_taker_volume_history` (`id`, `exchange`, `symbol`, `interval`, `unit`, `time`, `aggregated_buy_volume_usd`, `aggregated_sell_volume_usd`, `created_at`, `updated_at`) VALUES
(1, 'Binance', 'BTC', '30m', 'usd', 1732147200000, 52522582.45400000, 32502471.60150000, '2025-11-15 23:48:40', '2025-11-15 23:48:40'),
(2, 'Binance', 'BTC', '30m', 'usd', 1732149000000, 42831589.10720000, 39161872.71350000, '2025-11-15 23:48:40', '2025-11-15 23:48:40'),
(3, 'Binance', 'BTC', '30m', 'usd', 1732150800000, 28787962.69390000, 34578645.75150000, '2025-11-15 23:48:40', '2025-11-15 23:48:40'),
(4, 'Binance', 'BTC', '30m', 'usd', 1732152600000, 13392076.44970000, 25756765.77430000, '2025-11-15 23:48:40', '2025-11-15 23:48:40'),
(5, 'Binance', 'BTC', '30m', 'usd', 1732154400000, 25526906.46880000, 53271742.99170000, '2025-11-15 23:48:40', '2025-11-15 23:48:40')