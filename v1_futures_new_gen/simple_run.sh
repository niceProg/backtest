#!/bin/bash

# Simple script untuk menjalankan pipeline XGBoost step by step

echo "========================================"
echo "XGBoost Futures Pipeline - Manual Run"
echo "========================================"

# Default parameters
EXCHANGE=${EXCHANGE:-binance}
PAIR=${PAIR:-ETHUSDT}
INTERVAL=${INTERVAL:-1h}
MODEL_VERSION=${MODEL_VERSION:-}
OUTPUT_DIR=${OUTPUT_DIR:-}

if [ -z "$MODEL_VERSION" ]; then
    case "${PAIR^^}" in
        BTCUSDT)
            MODEL_VERSION="futures_new_gen_btc"
            ;;
        ETHUSDT)
            MODEL_VERSION="futures_new_gen_eth"
            ;;
        *)
            echo "❌ MODEL_VERSION is required. Example: futures_new_gen_btc or futures_new_gen_eth"
            exit 1
            ;;
    esac
fi

if [ -z "$OUTPUT_DIR" ]; then
    case "${PAIR^^}" in
        BTCUSDT)
            OUTPUT_DIR="./output_train_futures_new_gen"
            ;;
        ETHUSDT)
            OUTPUT_DIR="./output_train_futures_new_gen_eth"
            ;;
        *)
            OUTPUT_DIR="./output_train_futures_new_gen"
            ;;
    esac
fi

echo "Configuration:"
echo "  Exchange: $EXCHANGE"
echo "  Pair: $PAIR"
echo "  Interval: $INTERVAL"
echo "  Model Version: $MODEL_VERSION"
echo "  Output Directory: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Function to run a step
run_step() {
    local script=$1
    local step_name=$2
    shift 2  # Remove first two arguments, remaining are flags
    local extra_flags="$@"  # Capture all remaining flags

    echo "=========================================="
    echo "Running $step_name..."
    echo "Command: python $script $extra_flags --exchange $EXCHANGE --pair $PAIR --interval $INTERVAL --output-dir $OUTPUT_DIR --model-version $MODEL_VERSION"
    echo "=========================================="

    if python "$script" $extra_flags \
        --exchange "$EXCHANGE" \
        --pair "$PAIR" \
        --interval "$INTERVAL" \
        --output-dir "$OUTPUT_DIR" \
        --model-version "$MODEL_VERSION"; then
        echo "✅ $step_name completed successfully"
        echo ""
    else
        echo "❌ $step_name failed!"
        echo "Pipeline stopped."
        exit 1
    fi
}

# Parse extra flags (optional: --days N, --time start,end)
EXTRA_FLAGS=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --days)
            EXTRA_FLAGS="$EXTRA_FLAGS --days $2"
            shift 2
            ;;
        --time)
            EXTRA_FLAGS="$EXTRA_FLAGS --time $2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Run each step
run_step "load_database.py" "Step 1: Load Database" $EXTRA_FLAGS
run_step "merge_6_tables.py" "Step 2: Merge Tables" $EXTRA_FLAGS
run_step "feature_engineering.py" "Step 3: Feature Engineering" $EXTRA_FLAGS
run_step "label_builder.py" "Step 4: Label Building" $EXTRA_FLAGS
run_step "xgboost_trainer.py" "Step 5: Model Training" $EXTRA_FLAGS


echo "=========================================="
echo "✅ Pipeline completed successfully!"
echo "=========================================="

# Show structured output directory contents
echo ""
echo "Structured Output Directory Contents:"
echo "📁 $OUTPUT_DIR/"
ls -la "$OUTPUT_DIR"

echo ""
echo "📁 Model files:"
if [ -d "$OUTPUT_DIR/models" ]; then
    ls -la "$OUTPUT_DIR/models/"
else
    ls -la "$OUTPUT_DIR"/*.joblib 2>/dev/null || echo "No model files found"
fi

echo ""
echo "📁 Dataset files:"
if [ -d "$OUTPUT_DIR/datasets" ]; then
    echo "  📄 Dataset summary:"
    ls -la "$OUTPUT_DIR/datasets/"*summary*.txt 2>/dev/null || echo "  No dataset summary found"
    echo ""
    echo "  📄 Datasets:"
    ls -la "$OUTPUT_DIR/datasets/"*.parquet 2>/dev/null || echo "  No dataset files found"
fi

echo ""
echo "📁 Feature files:"
if [ -d "$OUTPUT_DIR/features" ]; then
    ls -la "$OUTPUT_DIR/features/" || echo "No feature files found"
fi

echo ""
echo "Next steps:"
echo "1. Access structured API: http://localhost:8000/output_train_futures/"
echo "2. View latest model: http://localhost:8000/output_train_futures/models/latest"
echo "3. View dataset summary: http://localhost:8000/output_train_futures/datasets/summary"
echo ""
echo "✅ Pipeline completed with structured output!"
echo "📁 New structure ready for production-v2 API access"
