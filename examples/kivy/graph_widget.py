from kivy.garden.graph import Graph, MeshLinePlot
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
import random

class RealTimeGraph(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # Create a Graph widget with x-axis ticks every 5 units
        self.graph = Graph(
            xlabel='Time',
            ylabel='Value',
            x_ticks_minor=1,
            x_ticks_major=5,
            y_ticks_major=1,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            xlog=False,
            ylog=False,
            xmin=0,
            xmax=10,
            ymin=0,
            ymax=10,
        )

        # Create a line plot
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.graph.add_plot(self.plot)

        # Set initial data points
        self.plot_points = [(0, random.uniform(0, 10))]
        self.plot.points = self.plot_points

        # Start the update timer
        self.current_x = 0  # Track the x-value over time
        #Clock.schedule_interval(self.update_graph, 1.0)

        # Create a clear button
        #clear_button = Button(text="Clear Plot", size_hint_y=None, height=140)
        #clear_button.bind(on_press=self.clear_plot)

        # Add widgets to the layout
        self.add_widget(self.graph)
        #self.add_widget(clear_button)

    def update_graph(self):
        # Add a new point to the plot
        self.current_x += 1
        new_y = random.uniform(0, 10)
        self.plot_points.append((self.current_x, new_y))

        # Rescale x-axis to always include all points
        self.graph.xmin = 0
        self.graph.xmax = self.current_x + 1  # Show some padding after the last point

        # Find min and max y-values to rescale y-axis
        y_values = [point[1] for point in self.plot_points]
        self.graph.ymin = min(y_values) - 1  # Adding a bit of padding
        self.graph.ymax = max(y_values) + 1  # Adding a bit of padding

        # Update plot with new points
        self.plot.points = self.plot_points

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
