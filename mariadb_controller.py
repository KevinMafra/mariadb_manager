import subprocess, secrets, shutil, threading

from config import root_path
from zipfile import ZipFile

class MariaDBController:

    def __init__(self):
        self.hex_key = None
        self.passwd = None

        self.status = None

        self.root_path = root_path / "mariadb"
        self.installer_path = root_path / "assets" / "mariadb.zip"
        self.dataset_path = self.root_path / "data"
        self.hex_key_path = self.root_path / "hex_key.txt"
        self.passwd_key_path = self.root_path / "passwd_key.txt"


    def mariadb_terminal_output(self):
        for line in self.process.stdout:
            yield line


    def check_status(self):
        self.process = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                """
                $mariadbd = Get-Process -Name mariadbd -ErrorAction SilentlyContinue

                if ($mariadbd) {
                    $connection = Get-NetTCPConnection -OwningProcess $mariadbd.Id -ErrorAction SilentlyContinue
                    if ($connection) {
                        Write-Output 'online'
                    }
                    else {
                        Write-Output 'offline'
                    }
                }
                else {
                    Write-Output 'offline'
                }
                """
            ],
            capture_output=True,
            text=True
        )
        self.status = self.process.stdout.strip()
        pass


    def mariadb_init(self):
        if not (self.root_path).exists():
            with ZipFile(self.installer_path, "r") as file:
                file.extractall(root_path)
        if not (self.dataset_path).exists():
            executable = self.root_path / "bin" / "mysql_install_db.exe"

            self.hex_key = secrets.token_hex(8)
            self.passwd = self.hex_key
            with open(self.hex_key_path, "w") as file:
                file.write(self.hex_key)
            with open(self.passwd_key_path, "w") as file:
                file.write(self.passwd)

            self.process = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-Command",
                    f"& '{executable}' -p'{self.hex_key}'"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1
            )

        with open(self.hex_key_path, "r") as file:
            self.hex_key = file.read()
        with open(self.passwd_key_path, "r") as file:
            self.passwd = file.read()
        pass


    def mariadb_start(self):
        executable = self.root_path / "bin" / "mariadbd.exe"
        
        self.process = subprocess.Popen(
            [
                str(executable),
                "--console"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1
        )
        pass


    def mariadb_shutdown(self, password=None):
        executable = self.root_path / "bin" / "mariadb-admin.exe"

        if (self.hex_key == self.passwd):
            self.process = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-Command",
                    f"& '{executable}' -u root -p'{self.passwd}' shutdown"
                ]
            )
        elif (self.passwd == password):
            self.process = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-Command",
                    f"& '{executable}' -u root -p'{password}' shutdown"
                ]
            )
        pass


    def mariadb_check_for_update(self, password=None):
        executable = self.root_path / "bin" / "mysql_upgrade.exe"

        if (self.hex_key == self.passwd):
            self.process = subprocess.Popen(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-Command",
                    f"& '{executable}' -u root -p'{self.passwd}'"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1
            )
        elif (self.passwd == password):
            self.process = subprocess.Popen(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-Command",
                    f"& '{executable}' -u root -p'{password}'"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1
            )
        pass


    def mariadb_factory_reset(self, confirmation):
        if (confirmation == "DELETE"):
            if (self.dataset_path).exists():
                shutil.rmtree(self.dataset_path)
                self.hex_key_path.unlink(missing_ok=True)
                self.passwd_key_path.unlink(missing_ok=True)
        pass