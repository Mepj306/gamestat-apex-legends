import os
import tkinter as tk
from tkinter import ttk
from threading import Thread

# Import SQLAlchemy components
from sqlalchemy import create_engine, Column, Integer, String, DateTime, UniqueConstraint, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# --- Database Model (Must match data_ingest.py) ---
# Note: Defining the Base and Model here is necessary for querying data.
Base = declarative_base()

class LegendStat(Base):
    __tablename__ = 'legend_stats'
    id = Column(Integer, primary_key=True)
    player_name = Column(String, nullable=False)
    legend_name = Column(String, nullable=False)
    kills = Column(Integer, default=0, nullable=False)
    wins = Column(Integer, default=0, nullable=False)
    damage = Column(Integer, default=0, nullable=False)
    recorded_at = Column(DateTime)
    __table_args__ = (UniqueConstraint('player_name', 'legend_name', name='_player_legend_uc'),)
    
# --- Application Constants ---
load_dotenv()
DB_URL = os.getenv("DB_URL") 
PLAYER_NAME = "ItzPagano94" # Must match the player in data_ingest.py

# Legend and Stat selection lists
LEGENDS = [
    "Pathfinder", "Wraith", "Bloodhound", "Gibraltar", "Lifeline", "Bangalore",
    "Caustic", "Mirage", "Octane", "Wattson", "Crypto", "Revenant", "Loba", 
    "Rampart", "Horizon", "Fuse", "Valkyrie", "Seer", "Ash", "Mad Maggie",
    "Newcastle", "Vantage", "Catalyst", "Ballistic", "Conduit", "Alter"
]

# MAP STAT DISPLAY NAME TO DB COLUMN NAME
STAT_MAPPING = {
    "Kills": "kills",
    "Wins": "wins",
    "Damage": "damage",
}
STATS = list(STAT_MAPPING.keys())


class ApexStatsGUI:
    def __init__(self, master):
        self.master = master
        master.title("Apex Legends Stat Lookup (Cached)")
        master.geometry("400x300")
        
        # 1. Database Setup
        self.db_engine = None
        self.Session = None
        self._setup_db_connection()

        # State variables for dropdown selections
        self.selected_legend = tk.StringVar(master)
        self.selected_stat = tk.StringVar(master)
        
        # Set default values
        self.selected_legend.set(LEGENDS[0])
        self.selected_stat.set(STATS[0])

        # Status/Result Label
        self.status_label = ttk.Label(master, text="Select a legend and a stat to search.")
        self.status_label.pack(pady=20, padx=10)

        # Legend Dropdown
        ttk.Label(master, text="Select Legend:").pack()
        legend_menu = ttk.OptionMenu(master, self.selected_legend, LEGENDS[0], *LEGENDS)
        legend_menu.pack(pady=5)

        # Stat Dropdown
        ttk.Label(master, text="Select Stat:").pack()
        stat_menu = ttk.OptionMenu(master, self.selected_stat, STATS[0], *STATS)
        stat_menu.pack(pady=5)

        # Lookup Button
        self.lookup_button = ttk.Button(master, text="Lookup Stat", command=self._start_fetch_thread)
        self.lookup_button.pack(pady=20)
        
        # Ensure database is connected before allowing use
        if not self.db_engine:
            self.status_label.config(text="ERROR: Database connection failed. Check DB_URL.")
            self.lookup_button.config(state=tk.DISABLED)


    def _setup_db_connection(self):
        """Initializes the database connection."""
        if not DB_URL:
            print("Error: DB_URL environment variable is not set.")
            return

        try:
            self.db_engine = create_engine(DB_URL, echo=False)
            # Optional: Test the connection
            with self.db_engine.connect() as connection:
                 # Execute a dummy query to verify connection is active
                connection.execute(text("SELECT 1"))
            
            self.Session = sessionmaker(bind=self.db_engine)
            print("Database connection successful.")
            
            # Ensure the table structure exists
            Base.metadata.create_all(self.db_engine)

        except Exception as e:
            print(f"Error establishing DB connection: {e}")
            self.db_engine = None
            self.Session = None

    def _start_fetch_thread(self):
        """Starts the data fetch process in a separate thread."""
        self.lookup_button.config(state=tk.DISABLED)
        self.status_label.config(text="Querying database...")
        
        # Use Threading to prevent GUI freeze
        Thread(target=self._fetch_and_display_stats).start()

    def _fetch_and_display_stats(self):
        """
        Fetches the requested stat from the PostgreSQL database.
        This runs in a separate thread.
        """
        chosen_legend = self.selected_legend.get()
        chosen_stat_display = self.selected_stat.get()
        # Map the display name to the actual database column name
        chosen_stat_column = STAT_MAPPING[chosen_stat_display] 

        session = self.Session()
        data_found = None
        
        try:
            # Construct the query to retrieve the specific column value
            # Note: We use getattr to dynamically access the attribute (column) based on the string name
            result = session.query(LegendStat).filter(
                LegendStat.player_name == PLAYER_NAME,
                LegendStat.legend_name == chosen_legend
            ).one_or_none()

            if result:
                # Dynamically retrieve the stat value from the returned ORM object
                data_found = getattr(result, chosen_stat_column)
                
            
            if data_found is not None:
                message = (
                    f"[{chosen_legend}] {chosen_stat_display}: {data_found}\n"
                    f"(Cached at: {result.recorded_at.strftime('%Y-%m-%d %H:%M:%S')})"
                )
            else:
                message = (
                    f"Stat '{chosen_stat_display}' for {chosen_legend} not found.\n"
                    "Data may be missing or has not been ingested yet."
                )

        except Exception as e:
            message = f"Database Error: {e}"
        finally:
            session.close()

        # Update GUI elements back on the main thread
        self.master.after(0, lambda: self._update_gui(message))

    def _update_gui(self, message):
        """Updates GUI elements after the thread completes."""
        self.status_label.config(text=message)
        self.lookup_button.config(state=tk.NORMAL)


if __name__ == '__main__':
    root = tk.Tk()
    app = ApexStatsGUI(root)
    root.mainloop()
