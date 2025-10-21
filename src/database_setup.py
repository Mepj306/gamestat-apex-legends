import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
APEX_DB = os.environ.get("Apex_DB_URL")

Base = declarative_base()

class StatEntry(Base):
    
    __tablename__ = 'stat_entries'

    id = Column(Integer, primary_key=True)

    player_name = Column(String, nullable = False)
    platform = Column(String, nullable = False)

    total_kills = Column(Integer, default = 0)
    damage_done = Column(String, nullable = False)
    level = Column(Integer, default = 0)

    recorded_at = Column(Integer, default = 0)

    def __repr__(self):
        return f"StatEntry(id = {self.id}, name =' {self.player_name}', kills = {self.total_kills}, recorded_at = '{self.recorded_at.strftime('%Y-%m-%d %H:%M')}')"
    
def init_db(connection_string = APEX_DB):
    try:
        engine = create_engine(connection_string, echo = True)

        Base.metadata.create_all(engine)
        print("Database connection succesfull and tables created!")
        return engine
    except Exception as e:
        print("Error connecting to database or creating tables: {e}")
        return None

if __name__ == '__main__':
    db_engine = init_db()
    if db_engine:
        print(f"Engin created succesffully: {db_engine}")
