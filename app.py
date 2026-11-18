import customtkinter as ctk

import threading, time

from mariadb_controller import MariaDBController
from PIL import Image
from config import root_path

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.resizable(False, False)
        self.title("MariaDB Manager v1.0")
        self.iconbitmap(root_path / "assets" / "icon.ico")

        self.controller = MariaDBController()

        self.controller.check_status()
        self.controller.mariadb_init()

        self.image_check_update = ctk.CTkImage(light_image=Image.open(root_path / "assets" / "check_update.png"), size=(24,24))

        self.label_check_status = ctk.CTkLabel(
            self,
            text=f"● {self.controller.status}",
            text_color="#00CC66") if self.controller.status == "online" else ctk.CTkLabel(self, text=f"● {self.controller.status}", text_color="#FF3333")
        self.label_check_status.grid(
            row=0,
            columnspan=2,
            pady=5
        )

        self.button_check_update = ctk.CTkButton(
            self,
            text="Check update",
            border_width=0,
            fg_color="transparent",
            hover_color="#202020",
            image=self.image_check_update,
            command=lambda: self.run_threading(
                self.check_update
            )
        )
        self.button_check_update.grid(
            row=0,
            column=2,
            padx=5,
            pady=5
        )

        self.button_mariadb_start = ctk.CTkButton(
            self,
            text="Start",
            command=lambda: self.run_threading(
                self.start_service
            )
        )
        self.button_mariadb_start.grid(
            row=1,
            column=0,
            padx=5,
            pady=5
        )

        self.button_mariadb_shutdown = ctk.CTkButton(
            self,
            text="Shutdown",
            command=lambda: self.run_threading(
                self.shutdown_service
            )
        )
        self.button_mariadb_shutdown.grid(
            row=1,
            column=1,
            padx=5,
            pady=5
        )

        self.textbox_terminal_output = ctk.CTkTextbox(
            self,
            height=100,
            state="disabled",
            cursor="arrow"
        )
        self.textbox_terminal_output.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="nsew"
        )
        self.textbox_terminal_output_dict = [
            "<Button-2>",
            "<Button-3>",
            "<Double-Button-1>",
            "<B2-Motion>",
            "<B3-Motion>"
        ]
        for event in self.textbox_terminal_output_dict:
            self.textbox_terminal_output.bind(
                event,
                lambda event: "break"
            )

        self.button_mariadb_delete_database = ctk.CTkButton(
            self,
            text="Reset database",
            command=self.delete_database_window
        )
        self.button_mariadb_delete_database.grid(
            row=1,
            column=2,
            padx=5,
            pady=5
        )


    def run_threading(self, command):
        thread = threading.Thread(
            target=command,
            daemon=True
        )
        thread.start()


    def read_terminal(self):
        for line in self.controller.mariadb_terminal_output():
            self.write_terminal(line.rstrip())


    def write_terminal(self, message):
        self.textbox_terminal_output.configure(state="normal")
        self.textbox_terminal_output.insert("end", f"{message}\n")
        self.textbox_terminal_output.see("end")
        self.textbox_terminal_output.configure(state="disabled")


    def update_status(self):

        if self.controller.status == "starting":
            self.label_check_status.configure(text=f"● {self.controller.status}", text_color="#3498DB")
        elif self.controller.status == "online":
            self.label_check_status.configure(text=f"● {self.controller.status}", text_color="#00CC66")
        elif self.controller.status == "stopping":
            self.label_check_status.configure(text=f"● {self.controller.status}", text_color="#E67E22")
        elif self.controller.status == "offline":
            self.label_check_status.configure(text=f"● {self.controller.status}", text_color="#FF3333")
        elif self.controller.status == "updating":
            self.label_check_status.configure(text=f"● {self.controller.status}", text_color="#D9D9D9")
        elif self.controller.status == "reseting":
            self.label_check_status.configure(text=f"● {self.controller.status}", text_color="#D9D9D9")


    def start_service(self):
        if not self.controller.dataset_path.exists():
            self.controller.status = "starting"
            self.after(0, self.update_status)
            self.controller.mariadb_init()
            self.write_terminal("Database created")
            self.controller.mariadb_start()
            self.run_threading(self.read_terminal)

            for _ in range(60):
                self.controller.check_status()
                if self.controller.status == "online":
                    break
            self.after(0, self.update_status)
        else:
            if self.controller.status == "offline":
                self.controller.status = "starting"
                self.after(0, self.update_status)
                self.controller.mariadb_start()
                self.run_threading(self.read_terminal)

                for _ in range(60):
                    self.controller.check_status()
                    if self.controller.status == "online":
                        break
                self.after(0, self.update_status)


    def shutdown_service(self):
        if self.controller.status == "online":
            self.controller.status = "stopping"
            self.after(0, self.update_status)
            self.controller.mariadb_shutdown()

            for _ in range(60):
                self.controller.check_status()
                if self.controller.status == "offline":
                    break
                time.sleep(0.5)
            self.after(0, self.update_status)
        pass


    def check_update(self):
        if self.controller.status == "online" and self.controller.status != "updating":

            self.controller.status = "updating"
            self.after(0, self.update_status)

            self.controller.mariadb_check_for_update()
            self.run_threading(self.read_terminal)

            for _ in range(60):
                if self.controller.process.poll() is not None:
                    break
                time.sleep(0.5)

            self.controller.status = "online"
            self.after(0, self.update_status)
        pass
    

    def delete_database_window(self):
        if hasattr(self, "window") and self.window.winfo_exists():
            self.window.destroy()
            return

        self.window = ctk.CTkFrame(
            self
        )
        self.window.place(
            relx=1,
            rely=0,
            anchor="ne",
            y=self.button_mariadb_delete_database.winfo_y() + self.button_mariadb_delete_database.winfo_height() + 10
        )

        self.label = ctk.CTkLabel(self.window, text="Enter DELETE to confirm", font=("Arial", 10))
        self.label.pack(padx=5, pady=5)

        self.input = ctk.CTkEntry(self.window, placeholder_text="DELETE", font=("Arial", 10), border_width=0, width=0)
        self.input.pack(fill="x", padx=5, pady=5)

        self.window.update()
        self.window.place(
            x=-(self.button_mariadb_delete_database.winfo_width()-5)+(self.window.winfo_width()-5),
        )

        self.input.bind(
            "<Return>",
            lambda event: enter(self.input.get())
        )


        def delete_database(confirmation):
            if self.controller.status == "online":
                self.controller.status = "stopping"
                self.after(0, self.update_status)
                self.controller.mariadb_shutdown()

                for _ in range(60):
                    self.controller.check_status()
                    if self.controller.status == "offline":
                        break
                    time.sleep(0.5)

                self.controller.status = "reseting"
                self.after(0, self.update_status)

                self.controller.mariadb_factory_reset(confirmation)

                self.controller.status = "offline"
                self.after(0, self.update_status)
            elif self.controller.status == "offline":
                self.controller.status = "reseting"
                self.after(0, self.update_status)
                self.controller.mariadb_factory_reset(confirmation)

                for _ in range(60):
                    self.controller.check_status()
                    if self.controller.status == "offline":
                        break
                    time.sleep(0.5)
                self.after(0, self.update_status)
            pass
        

        def enter(confirmation):
            if confirmation == "DELETE":
                self.window.destroy()
                self.run_threading(
                    lambda: (
                        delete_database(confirmation),
                        self.write_terminal("Database reseted")
                    )
                )
            else:
                self.input.delete(0, "end")
                self.input.master.focus_set()


    def on_close(self):
        self.run_threading(self.close_application)


    def close_application(self):
        self.shutdown_service()

        while self.controller.status == "starting":
            self.controller.check_status()
            time.sleep(0.5)
        while self.controller.status == "online":
            self.shutdown_service()
            self.controller.check_status()
            time.sleep(0.5)
        if self.controller.status == "offline":
            self.after(0, self.destroy)

if __name__ == "__main__":
    app = App()
    app.mainloop()