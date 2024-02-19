
class AppSettings:
    def __init__(self, settings_file_path):
        self.file = settings_file_path  # Initialize instance variable with string value

    def get_values_for_keys(self, keys):
        # Initialize a dictionary to hold the keys and their found values
        found_values = {}
        with open(self.file, "r") as file:
            lines = file.readlines()
            for line in lines:
                # Split the line into key and value based on the '=' character
                parts = line.strip().split("=")
                # If the line is correctly formatted and the key is of interest,
                # update the dictionary
                if len(parts) == 2 and parts[0].strip() in keys:
                    found_values[parts[0].strip()] = parts[1].strip()
        
        # Prepare the result list, filling in None for keys not found,
        # preserving the order of keys as they were submitted
        values_in_order = [found_values.get(key, None) for key in keys]
        
        return values_in_order
    
#tests
# settings = AppSettings("doorSettings")
# settings_values = settings.get_values_for_keys(["relay pin", "closed door sensor pin", "open door sensor pin", "warn when open for minutes", "warn when moving for secs"])
# print(settings_values)
