import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "reviews.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            case_title TEXT NOT NULL,
            status TEXT NOT NULL, -- 'Accepted', 'Edited', 'Rejected'
            ai_response TEXT NOT NULL, -- JSON string of LLM diagnosis
            corrected_notes TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    
    # Check if empty, and pre-seed with mock reviews to showcase charts instantly
    cursor.execute("SELECT COUNT(*) FROM reviews")
    count = cursor.fetchone()[0]
    if count == 0:
        # Pre-seed data
        seed_data = [
            (
                "Case #12", 
                "Guest Wi-Fi", 
                "Accepted", 
                json.dumps({
                    "root_cause": "Interface GigabitEthernet0/1 is administratively down (shutdown).",
                    "osi_layer": "Layer 1",
                    "confidence": "high",
                    "evidence": "shutdown",
                    "next_command": "show ip interface brief",
                    "fix_steps": ["interface GigabitEthernet0/1", "no shutdown"]
                }),
                "Confirmed. Simple admin down issue. AI identified it correctly.",
                "2026-08-30 10:15:30"
            ),
            (
                "Case #15", 
                "WAN Link Host Mask", 
                "Edited", 
                json.dumps({
                    "root_cause": "A /32 host mask is misconfigured on GigabitEthernet0/0.",
                    "osi_layer": "Layer 3",
                    "confidence": "low",
                    "evidence": "255.255.255.255",
                    "next_command": "show ip route",
                    "fix_steps": ["interface GigabitEthernet0/0", "ip address 203.0.113.5 255.255.255.255"]
                }),
                "AI suggested the wrong fix (keeping /32). Changed mask to /30 (255.255.255.252) so it can route to ISP gateway.",
                "2026-08-30 11:20:45"
            ),
            (
                "Case #3", 
                "Core Switch Trunking", 
                "Accepted", 
                json.dumps({
                    "root_cause": "VLAN 10 is missing from the switchport trunk allowed list.",
                    "osi_layer": "Layer 2",
                    "confidence": "high",
                    "evidence": "switchport trunk allowed vlan 1,2,5,20",
                    "next_command": "show interfaces trunk",
                    "fix_steps": ["interface GigabitEthernet1/0/1", "switchport trunk allowed vlan add 10"]
                }),
                "AI response was 100% correct.",
                "2026-08-30 14:05:00"
            ),
            (
                "Case #12", 
                "Guest Wi-Fi", 
                "Rejected", 
                json.dumps({
                    "root_cause": "No issues detected on interface.",
                    "osi_layer": "Layer 3",
                    "confidence": "medium",
                    "evidence": "None",
                    "next_command": "ping 192.168.100.1",
                    "fix_steps": []
                }),
                "AI completely missed that the interface is shutdown. Marked as shutdown under GigabitEthernet0/1.",
                "2026-08-30 15:45:22"
            )
        ]
        cursor.executemany("""
            INSERT INTO reviews (case_id, case_title, status, ai_response, corrected_notes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, seed_data)
        conn.commit()
    conn.close()

def save_review(case_id, case_title, status, ai_response_str, corrected_notes):
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO reviews (case_id, case_title, status, ai_response, corrected_notes, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (case_id, case_title, status, ai_response_str, corrected_notes, timestamp))
    conn.commit()
    conn.close()

def get_all_reviews():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reviews ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    reviews = [dict(row) for row in rows]
    conn.close()
    return reviews

def get_metrics():
    reviews = get_all_reviews()
    total = len(reviews)
    if total == 0:
        return {"total": 0, "accepted": 0, "edited": 0, "rejected": 0, "agreement_rate": 0.0}
    
    accepted = sum(1 for r in reviews if r["status"] == "Accepted")
    edited = sum(1 for r in reviews if r["status"] == "Edited")
    rejected = sum(1 for r in reviews if r["status"] == "Rejected")
    
    # Agreement rate is percentage of Accepted reviews
    agreement_rate = (accepted / total) * 100.0
    
    return {
        "total": total,
        "accepted": accepted,
        "edited": edited,
        "rejected": rejected,
        "agreement_rate": agreement_rate
    }

def clear_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reviews")
    conn.commit()
    conn.close()
