from osc_site.settings import *


def get_secret(secrets, section, option):
    try:
        return secrets.get(section, option)
    except Exception:
        return None
