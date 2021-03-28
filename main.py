import logging
from loader import config_loader
from loader import paste_id_updater

root = logging.getLogger()
root.setLevel(logging.INFO)

cc_config = config_loader.config("config/config.toml")
secrets_config = config_loader.config("config/secrets.toml")

paste = paste_id_updater.create_paste(cc_config, secrets_config)

readme_text = ""
with open("README.md", "r") as readme_file:
    for line in readme_file:
        if "pastebin run" in line:
            line = f"pastebin run {paste}\n"
        readme_text += line

with open("README.md", "w") as readme_file:
    readme_file.write(readme_text)
