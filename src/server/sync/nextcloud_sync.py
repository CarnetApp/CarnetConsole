#this will make use of nextcloudcmd for syncing
from .settings_manager import SettingsManager


class NextcloudSync():
    def __init__(self):
        self.settingsManager = SettingsManager()

    def startSync(self):
        username = self.settingsManager.get_webdav_username()
        password = self.settingsManager.get_webdav_password()
        server = self.settingsManager.get_webdav_server()
        dest = self.settingsManager.get_webdav_sync_dest()