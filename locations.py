import json
import os

locations_file = "locations.json" 

def load_locations():
    if not os.path.exists(locations_file):
        return {}
    with open(locations_file, "r") as file:
        return json.load(file)
    
def save_locations(name, coordinates):
    locations = load_locations()
    locations[name] = coordinates

    with open(locations_file, "w") as file:
        json.dump(locations, file, indent=2)
    print(f"saved '{name} at {coordinates}")

def get_locations(name):
    locations = load_locations()

    return locations.get(name, None)


def add_location():
    print("\nAdd named locations for Orion to remember")
    print("type 'list' to see saved locations and 'quit' to exit\n")

    while True:
        name = input("Location name: ").strip().lower()

        if name == "quit":
            break
        
        if name == "list":
            locations = load_locations()

            if not locations:
                print("No locations saved")
            else:
                for i, coords in locations.items():
                    print(f"{n}: {coords}")
            continue
        
        if not name:
            continue

        try:
            x = float(input(f" x coord in cm: "))
            y = float(input(f" y coord in cm: "))
            
            save_locations(name,[x, y])
        except ValueError:
            print("Invalid coords")


if __name__ == "__main__":
    add_location()

