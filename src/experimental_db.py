import os
import requests
import time
from sqlalchemy import create_engine, Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
APEX_DB = os.environ.get("DB_URL")
API_KEY = os.getenv("API_KEY")
URL = "https://api.mozambiquehe.re/bridge?"

headers = {
       "Authorization": API_KEY
       
}

params = {
    "platform": "PC",                 
    "player": "ItzPagano94"  
}
STAT_MAPPING = {
    "specialEvent_kills": "kills",
    "specialEvent_wins": "wins",
    "specialEvent_damage": "damage",
}
stats_to_cache = list(STAT_MAPPING.keys())

Base = declarative_base()

class StatEntry(Base):
    
    __tablename__ = 'stat_entries'

    id = Column(Integer, primary_key=True)

    player_name = Column(String, nullable = False)
    platform = Column(String, nullable = False)

    total_kills = Column(Integer, default = 0)
    damage_done = Column(String, nullable = False)
    level = Column(Integer, default = 0)

    recorded_at = Column(DateTime, default = datetime.now)

    def __repr__(self):
        return f"StatEntry(id = {self.id}, name =' {self.player_name}', kills = {self.total_kills}, recorded_at = '{self.recorded_at.strftime('%Y-%m-%d %H:%M')}')"

class LegendStats(Base):
    __tablename__ = 'legend_stats'

    id = Column(Integer, primary_key=True)
    player_name = Column(String, nullable=False)
    legend_name = Column(String, nullable=False)
    kills = Column(Integer, default=0,nullable=False)
    wins = Column(Integer, default=0, nullable=False)
    damage = Column(Integer, default=0, nullable=False)
    recorded_at = Column(DateTime, default = datetime.now)
    __table_args__ = (
        UniqueConstraint('player_name', 'legend_name', name='_player_legend_uc'),
    )

    def __repr__(self):
        return (f"LegendStat(player='{self.player_name}', legend='{self.legend_name}', "
                f"Kills={self.kills}, Wins={self.wins})")

    
def init_db(conn = APEX_DB):
    if not conn:
        print("Error: Environment variable is not set.")
        return None
    
    try:
        engine = create_engine(conn, echo = True)

        Base.metadata.create_all(engine)
        print("Database connection succesfull and tables created!")
        return engine
    except Exception as e:
        print("Error connecting to database or creating tables: {e}")
        return None

def fetch_player_stats(URL, headers, params):
    try: 
        response = requests.get(URL, headers=headers, params=params)
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")
        return response.json() 
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return None
    
def ingest_data(db_engine):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting data ingestion...")

    data = fetch_player_stats(URL, headers, params)

    if not data or 'legends' not in data:
        print("Failed to retrieve valid data from API.")
        return
    
    Session = sessionmaker(bind=db_engine)
    session = Session()

    all_legends = data['legends']['all']
    player_name = params['player']

    stats_processed = 0

    try:
        for legend_name, legend_data in all_legends.items():

            collected_stats = {
                "kills": 0,
                "wins": 0,
                "damage": 0
            }

            for stat_entry in legend_data.get('data', []):
                api_stat_name = stat_entry.get('key')

                if api_stat_name in stats_to_cache:
                    db_column_name = STAT_MAPPING[api_stat_name]
                    stat_value = stat_entry.get('value', 0)
                    collected_stats[db_column_name] = stat_value

            record = session.query(LegendStats).filter_by(
                player_name=player_name,
                legend_name=legend_name,
            ).one_or_none()

            if record:
                record.kills = collected_stats['kills']
                record.wins = collected_stats['wins']
                record.damage = collected_stats['damage']
                record.recorded_at = datetime.now()
            else:
                new_stat = LegendStats(
                    player_name=player_name,
                    legend_name=legend_name,
                    kills=collected_stats["kills"],
                    wins=collected_stats["wins"],
                    damage=collected_stats["damage"],

                )
                session.add(new_stat)
            stats_processed += 1
        session.commit()
        print(f"Successfully committed {stats_processed} legend records to database. ")    
    except Exception as e:
        session.rollback()
        print(f"An error occurred during database commit: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    db_engine = init_db()
    if db_engine:
        ingest_data(db_engine)
