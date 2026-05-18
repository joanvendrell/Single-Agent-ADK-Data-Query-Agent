from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "sensor_data.xlsx"

VALID_FILTER_TYPES = {"location", "sensor_type", "value_range", "anomaly_label"}
VALID_SENSOR_TYPES = {"temperature", "pressure", "gas", "vibration"}
