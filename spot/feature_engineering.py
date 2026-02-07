#!/usr/bin/env python3
"""
Feature engineering for spot trading tables based on semantic nature of each dataset.
Implements spot-focused features for XGBoost training.
Spot-only with 3 core tables (price, taker, aggregated taker).
"""

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Import our command line options handler
from command_line_options import parse_arguments, validate_arguments, DataFilter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Implement feature engineering based on futures table semantics."""

    def __init__(self, data_filter: DataFilter, output_dir: str = './output_train'):
        self.data_filter = data_filter
        self.output_dir = Path(output_dir)
        self.feature_columns = []

    def load_merged_data(self) -> pd.DataFrame:
        """Load merged data from previous step."""
        logger.info("Loading merged data...")

        # Try datasets directory first (new structure), then root (compatibility)
        datasets_dir = self.output_dir / 'datasets'
        merged_file = datasets_dir / 'merged_3_tables.parquet'

        if not merged_file.exists():
            # Fallback to root directory for backward compatibility
            merged_file = self.output_dir / 'merged_3_tables.parquet'

        if not merged_file.exists():
            logger.error(f"Merged data file not found: {merged_file}")
            logger.error(f"Checked: {datasets_dir / 'merged_6_tables.parquet'} and {self.output_dir / 'merged_6_tables.parquet'}")
            sys.exit(1)

        try:
            df = pd.read_parquet(merged_file)
            logger.info(f"Loaded {len(df)} rows with {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"Error loading merged data: {e}")
            sys.exit(1)

    def add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add features for cg_futures_price_history (OHLCV)."""
        logger.info("Adding price features...")

        # Helper function for groupby rolling with proper index alignment
        def groupby_rolling_agg(series, window, func):
            result = df.groupby(['exchange', 'symbol', 'interval'])[series].rolling(window)
            if func == 'mean':
                return result.mean().groupby(level=[0,1,2]).transform('first').reset_index(level=[0,1,2], drop=True)
            elif func == 'std':
                return result.std().groupby(level=[0,1,2]).transform('first').reset_index(level=[0,1,2], drop=True)
            return result

        # Price returns
        df['price_close_return_1'] = df.groupby(['exchange', 'symbol', 'interval'])['price_close'].pct_change(1)
        df['price_close_return_5'] = df.groupby(['exchange', 'symbol', 'interval'])['price_close'].pct_change(5)
        df['price_log_return'] = np.log(df['price_close'] / df.groupby(['exchange', 'symbol', 'interval'])['price_close'].shift(1))

        # Rolling volatility - using direct calculation to avoid index issues
        df['price_rolling_vol_5'] = df.groupby(['exchange', 'symbol', 'interval'])['price_close_return_1'].transform(lambda x: x.rolling(5).std())

        # True range and candlestick features
        df['price_true_range'] = df['price_high'] - df['price_low']
        df['price_close_mean_5'] = df.groupby(['exchange', 'symbol', 'interval'])['price_close'].transform(lambda x: x.rolling(5).mean())
        df['price_close_std_5'] = df.groupby(['exchange', 'symbol', 'interval'])['price_close'].transform(lambda x: x.rolling(5).std())

        # Volume features
        df['price_volume_mean_10'] = df.groupby(['exchange', 'symbol', 'interval'])['price_volume_usd'].transform(lambda x: x.rolling(10).mean())
        volume_std_10 = df.groupby(['exchange', 'symbol', 'interval'])['price_volume_usd'].transform(lambda x: x.rolling(10).std())
        df['price_volume_zscore'] = (df['price_volume_usd'] - df['price_volume_mean_10']) / volume_std_10
        df['price_volume_change'] = df.groupby(['exchange', 'symbol', 'interval'])['price_volume_usd'].pct_change(1)

        # Candlestick features
        df['price_wick_upper'] = df['price_high'] - np.maximum(df['price_open'], df['price_close'])
        df['price_wick_lower'] = np.minimum(df['price_open'], df['price_close']) - df['price_low']
        df['price_body_size'] = np.abs(df['price_close'] - df['price_open'])

        self.feature_columns.extend([
            'price_close_return_1', 'price_close_return_5', 'price_log_return',
            'price_rolling_vol_5', 'price_true_range', 'price_close_mean_5',
            'price_close_std_5', 'price_volume_mean_10', 'price_volume_zscore',
            'price_volume_change', 'price_wick_upper', 'price_wick_lower', 'price_body_size'
        ])

        return df

    def add_funding_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add features for cg_funding_rate_history."""
        logger.info("Adding funding rate features...")

        if 'funding_close' not in df.columns:
            logger.warning("Funding rate data not available")
            return df

        # Normalized funding rate
        df['funding_norm'] = df['funding_close'] / 0.01

        # Rolling statistics using transform to maintain index compatibility
        df['funding_mean_24'] = df.groupby(['exchange', 'symbol', 'interval'])['funding_close'].transform(lambda x: x.rolling(24).mean())
        df['funding_std_24'] = df.groupby(['exchange', 'symbol', 'interval'])['funding_close'].transform(lambda x: x.rolling(24).std())
        df['funding_zscore'] = (df['funding_close'] - df['funding_mean_24']) / df['funding_std_24']

        # Extreme indicators
        df['funding_extreme_positive'] = (df['funding_close'] > 0.015).astype(int)  # > 1.5x standard rate
        df['funding_extreme_negative'] = (df['funding_close'] < -0.015).astype(int)  # < -1.5x standard rate

        self.feature_columns.extend([
            'funding_norm', 'funding_mean_24', 'funding_std_24',
            'funding_zscore', 'funding_extreme_positive', 'funding_extreme_negative'
        ])

        return df

    def add_basis_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add features for cg_futures_basis_history."""
        logger.info("Adding basis features...")

        if 'basis_close_basis' not in df.columns:
            logger.warning("Basis data not available")
            return df

        # Basis changes
        df['basis_delta'] = df.groupby(['exchange', 'symbol', 'interval'])['basis_close_basis'].diff()
        df['basis_drift'] = df['basis_close_basis'] - df['basis_open_basis']

        # Rolling statistics using transform to maintain index compatibility
        df['basis_mean_24'] = df.groupby(['exchange', 'symbol', 'interval'])['basis_close_basis'].transform(lambda x: x.rolling(24).mean())
        basis_std_24 = df.groupby(['exchange', 'symbol', 'interval'])['basis_close_basis'].transform(lambda x: x.rolling(24).std())
        df['basis_zscore'] = (df['basis_close_basis'] - df['basis_mean_24']) / basis_std_24
        df['basis_volatility_24'] = basis_std_24

        self.feature_columns.extend([
            'basis_delta', 'basis_drift', 'basis_mean_24',
            'basis_zscore', 'basis_volatility_24'
        ])

        return df

    def add_taker_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add features for spot taker volume tables (taker + aggregated)."""
        logger.info("Adding taker volume features...")

        prefixes = [
            ("taker", "taker_aggregated_buy_volume_usd", "taker_aggregated_sell_volume_usd"),
            ("agg_taker", "agg_taker_aggregated_buy_volume_usd", "agg_taker_aggregated_sell_volume_usd"),
        ]

        for prefix, buy_col, sell_col in prefixes:
            if buy_col not in df.columns or sell_col not in df.columns:
                logger.warning(f"{prefix} volume data not available")
                continue

            total_volume = df[buy_col] + df[sell_col]
            df[f'{prefix}_buy_ratio'] = df[buy_col] / total_volume
            df[f'{prefix}_imbalance'] = df[buy_col] - df[sell_col]

            df[f'{prefix}_buy_mean_12'] = df.groupby(['exchange', 'symbol', 'interval'])[buy_col].transform(lambda x: x.rolling(12).mean())
            df[f'{prefix}_sell_mean_12'] = df.groupby(['exchange', 'symbol', 'interval'])[sell_col].transform(lambda x: x.rolling(12).mean())
            df[f'{prefix}_buy_std_12'] = df.groupby(['exchange', 'symbol', 'interval'])[buy_col].transform(lambda x: x.rolling(12).std())
            df[f'{prefix}_sell_std_12'] = df.groupby(['exchange', 'symbol', 'interval'])[sell_col].transform(lambda x: x.rolling(12).std())

            df[f'{prefix}_buy_zscore'] = (df[buy_col] - df[f'{prefix}_buy_mean_12']) / df[f'{prefix}_buy_std_12']
            df[f'{prefix}_sell_zscore'] = (df[sell_col] - df[f'{prefix}_sell_mean_12']) / df[f'{prefix}_sell_std_12']

            self.feature_columns.extend([
                f'{prefix}_buy_ratio', f'{prefix}_imbalance', f'{prefix}_buy_mean_12',
                f'{prefix}_sell_mean_12', f'{prefix}_buy_std_12', f'{prefix}_buy_zscore', f'{prefix}_sell_zscore'
            ])

        return df

    def add_open_interest_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add features for cg_open_interest_aggregated_history."""
        logger.info("Adding open interest features...")

        if 'oi_close' not in df.columns:
            logger.warning("Open interest data not available")
            return df

        df['oi_delta'] = df.groupby(['symbol', 'interval'])['oi_close'].diff()
        df['oi_change_pct'] = df.groupby(['symbol', 'interval'])['oi_close'].pct_change(1)
        df['oi_mean_24'] = df.groupby(['symbol', 'interval'])['oi_close'].transform(lambda x: x.rolling(24).mean())
        df['oi_std_24'] = df.groupby(['symbol', 'interval'])['oi_close'].transform(lambda x: x.rolling(24).std())
        df['oi_zscore'] = (df['oi_close'] - df['oi_mean_24']) / df['oi_std_24']

        self.feature_columns.extend([
            'oi_delta', 'oi_change_pct', 'oi_mean_24', 'oi_std_24', 'oi_zscore'
        ])

        return df

    def add_longshort_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add features for long/short ratio tables."""
        logger.info("Adding long/short ratio features...")

        # Top account ratios only
        if 'ls_top_top_account_long_short_ratio' in df.columns:
            df['ls_top_ratio'] = df['ls_top_top_account_long_percent'] / df['ls_top_top_account_short_percent']
            top_mean_24 = df.groupby(['exchange', 'symbol', 'interval'])['ls_top_top_account_long_short_ratio'].transform(lambda x: x.rolling(24).mean())
            top_std_24 = df.groupby(['exchange', 'symbol', 'interval'])['ls_top_top_account_long_short_ratio'].transform(lambda x: x.rolling(24).std())
            df['ls_top_zscore'] = (df['ls_top_top_account_long_short_ratio'] - top_mean_24) / top_std_24
            df['ls_top_delta'] = df.groupby(['exchange', 'symbol', 'interval'])['ls_top_top_account_long_short_ratio'].diff()

            self.feature_columns.extend([
                'ls_top_ratio', 'ls_top_zscore', 'ls_top_delta'
            ])

        return df

    def add_cross_table_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add cross-table interaction features."""
        logger.info("Adding cross-table features...")

        # Initialize cross-table features
        cross_features = []

        if 'taker_buy_ratio' in df.columns and 'price_close_return_1' in df.columns:
            df['cross_taker_price'] = df['taker_buy_ratio'] * df['price_close_return_1']
            cross_features.append('cross_taker_price')

        if 'agg_taker_buy_ratio' in df.columns and 'price_close_return_1' in df.columns:
            df['cross_agg_taker_price'] = df['agg_taker_buy_ratio'] * df['price_close_return_1']
            cross_features.append('cross_agg_taker_price')

        if 'taker_imbalance' in df.columns and 'price_close_return_1' in df.columns:
            df['cross_taker_imbalance_price'] = df['taker_imbalance'] * df['price_close_return_1']
            cross_features.append('cross_taker_imbalance_price')

        if 'agg_taker_imbalance' in df.columns and 'price_close_return_1' in df.columns:
            df['cross_agg_taker_imbalance_price'] = df['agg_taker_imbalance'] * df['price_close_return_1']
            cross_features.append('cross_agg_taker_imbalance_price')

        self.feature_columns.extend(cross_features)
        logger.info(f"Added {len(cross_features)} cross-table features")

        return df

    def clean_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare features for ML."""
        logger.info("Cleaning features...")

        # Replace infinities with NaN
        df = df.replace([np.inf, -np.inf], np.nan)

        # Get feature columns only
        feature_cols = [col for col in self.feature_columns if col in df.columns]

        # Fill missing values with forward fill then backward fill
        for col in feature_cols:
            if df[col].dtype in ['float64', 'int64']:
                # Group by symbol/exchange/interval for proper filling
                df[col] = df.groupby(['exchange', 'symbol', 'interval'])[col].ffill().bfill()

        # Drop rows with missing essential features
        essential_features = ['price_close_return_1', 'price_rolling_vol_5']
        available_essential = [col for col in essential_features if col in df.columns]

        if available_essential:
            initial_rows = len(df)
            df = df.dropna(subset=available_essential)
            final_rows = len(df)
            logger.info(f"Dropped {initial_rows - final_rows} rows with missing essential features")

        # Report feature statistics
        feature_df = df[feature_cols]
        missing_counts = feature_df.isnull().sum()
        if missing_counts.any():
            logger.warning(f"Missing values in features after cleaning:\n{missing_counts[missing_counts > 0]}")

        logger.info(f"Final feature set: {len(feature_cols)} features")
        return df

    def validate_features(self, df: pd.DataFrame) -> bool:
        """Validate engineered features."""
        logger.info("\n=== Feature Validation ===")

        feature_cols = [col for col in self.feature_columns if col in df.columns]
        logger.info(f"Total engineered features: {len(feature_cols)}")

        if not feature_cols:
            logger.error("No features were created!")
            return False

        # Check for basic statistics
        feature_stats = df[feature_cols].describe()
        logger.info("Feature statistics summary:")
        logger.info(feature_stats.loc[['mean', 'std', 'min', 'max']].round(4))

        # Check for constant features
        constant_features = []
        for col in feature_cols:
            if df[col].nunique() <= 1:
                constant_features.append(col)

        if constant_features:
            logger.warning(f"Constant features found: {constant_features}")
        else:
            logger.info("No constant features found")

        logger.info("=" * 30)
        return True

    def save_features(self, df: pd.DataFrame):
        """Save engineered features."""
        if df.empty:
            logger.error("No data to save")
            return

        # Create directories
        datasets_dir = self.output_dir / 'datasets'
        features_dir = self.output_dir / 'features'
        datasets_dir.mkdir(exist_ok=True)
        features_dir.mkdir(exist_ok=True)

        # Save complete dataset with features to datasets directory
        output_file = datasets_dir / 'features_engineered.parquet'
        df.to_parquet(output_file, index=False)
        logger.info(f"Features saved to {output_file}")

        # Save feature list to features directory
        feature_cols = [col for col in self.feature_columns if col in df.columns]
        feature_file = features_dir / 'feature_list.txt'
        with open(feature_file, 'w') as f:
            f.write("Engineered Features:\n")
            f.write("=" * 20 + "\n")
            for col in feature_cols:
                f.write(f"{col}\n")
        logger.info(f"Feature list saved to {feature_file}")

        # Save features-only dataset to datasets directory
        features_df = df[feature_cols].copy()
        features_file = datasets_dir / 'features_only.parquet'
        features_df.to_parquet(features_file, index=False)
        logger.info(f"Features-only dataset saved to {features_file}")

        # Also keep copies in root for backward compatibility
        root_output_file = self.output_dir / 'features_engineered.parquet'
        root_features_file = self.output_dir / 'features_only.parquet'
        root_feature_file = self.output_dir / 'feature_list.txt'

        try:
            df.to_parquet(root_output_file, index=False)
            features_df.to_parquet(root_features_file, index=False)
            root_feature_file.write_text(feature_file.read_text())
            logger.info("Also saved copies to root directory for compatibility")
        except Exception as e:
            logger.warning(f"Could not save root compatibility copies: {e}")

        # Duplicate line removed

        # DATABASE STORAGE DISABLED per client requirement
        # Client tidak mau: xgboost_evaluations, xgboost_features, xgboost_training_sessions
        logger.info("📝 Feature database storage disabled per client requirement")

def main():
    """Main function to engineer features."""
    args = parse_arguments()
    validate_arguments(args)

    # Set up logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create data filter
    data_filter = DataFilter(args)

    # Initialize feature engineer
    engineer = FeatureEngineer(data_filter, args.output_dir)

    try:
        # Load merged data
        logger.info("Loading merged data for feature engineering...")
        df = engineer.load_merged_data()

        # Add features for each table type
        df = engineer.add_price_features(df)
        df = engineer.add_taker_volume_features(df)
        df = engineer.add_cross_table_features(df)

        # Clean features
        df = engineer.clean_features(df)

        # Validate features
        if not engineer.validate_features(df):
            sys.exit(1)

        # Save features
        engineer.save_features(df)

        logger.info("\n=== Feature Engineering Complete ===")
        logger.info("Ready for label_builder.py")

    except Exception as e:
        logger.error(f"Error in feature engineering: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
