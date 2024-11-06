import asyncio
import threading

from bleak import BleakScanner, BleakClient
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
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

# UUIDs for the Nordic UART Service (NUS)
NUS_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
RX_CHARACTERISTIC_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
TX_CHARACTERISTIC_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

class ScannerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = None  # Store the BleakClient instance
        self.device_to_connect = None  # Store the device to connect
        self.keep_connected = True
        self.connected = False
        self.data_list = []
        self.screen_manager = ScreenManager()

    def build(self):
        # Main Screen
        self.main_screen = Screen(name='main')
        layout = BoxLayout(orientation='vertical')
        self.output_label = Label(text="Press Scan to start...")
        layout.add_widget(self.output_label)

        self.scan_button = Button(text="Scan", on_press=self.scan_devices, disabled=False)
        layout.add_widget(self.scan_button)
        self.main_screen.add_widget(layout)

        self.screen_manager.add_widget(self.main_screen)
        return self.screen_manager

    def scan_devices(self, instance):
        self.scan_button.disabled = True  # Disable while scanning
        self.keep_connected = True
        if self.connected:
            asyncio.ensure_future(self.disconnect_worker())  # Run the scan in the background
        else:
            asyncio.ensure_future(self.scan_worker())  # Run the scan in the background


    async def scan_worker(self):
        self.output_label.text = "Scanning for devices..."
        devices = await BleakScanner.discover(5)  # Increased timeout to 5 seconds

        # Device List Screen
        device_list_screen = Screen(name='device_list')
        layout = BoxLayout(orientation='vertical')
        grid = GridLayout(cols=1, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        for d in devices:
            button = Button(text=f"{d.name} ({d.address})", on_press=lambda instance, dev=d: self.select_device(dev), size_hint_y=None, height=40)
            grid.add_widget(button)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(grid)
        layout.add_widget(scroll)

        close_button = Button(text="Close", on_press=lambda instance: self.switch_to_main_screen(), size_hint_y=None, height=40)
        layout.add_widget(close_button)
        device_list_screen.add_widget(layout)

        self.screen_manager.add_widget(device_list_screen)
        self.switch_to_screen('device_list')

    def switch_to_screen(self, screen_name):
        self.screen_manager.current = screen_name

    def switch_to_main_screen(self):
        self.switch_to_screen('main')
        self.scan_button.disabled = False

    def select_device(self, device):
        self.device_to_connect = device
        self.switch_to_main_screen()
        self.output_label.text = f"Connecting to {device.name}..."
        self.scan_button.disabled = True  # Disable while connecting
        asyncio.ensure_future(self.connect_worker(device))

    async def notification_handler(self, sender, data):
        """Handle received data from the TX characteristic."""
        self.data_list.append(data.decode())
        Clock.schedule_once(lambda dt: self.update_label(f"Received {self.data_list}", dt), 0)

    async def connect_worker(self, device):
        async with BleakClient(device) as client:
            self.connected = True
            #Clock.schedule_once(lambda dt: self.update_label(f"Connected to {device.name}", dt), 0)
            Clock.schedule_once(lambda dt: self.update_scan_button("Disconnect", dt), 0)
            await client.start_notify(TX_CHARACTERISTIC_UUID, self.notification_handler)
            while self.keep_connected:
                await asyncio.sleep(1)
            await client.stop_notify(TX_CHARACTERISTIC_UUID)
            await client.disconnect()
            self.connected = False

    def update_label(self, text, dt):
        self.output_label.text = text

    def update_scan_button(self, text, dt):
        self.scan_button.text = text
        self.scan_button.disabled = False

    async def disconnect_worker(self):
        self.keep_connected = False
        await asyncio.sleep(1)
        Clock.schedule_once(lambda dt: self.update_label("Disconnected", dt), 0)
        Clock.schedule_once(lambda dt: self.update_scan_button("Scan", dt), 0)

async def main(app):
    await app.async_run("asyncio")  # Run the Kivy app

if __name__ == '__main__':
    app = ScannerApp()
    asyncio.run(main(app))
