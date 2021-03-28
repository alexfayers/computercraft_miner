import toml
import logging


# using a class here so that 1 config can be shared between multiple files.


class config:
    def __init__(self, config_path):
        self.config = None

        self.config_path = config_path

        self.load()

    def load(self):
        if self.config == None:
            logging.info("Config loaded.")
            self.config = toml.load(self.config_path)
        else:
            logging.warning("Config already loaded!")

    def dump(self):
        if self.config != None:
            res = None

            with open(self.config_path, "w") as config_file:
                res = toml.dump(self.config, config_file)

            if res:
                logging.info("Config dumped.")
            else:
                logging.error("Config failed to dump!")

    def update_field(self, section, field, new_value):
        self.config[section][field] = new_value

        logging.info(f"Updated '{field}' to '{new_value}' in '{section}' section.")

        self.dump()

    def get_all(self):
        return self.config

    def get_value(self, section, field):
        return self.config[section][field]


if __name__ == "__main__":
    cc_config = config()
