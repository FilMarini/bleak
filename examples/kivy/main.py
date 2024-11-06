import asyncio
import threading

from bleak import BleakScanner, BleakClient
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.utils import platform

if platform == "android":
    from android.permissions import request_permissions, Permission, check_permission
    permissions_list=[
        #Permission.INTERNET,
        Permission.BLUETOOTH_ADMIN,
        Permission.BLUETOOTH_SCAN,
        Permission.BLUETOOTH_CONNECT,
        Permission.ACCESS_COARSE_LOCATION,
        Permission.ACCESS_FINE_LOCATION,
        Permission.ACCESS_BACKGROUND_LOCATION, # If needed
    ]

    request_permissions(permissions_list)


class ScannerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_address = "2C:CF:67:97:DE:C7"
        self.client = None  # Store the BleakClient instance
        self.device_to_connect = None  # Store the device to connect
        self.keep_connected = True
        self.need_to_scan = True
        self.connected = False

    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.output_label = Label(text="Press Scan to start...")
        self.layout.add_widget(self.output_label)

        self.connect_disconnect_button = Button(text="Scan", on_press=self.connect_disconnect, disabled=False)
        self.layout.add_widget(self.connect_disconnect_button)

        # Start the scanning thread
        #threading.Thread(target=self.scan_worker).start()
        return self.layout

    async def scan_worker(self):
        self.output_label.text = "Scanning for devices..."
        devices = await BleakScanner.discover(1)
        self.need_to_scan = False
        # Filter for the target device
        target_device = None
        for d in devices:
            if d.address.lower() == self.target_address.lower():
                target_device = d
                break

        if target_device:
            device_info = f"Found target device: {target_device.name}"
            self.device_to_connect = target_device  # Store the device to connect
            Clock.schedule_once(lambda dt: self.update_label(device_info, dt), 0)
            Clock.schedule_once(lambda dt: self.update_connect_disconnect_button("Connect", dt), 0)
            self.keep_connected = True
        else:
            Clock.schedule_once(lambda dt: self.update_label("Target device not found.", dt), 0)


    def update_label(self, text, dt):
        self.output_label.text = text
        if self.device_to_connect:
            self.connect_disconnect_button.disabled = False

    def connect_disconnect(self, instance):
        if self.connected:
            self.connect_disconnect_button.disabled = True  # Disable while disconnecting
            asyncio.ensure_future(self.disconnect_worker())  # Run the scan in the background
        elif self.need_to_scan:
            self.connect_disconnect_button.disabled = True  # Disable while scanning
            asyncio.ensure_future(self.scan_worker())  # Run the scan in the background
        else:  # Not connected, so connect
            if self.device_to_connect:
                self.output_label.text = f"Connecting to {self.device_to_connect.name}..."
                self.connect_disconnect_button.disabled = True  # Disable while connecting
                asyncio.ensure_future(self.connect_worker(self.device_to_connect))  # Run the scan in the background
                #threading.Thread(target=self.connect_worker, args=(self.device_to_connect,)).start()

    async def connect_worker(self, device):
        async with BleakClient(device) as client:
            self.connected = True
            Clock.schedule_once(lambda dt: self.update_label(f"Connected to {device.name}", dt), 0)
            Clock.schedule_once(lambda dt: self.update_connect_disconnect_button("Disconnect", dt), 0)
            while self.keep_connected:
                await asyncio.sleep(1)
            await client.disconnect()



    def update_connect_disconnect_button(self, text, dt):
        self.connect_disconnect_button.text = text
        self.connect_disconnect_button.disabled = False

    async def disconnect_worker(self):
        self.keep_connected = False
        self.need_to_scan = True
        self.connected = False
        await asyncio.sleep(1)
        Clock.schedule_once(lambda dt: self.update_label("Disconnected", dt), 0)
        Clock.schedule_once(lambda dt: self.update_connect_disconnect_button("Scan", dt), 0)

async def main(app):
    await app.async_run("asyncio")  # Run the Kivy app


if __name__ == '__main__':
    app = ScannerApp()
    asyncio.run(main(app))
