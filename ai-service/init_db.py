"""
Database Initialization Script (Raw SQLite3 for Python 3.14 Compatibility)
Creates tables and seeds synthetic data for Turbo Sprint.
"""
import sqlite3
import json
import uuid
import os
from datetime import datetime
from services.data_bootstrap import DataBootstrapService

DB_FILE = "novadb.sqlite"

def init_db():
    print(f"Initializing database: {DB_FILE}")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Create Tables (DDL)
    print("Creating tables...")
    
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS founder_profiles (
        id TEXT PRIMARY KEY,
        skills JSON,
        risk_appetite INTEGER,
        financial_runway INTEGER,
        thesis_vector JSON,
        technical_feasibility_override BOOLEAN,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS idea_dna (
        id TEXT PRIMARY KEY,
        founder_id TEXT,
        name TEXT,
        tagline TEXT,
        description TEXT,
        problem_statement TEXT,
        target_customer TEXT,
        stage TEXT,
        conviction_score INTEGER,
        origin_lens TEXT,
        market_size_score INTEGER,
        tech_feasibility_score INTEGER,
        unit_economics_score INTEGER,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY(founder_id) REFERENCES founder_profiles(id)
    );

    CREATE TABLE IF NOT EXISTS conviction_snapshots (
        id TEXT PRIMARY KEY,
        idea_id TEXT,
        total_score INTEGER,
        market_score INTEGER,
        timing_score INTEGER,
        execution_score INTEGER,
        change_reason TEXT,
        delta INTEGER,
        recorded_at TIMESTAMP,
        FOREIGN KEY(idea_id) REFERENCES idea_dna(id)
    );

    CREATE TABLE IF NOT EXISTS market_signals (
        id TEXT PRIMARY KEY,
        sector TEXT,
        region TEXT,
        data JSON,
        last_updated TIMESTAMP,
        expires_at TIMESTAMP
    );
    """)
    
    print("Tables created.")

    # 2. Seed Data
    try:
        print("Seeding synthetic data...")
        history = DataBootstrapService.generate_synthetic_history(count=50)
        
        count = 0
        for item in history:
            # Upsert MarketSignal
            signal_id = f"history:{item['id']}"
            sector = item['sector']
            region = "Global"
            data_json = json.dumps(item)
            now = datetime.utcnow().isoformat()
            
            cursor.execute("""
                INSERT OR REPLACE INTO market_signals (id, sector, region, data, last_updated, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (signal_id, sector, region, data_json, now, None))
            count += 1
            
        # Seed Sector Benchmarks
        unique_sectors = set(item['sector'] for item in history)
        for sector in unique_sectors:
            benchmarks = DataBootstrapService.get_sector_benchmarks(sector)
            signal_id = f"sector:{sector.lower()}:global"
            data_json = json.dumps(benchmarks)
            now = datetime.utcnow().isoformat()
            
            cursor.execute("""
                INSERT OR REPLACE INTO market_signals (id, sector, region, data, last_updated, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (signal_id, sector, "Global", data_json, now, None))
        
        conn.commit()
        print(f"Seeded {count} history records and {len(unique_sectors)} sector benchmarks.")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
