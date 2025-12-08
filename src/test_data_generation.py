"""
Generate test data with 10 columns (covering common Parquet + Avro types)
and 20 rows, then write to CSV, AVRO, and PARQUET formats.

Columns:
- id_int32            (int32)
- big_int64           (int64)
- flag_bool           (boolean)
- ratio_float         (float32)
- score_double        (float64)
- name_string         (utf8 string)
- payload_binary      (binary/bytes)
- amount_decimal      (decimal(18,4))
- order_date          (date)
- created_ts          (timestamp(millis))

Outputs:
- testdata.csv
- testdata.avro
- testdata.parquet
"""

import os
from datetime import date, datetime, timedelta
from decimal import Decimal, getcontext

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from fastavro import writer as avro_writer


def generate_data(n_rows: int = 20, seed: int = 42):
    np.random.seed(seed)
    getcontext().prec = 38  # sufficient for decimal128

    # 1) Primitive types
    id_int32 = np.arange(1, n_rows + 1, dtype=np.int32)
    big_int64 = np.random.randint(10**9, 10**10, size=n_rows, dtype=np.int64)  # large 64-bit ints
    flag_bool = np.random.choice([True, False], size=n_rows).astype(bool)
    ratio_float = (np.random.rand(n_rows) * 100).astype(np.float32)  # float32
    score_double = (np.random.randn(n_rows) * 1000).astype(np.float64)  # float64
    name_string = [f"row_{i:04d}" for i in range(1, n_rows + 1)]
    # payload_binary = [np.random.bytes(8) for _ in range(n_rows)]  # 8 bytes each

    # 2) Logical types
    # Decimal(18,4): generate some amounts with 4 decimal places
    raw_amounts = np.random.randint(10_000, 1_000_000, size=n_rows)  # integer cents
    amount_decimal = [Decimal(int(x)) / Decimal(10_000) for x in raw_amounts]  # scale=4

    # Date: sequential days from a start date
    start_d = date(2020, 1, 1)
    order_date = [start_d + timedelta(days=i) for i in range(n_rows)]

    # Timestamp (millis): sequential hours from a start datetime
    start_dt = datetime(2020, 1, 1, 0, 0, 0)
    created_ts = [start_dt + timedelta(hours=i) for i in range(n_rows)]

    # Build a pandas DataFrame for CSV output (object dtype is fine for non-primitive)
    df = pd.DataFrame(
        {
            "id_int32": id_int32,
            "big_int64": big_int64,
            "flag_bool": flag_bool,
            "ratio_float": ratio_float,
            "score_double": score_double,
            "name_string": name_string,
            # "payload_binary": payload_binary,  # will render as b'...' in CSV
            "amount_decimal": amount_decimal,  # Decimal -> string in CSV
            "order_date": order_date,  # date -> ISO string in CSV
            "created_ts": created_ts,  # datetime -> ISO string in CSV
        }
    )

    return {
        "df": df,
        "id_int32": id_int32,
        "big_int64": big_int64,
        "flag_bool": flag_bool,
        "ratio_float": ratio_float,
        "score_double": score_double,
        "name_string": name_string,
        # "payload_binary": payload_binary,
        "amount_decimal": amount_decimal,
        "order_date": order_date,
        "created_ts": created_ts,
    }


def write_csv(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)
    print(f"CSV written: {path}")


def write_parquet(columns: dict, path: str):
    """
    Write Parquet with explicit Arrow schema for precise Parquet types.
    """
    schema = pa.schema(
        [
            pa.field("id_int32", pa.int32()),
            pa.field("big_int64", pa.int64()),
            pa.field("flag_bool", pa.bool_()),
            pa.field("ratio_float", pa.float32()),
            pa.field("score_double", pa.float64()),
            pa.field("name_string", pa.string()),
            # pa.field("payload_binary", pa.binary()),
            pa.field("amount_decimal", pa.decimal128(18, 4)),  # precision=18, scale=4
            pa.field("order_date", pa.date32()),
            pa.field("created_ts", pa.timestamp("ms")),
        ]
    )

    arrays = [
        pa.array(columns["id_int32"], type=pa.int32()),
        pa.array(columns["big_int64"], type=pa.int64()),
        pa.array(columns["flag_bool"], type=pa.bool_()),
        pa.array(columns["ratio_float"], type=pa.float32()),
        pa.array(columns["score_double"], type=pa.float64()),
        pa.array(columns["name_string"], type=pa.string()),
        # pa.array(columns["payload_binary"], type=pa.binary()),
        pa.array(columns["amount_decimal"], type=pa.decimal128(18, 4)),
        pa.array(columns["order_date"], type=pa.date32()),
        pa.array(columns["created_ts"], type=pa.timestamp("ms")),
    ]

    table = pa.Table.from_arrays(arrays, schema=schema)
    pq.write_table(table, path, compression="snappy")  # common default
    print(f"Parquet written: {path}")


def write_avro(columns: dict, path: str):
    """
    Write Avro with logical types for decimal/date/timestamp.
    For date/timestamp, we explicitly convert to the Avro primitive representations:
      - date: int (days since epoch)
      - timestamp-millis: long (milliseconds since epoch)
    Decimal is provided as Decimal and fastavro will encode as bytes.
    """

    avro_schema = {
        "type": "record",
        "name": "TestData",
        "namespace": "com.example",
        "fields": [
            {"name": "id_int32", "type": "int"},
            {"name": "big_int64", "type": "long"},
            {"name": "flag_bool", "type": "boolean"},
            {"name": "ratio_float", "type": "float"},
            {"name": "score_double", "type": "double"},
            {"name": "name_string", "type": "string"},
            # {"name": "payload_binary", "type": "bytes"},
            {
                "name": "amount_decimal",
                "type": {"type": "bytes", "logicalType": "decimal", "precision": 18, "scale": 4},
            },
            {"name": "order_date", "type": {"type": "int", "logicalType": "date"}},
            {"name": "created_ts", "type": {"type": "long", "logicalType": "timestamp-millis"}},
        ],
    }

    # Epoch anchors
    epoch_date = date(1970, 1, 1)
    epoch_dt = datetime(1970, 1, 1, 0, 0, 0)

    records = []
    for i in range(len(columns["id_int32"])):
        d = columns["order_date"][i]
        dt = columns["created_ts"][i]

        # Convert to Avro primitives for logical types
        days_since_epoch = (d - epoch_date).days
        millis_since_epoch = int((dt - epoch_dt).total_seconds() * 1000)

        records.append(
            {
                "id_int32": int(columns["id_int32"][i]),
                "big_int64": int(columns["big_int64"][i]),
                "flag_bool": bool(columns["flag_bool"][i]),
                "ratio_float": float(columns["ratio_float"][i]),
                "score_double": float(columns["score_double"][i]),
                "name_string": columns["name_string"][i],
                # "payload_binary": columns["payload_binary"][i],  # bytes
                "amount_decimal": columns["amount_decimal"][i],  # Decimal
                "order_date": days_since_epoch,  # int
                "created_ts": millis_since_epoch,  # long
            }
        )

    with open(path, "wb") as f:
        avro_writer(f, avro_schema, records)
    print(f"Avro written: {path}")


def main():
    out_dir = "."
    os.makedirs(out_dir, exist_ok=True)

    # Generate
    data = generate_data(n_rows=20, seed=42)

    # Write CSV
    write_csv(data["df"], os.path.join(out_dir, "testdata.csv"))

    # Write Parquet
    write_parquet(data, os.path.join(out_dir, "testdata.parquet"))

    # Write Avro
    write_avro(data, os.path.join(out_dir, "testdata.avro"))


if __name__ == "__main__":
    main()
