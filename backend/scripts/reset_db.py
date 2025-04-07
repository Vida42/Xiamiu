import os
import sys
import argparse
from pathlib import Path
import importlib


def reset_database(reload_data=False, dump_data=False):
    print("Starting database management process...")
    
    # Get the path to backend directory
    backend_dir = Path(__file__).parent.parent
    
    # If dump_before_reset is True, dump the current database state
    if dump_data:
        print("\n==== STEP 1: Dumping current database state ====")
        try:
            # Import from the same directory
            from .dump_data import dump_data
            if dump_data():
                print("Database state successfully dumped.")
            else:
                print("Failed to dump database state.")
                if input("Continue with reset? (y/n): ").lower() != 'y':
                    return
        except Exception as e:
            print(f"Error dumping database: {e}")
            if input("Continue with reset? (y/n): ").lower() != 'y':
                return

    # Reset the database
    print("\n==== STEP 2: Resetting database ====")
    try:
        from .remove_database import remove_database
        remove_database()
    except Exception as e:
        print(f"Error resetting database: {e}")
        return

    # If reload_data flag is set, run the load_data script
    if reload_data:
        print("\n==== STEP 3: Reloading data from seed file ====")
        try:
            # Import from the same directory
            from .load_data import load_data
            load_data()
            print("Data loaded successfully.")
        except Exception as e:
            print(f"Error loading data: {e}")
            return
    
    print("\nDatabase management process completed successfully.")
    if not reload_data:
        print("Note: To load data, use the --reload flag")


def main():
    parser = argparse.ArgumentParser(description='Manage the Xiamiu database')
    parser.add_argument('--reload', action='store_true', 
                      help='Reload data after resetting')
    parser.add_argument('--dump', action='store_true',
                      help='Dump current database state before resetting')
    
    args = parser.parse_args()
    
    reset_database(reload_data=args.reload, dump_data=args.dump)


if __name__ == "__main__":
    main()
