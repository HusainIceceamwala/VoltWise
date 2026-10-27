from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, Text, select, insert, update
)
from dotenv import load_dotenv
import os
import json
import datetime

# Load .env if present
load_dotenv()

# Priority 1: explicit DATABASE_URL env var
DATABASE_URL = os.environ.get("DATABASE_URL")

# Priority 2: build from MySQL env vars if provided
if not DATABASE_URL and os.environ.get("MYSQL_HOST"):
    user = os.environ.get("MYSQL_USER", "root")
    password = os.environ.get("MYSQL_PASSWORD", "")
    host = os.environ.get("MYSQL_HOST", "localhost")
    port = os.environ.get("MYSQL_PORT", "3306")
    dbname = os.environ.get("MYSQL_DB", "wattwise")
    DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"

# Fallback: local SQLite
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///wattwise.db"

engine = create_engine(DATABASE_URL, future=True)
metadata = MetaData()

bills = Table(
    "bills",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("consumer_number", String(255)),
    Column("bill_date", String(255)),
    Column("units", String(255)),
    Column("total_amount", String(255)),
    Column("ai_analysis", Text),
)

# Samples table for labeled training / corrected examples
samples = Table(
    "samples",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("filename", String(512)),
    Column("raw_text", Text),
    Column("parsed_json", Text),
    Column("corrected_json", Text),
    Column("tags", String(255)),
    Column("created_at", String(64)),
)


def create_database():
    """Create tables if they do not exist."""
    metadata.create_all(engine)


def save_bill(data, analysis):
    """Insert a bill and return the new bill id."""
    stmt = insert(bills).values(
        consumer_number=data.get("Consumer Number", ""),
        bill_date=data.get("Bill Date", ""),
        units=data.get("Units", ""),
        total_amount=data.get("Amount", ""),
        ai_analysis=analysis,
    )
    with engine.begin() as conn:
        result = conn.execute(stmt)
        pk = result.inserted_primary_key
        return int(pk[0]) if pk else None


def update_bill_analysis(bill_id, analysis):
    """Update the AI analysis text for a saved bill."""
    stmt = update(bills).where(bills.c.id == bill_id).values(ai_analysis=analysis)
    with engine.begin() as conn:
        conn.execute(stmt)


def get_all_bills():
    """Return all bills as a list of tuples matching the old format.

    (id, consumer_number, bill_date, units, total_amount, ai_analysis)
    """
    stmt = select(bills).order_by(bills.c.id)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        rows = []
        for r in result:
            rows.append((r.id, r.consumer_number, r.bill_date, r.units, r.total_amount, r.ai_analysis))
        return rows


def save_sample(filename, raw_text, parsed, corrected=None, tags=None):
    """Persist a labeled sample for later export or training."""
    corrected = corrected or {}
    parsed_json = json.dumps(parsed or {})
    corrected_json = json.dumps(corrected or {})
    tags = tags or ""
    created_at = datetime.datetime.utcnow().isoformat()
    stmt = insert(samples).values(
        filename=filename,
        raw_text=raw_text,
        parsed_json=parsed_json,
        corrected_json=corrected_json,
        tags=tags,
        created_at=created_at,
    )
    with engine.begin() as conn:
        result = conn.execute(stmt)
        pk = result.inserted_primary_key
        return int(pk[0]) if pk else None


def get_all_samples():
    stmt = select(samples).order_by(samples.c.id)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        rows = []
        for r in result:
            rows.append((r.id, r.filename, r.raw_text, r.parsed_json, r.corrected_json, r.tags, r.created_at))
        return rows


def export_samples_csv():
    """Return CSV text of all samples for download or external labeling."""
    import io, csv
    rows = get_all_samples()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "filename", "raw_text", "parsed_json", "corrected_json", "tags", "created_at"])
    for r in rows:
        writer.writerow(r)
    return output.getvalue()
