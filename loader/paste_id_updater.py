# This module uploads the latest bootloader.lua into pastebin and updates the config.toml if the paste ID has changed

from pbwrap import Pastebin
import requests
import logging
import getpass


def populate_template(config_data, **kwargs):

    required_args = ["repo_path", "repo_name", "python_url"]

    for arg in required_args:
        if arg not in kwargs.keys():
            logging.error(
                f"Error - '{arg}' has not been passed into the populate_template funtion."
            )
            return False

    replace_map = {arg.upper(): kwargs[arg.lower()] for arg in required_args}

    bootloader_template = ""

    with open(
        config_data["pastebin"]["bootloader_template"], "rb"
    ) as bootloader_template_file:
        bootloader_template = bootloader_template_file.read().decode()

        for key, value in replace_map.items():
            bootloader_template = bootloader_template.replace(f"{{{{{key}}}}}", value)

    return bootloader_template


def create_paste(cc_config, secrets_config):

    config_data = cc_config.get_all()
    secret_data = secrets_config.get_all()

    dev_key = secret_data["pastebin"]["developer_key"]
    username = secret_data["pastebin"]["username"]

    pastebin = Pastebin(dev_key)

    paste = None

    if secret_data["pastebin"]["user_key"] == "":

        while True:
            password = getpass.getpass(f"Password for '{username}' pastebin user: ")

            user_id = pastebin.authenticate(username, password)

            if not "invalid login" in user_id:

                secrets_config.update_field("pastebin", "user_key", user_id)

                logging.info("Created new pastebin user key and updated config file.")

                break

            else:

                logging.warning("Incorrect username or password.")

    else:

        logging.info("Pastebin user key already exists, using it.")

        setattr(pastebin, "api_user_key", secret_data["pastebin"]["user_key"])

        if secret_data["pastebin"]["last_paste"] != "":
            logging.info(
                "Paste already exists, fetching the data to see if we need to update"
            )
            paste = requests.get(
                f"http://pastebin.com/raw/{secret_data['pastebin']['last_paste']}"
            ).text

    lua = populate_template(
        config_data,
        repo_path=config_data["github"]["repo_path"],
        repo_name=config_data["github"]["repo_path"].split('/')[-1],
        python_url=config_data["python"]["interpreter_url"],
    )

    if paste != lua:

        logging.info("Update required - updating.")

        pastebin.delete_user_paste(secret_data["pastebin"]["last_paste"])
        secrets_config.update_field("pastebin", "last_paste", "")

        res = pastebin.create_paste(lua)

        if not ' ' in res:

            paste = res.split("/")[-1]

            secrets_config.update_field("pastebin", "last_paste", paste)

            return paste
        
        else:

            logging.error(res)
            logging.error("Error in pastebin API - writing locally")

            with open('bootloader.lua', 'w') as bootloaderfile:
                bootloaderfile.write(lua)

            return False

    else:

        logging.info("No update required.")

        return secret_data["pastebin"]["last_paste"]
