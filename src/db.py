import os
import api
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

load_dotenv()
APEX_DB = os.environ.get("DB_URL")
if not APEX_DB:
    raise EnvironmentError("Environment variable not found in .env file")

engine = create_engine(APEX_DB)
Base = declarative_base()

class LegendStat(Base):
    
    __tablename__ = 'legend_stats'

    id = Column(Integer, primary_key=True)
    player_name = Column(String, nullable=False)
    legend_name = Column(String, unique = True, nullable = False)
    kills = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    damage = Column(Integer, default=0)
    recorded_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return (
            f"<LegendStat(name='{self.legend_name}, kills={self.kills}), "
            f"wins={self.wins}, damage={self.damage})>"
        )
    
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def update_or_insert(legend_name, kills, wins, damage):

    session = Session()
    
    try:

        existing_legend = session.query(LegendStat).filter_by(legend_name=legend_name).first()

        if existing_legend:
            print(f"Found {legend_name}, updating stats...")
            existing_legend.kills = kills
            existing_legend.wins = wins
            existing_legend.damage = damage
            existing_legend.recorded_at = datetime.now()
        else:

            print(f"Adding new legend {legend_name}...")
            new_stat = LegendStat(
                player_name="Pagano94",
                legend_name = legend_name,
                kills=kills,
                wins=wins,
                damage=damage
            )
            session.add(new_stat)
        
        session.commit()
        print(f"Data saved for {legend_name}.")

    except Exception as e:
        print(f"Something went wrong: {e}")
        session.rollback()
    
    finally:
        session.close()

def get_legend_stats(data, legend_name):
    
    total_kills = 0
    total_wins = 0
    total_damage = 0

    kill_keys = {'kills', 'specialEvent_kills'}
    win_keys = {'wins', 'specialEvent_wins'}
    damage_keys = {'damage', 'specialEvent_damage'}

    try:

        legend_data_list = data.get('legends', {}).get('all', {}).get(legend_name, {}).get('data', [])

        if not legend_data_list:
            print(f"Warning: No 'data' list found for legend {legend_name}.")
            return 0, 0, 0

        for stat_item in legend_data_list:
            key = stat_item.get('key')
            value = stat_item.get('value', 0)
            
            if key in kill_keys:
                total_kills += value
            elif key in win_keys:
                total_wins += value
            elif key in damage_keys:
                total_damage += value

    except Exception as e:

        print(f"An error occurred while processing legend {legend_name}: {e}")
        return 0, 0, 0

    return int(total_kills), int(total_wins), int(total_damage)

def update_legend_stats_api():
    
    print("--- Starting API Fetch and Database Update ---")
    
    data = api.get_data()
    if data is None:
        print("Update Failed: Could not fetch player data from API.")
        return False
    
    all_legends_data = data.get('legends', {}).get('all', {})
    if not all_legends_data:
        print("Update Failed: No legend data found in API response.")
        return False

    
    for legend_name in all_legends_data:
        
        kills, wins, damage = get_legend_stats(data, legend_name)
        update_or_insert(legend_name, kills, wins, damage)
        
    print("--- Database Update Complete ---")
    return True

def display_legend_stats(legend_name, stat_key):
    session = Session()
    try:
        legend_stat = session.query(LegendStat).filter_by(legend_name=legend_name).first()

        if not legend_stat:
            return f"Error: '{legend_name}' not found in the database. Update database first."
        
        stat_value = getattr(legend_stat, stat_key, None)

        if stat_value is None:
            return f"Error: Stat key '{stat_key}' is invalid or missing for {legend_name}"
        
        recorded_date = legend_stat.recorded_at.strftime('%Y-%m-%d %H:%M')
        return f"{legend_name}'s {stat_key.title()}: {stat_value} (as of {recorded_date})" 
    
    except Exception as e:
        return f"Database Retrieval error: {e}"
    finally: 
        session.close()

def delete_legend_data(legend_name):

    session = Session()
    try:
        legend_to_delete = session.query(LegendStat).filter_by(legend_name=legend_name).first()

        if not legend_to_delete:
             return f"{legend_to_delete}'s data not found."
        
        session.delete(legend_to_delete)
        session.commit()

        return f"{legend_to_delete}'s data has been deleted succesffully."
      
    except Exception as e:
        session.rollback()
        return f"Error deleting legend data: {e}"
    finally:
        session.close()

if __name__ == '__main__':

    print("Running testdb.py standalone...")
    data = api.get_data()
    if data:
     
        test_name = 'Pathfinder' 
        try:
            kills, wins, damage = get_legend_stats(data, test_name)

            print(f"Stats for {test_name}: Kills: {kills}, Wins: {wins}, Damage: {damage}")

            if test_name:
                update_or_insert(test_name, kills, wins, damage)
            else:
                print("Error: No legend name was provided for standalone test.")

        except Exception as e:
            print(f"An unexpected error occurred during standalone run: {e}")
    else:
        print("API data could not be fetched for standalone test.")