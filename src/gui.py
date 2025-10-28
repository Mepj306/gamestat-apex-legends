import tkinter as tk
from tkinter import ttk
import db

PLAYER_NAME = "Pagano94"

LEGENDS = [
    "Pathfinder", "Wraith", "Bloodhound", "Gibraltar", "Lifeline", "Bangalore",
    "Caustic", "Mirage", "Octane", "Wattson", "Crypto", "Revenant", "Loba", 
    "Rampart", "Horizon", "Fuse", "Valkyrie", "Seer", "Ash", "Mad Maggie",
    "Newcastle", "Vantage", "Catalyst", "Ballistic", "Conduit", "Alter"
]

STAT_MAPPING = {
    "Kills": "kills",
    "Wins": "wins",
    "Damage": "damage",
}
STATS = list(STAT_MAPPING.keys())


root = tk.Tk()
root.geometry("400x350")
root.title("Apex Legends Stat Tracker")

BACKGROUND_COLOR = "#303030" 
BUTTON_COLOR = "#404040"    
BUTTON_ACTIVE_COLOR = "#505050"
TEXT_COLOR = "white"

root.config(bg=BACKGROUND_COLOR)

style = ttk.Style()

style.theme_use('clam')

style.configure('TLabel', background=BACKGROUND_COLOR, foreground=TEXT_COLOR)
style.configure('TButton', background=BUTTON_COLOR, foreground=TEXT_COLOR, relief='raised')
style.map('TButton', background=[('active', BUTTON_ACTIVE_COLOR)])


style.configure('TMenubutton', 
    background=BUTTON_COLOR, 
    foreground=TEXT_COLOR, 
    relief='flat', 
    border=0,
)

style.map('TMenubutton', background=[('active', BUTTON_ACTIVE_COLOR)])


status_label = ttk.Label(
    root,
    text=f"Hello {PLAYER_NAME}. Select a legend and a stat to search.",
    background='#1e1e1e',
    foreground='yellow',
    anchor='w',
    relief='sunken'
)

status_label.pack(side='bottom', fill='x', ipady=5)

selected_legend = tk.StringVar(root)
selected_stat = tk.StringVar(root)

legend_select_label= ttk.Label(root, text="Choose Legend")
legend_select_label.pack(pady=5)
legend_select_menu = ttk.OptionMenu(root, selected_legend, LEGENDS[0], *LEGENDS)
legend_select_menu.pack(pady=5)

stat_select_label= ttk.Label(root, text="Choose Stat")
stat_select_label.pack(pady=5)
stat_select_menu = ttk.OptionMenu(root, selected_stat, STATS[0], *STATS)
stat_select_menu.pack(pady=5)

def update_db():

    status_label.config(text="Contacting API and updating databas...")
    root.update()

    success = db.update_legend_stats_api()

    if success:
        status_label.config(text="Database updated successfully!")
    else:
        status_label.config(text="Update FAILED. Check console for API errors.")

update_button = ttk.Button(root, text="Update Database (API CALL)", command=update_db)
update_button.pack(pady=10)

def lookup_stat():
    
    legend = selected_legend.get()
    stat_display_name = selected_stat.get()
    stat_key = STAT_MAPPING.get(stat_display_name)

    if not legend or not stat_key:
        status_label.config(text="Please select a Legend and a Stat.")
        return
    
    status_label.config(text=f"Retrieving {PLAYER_NAME}'s: {legend}'s {stat_display_name} from DB...")
    root.update()

    result = db.display_legend_stats(legend, stat_key)

    status_label.config(text=f"{PLAYER_NAME}'s {result}")

lookup_button = ttk.Button(root, text="Lookup Stat (From DB)", command=lookup_stat)
lookup_button.pack(pady=10)

def delete_stat():

    legend_to_delete = selected_legend.get()

    if not legend_to_delete:
        status_label.config(text="Select a legend to delete it's data.")
        return
    
    status_label.config(text="Deleting {legend_to_delete}'s data.")
    root.update()

    result = db.delete_legend_data(legend_to_delete)

    status_label.config(text=f"{result}")

delete_button =  ttk.Button(root, text="Delete Selected Legend Data", command=delete_stat)
delete_button.pack(pady=10)

root.mainloop()