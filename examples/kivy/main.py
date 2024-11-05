import asyncio

import bleak
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform

# bind bleak's python logger into kivy's logger before importing python module using logging
from kivy.logger import Logger  # isort: skip
import logging  # isort: skip

logging.Logger.manager.root = Logger

if platform == "android":
    from android.permissions import request_permissions, Permission, check_permission

    permissions_list = [
        # Permission.INTERNET,
        Permission.BLUETOOTH_ADMIN,
        Permission.BLUETOOTH_SCAN,
        Permission.BLUETOOTH_CONNECT,
        Permission.ACCESS_COARSE_LOCATION,
        Permission.ACCESS_FINE_LOCATION,
        Permission.ACCESS_BACKGROUND_LOCATION
    ]

    request_permissions(permissions_list)


class ExampleApp(App):
    def __init__(self):
        super().__init__()
        self.label = None
        self.running = False  # Start with scanning not running

    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.scrollview = ScrollView(do_scroll_x=False, scroll_type=["bars", "content"])
        self.label = Label(font_size="10sp")
        self.scrollview.add_widget(self.label)
        layout.add_widget(self.scrollview)

        # Add a button to start the scan
        scan_button = Button(text="Start Scan")
        scan_button.bind(on_press=self.start_scan)
        layout.add_widget(scan_button)

        return layout

    def start_scan(self, instance):
        self.running = True
        asyncio.ensure_future(self.example())  # Run the scan in the background

    def line(self, text, empty=False):
        Logger.info("example:" + text)
        if self.label is None:
            return
        text += "\n"
        if empty:
            self.label.text = text
        else:
            self.label.text += text

    def on_stop(self):
        self.running = False

    async def example(self):
        while self.running:
            try:
                self.line("scanning")
                scanned_devices = await bleak.BleakScanner.discover(1)
                self.line("scanned", True)

                if len(scanned_devices) == 0:
                    raise bleak.exc.BleakError("no devices found")

                for device in scanned_devices:
                    self.line(f"{device.name} ({device.address})")

                for device in scanned_devices:
                    self.line(f"Connecting to {device.name} ...")
                    try:
                        async with bleak.BleakClient(device) as client:
                            for service in client.services:
                                self.line(f"  service {service.uuid}")
                                for characteristic in service.characteristics:
                                    self.line(
                                        f"  characteristic {characteristic.uuid} {hex(characteristic.handle)} ({len(characteristic.descriptors)} descriptors)"
                                    )
                    except bleak.exc.BleakError as e:
                        self.line(f"  error {e}")
                        asyncio.sleep(10)
            except bleak.exc.BleakError as e:
                self.line(f"ERROR {e}")
                await asyncio.sleep(1)
        self.line("example loop terminated", True)


async def main(app):
    await app.async_run("asyncio")  # Run the Kivy app


if __name__ == "__main__":
    Logger.setLevel(logging.DEBUG)

    app = ExampleApp()
    asyncio.run(main(app))
