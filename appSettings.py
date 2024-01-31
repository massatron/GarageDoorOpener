
class AppSettings:
    def __init__(self, settings_file_path):
        self.file = settings_file_path  # Initialize instance variable with string value

    def get_values_for_keys(self, keys):
        values = []
        with open(self.file, "r") as file:
            lines = file.readlines()
            for line in lines:
                # Split the line into key and value based on the '=' character
                parts = line.strip().split("=")
                # Check if the key is in the given array of keys
                if len(parts) == 2 and parts[0].strip() in keys:
                    values.append(parts[1].strip())
        return values
