from kivy.garden.graph import Graph, MeshLinePlot
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import random

class RealTimeGraph(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'

        # Create a Graph widget with x-axis ticks every 5 units
        self.graph = Graph(
            xlabel='Time',
            ylabel='Value',
            x_ticks_minor=1,
            x_ticks_major=5,
            y_ticks_major=10,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            xlog=False,
            ylog=False,
            xmin=0,
            xmax=10,
            ymin=0,
            ymax=10,
            size_hint_x=0.8,
        )

        # Create a line plot
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.graph.add_plot(self.plot)

        # Set initial data points
        self.plot_points = [(0, random.uniform(0, 10))]
        self.plot.points = self.plot_points

        # Start the update timer
        self.current_x = 0  # Track the x-value over time

        # Add widgets to the layout
        self.add_widget(self.graph)

        # Current value printer
        self.current_value = Label(text="Weight\n0", size_hint_x=0.2)
        self.add_widget(self.current_value)

    def update_graph(self, new_y):
        # Add a new point to the plot
        self.current_x += 1
        self.plot_points.append((self.current_x, new_y))

        # Rescale x-axis to always include all points
        self.graph.xmin = 0
        self.graph.xmax = self.current_x + 1  # Show some padding after the last point

        # Find min and max y-values to rescale y-axis
        y_values = [point[1] for point in self.plot_points[1:]]
        self.graph.ymin = min(y_values) - 1  # Adding a bit of padding
        self.graph.ymax = max(y_values) + 1  # Adding a bit of padding

        # Update plot with new points
        self.plot.points = self.plot_points

        # Update value printer
        self.current_value.text = f"Weight\n{round(new_y, 1)}"

    def clear_plot(self):
        # Reset the plot data
        self.plot_points = [(0, random.uniform(0, 10))]
        self.plot.points = self.plot_points
        self.current_x = 0

        # Reset axis limits
        self.graph.xmin = 0
        self.graph.xmax = 10
        self.graph.ymin = 0
        self.graph.ymax = 10
