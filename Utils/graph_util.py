from pychartjs import BaseChart, ChartType, Color, Options
import textwrap
from pychartjs.Color import Red, Blue, Green
from bokeh.embed import components
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, RangeTool
from bokeh.plotting import figure
from math import pi


class MyBarGraph(BaseChart):
    type = ChartType.Line

    class labels:
        labels = []

    class data:
        label = ""
        data = []
        backgroundColor = Color.Gray


def build_range_tool_graph(stock_data):
    source = ColumnDataSource(data=dict(date=stock_data.time, close=stock_data.close))

    plot = figure(
        plot_height=300,
        plot_width=950,
        sizing_mode='scale_width',
        tools="xpan",
        toolbar_location=None,
        x_axis_type="datetime",
        x_axis_location="above",
        background_fill_color="white",                                                                    # color here
        x_range=(stock_data.time[280], stock_data.time[355])
    )
    plot.sizing_mode = "scale_both"
    plot.line('date', 'close', source=source)
    plot.yaxis.axis_label = 'Price'
    select = figure(
        # title="Drag the middle and edges of the selection box to change the range above",
        plot_height=100,
        # plot_width=1000,
        sizing_mode='scale_width',
        y_range=plot.y_range,
        x_axis_type="datetime",
        y_axis_type=None,
        tools="",
        toolbar_location=None,
        background_fill_color="white"                                                                     # color here
    )
    select.sizing_mode = "scale_both"
    range_tool = RangeTool(x_range=plot.x_range)
    range_tool.overlay.fill_color = "white"                                                             # color here
    range_tool.overlay.fill_alpha = 0.1  # transparent

    select.line('date', 'close', source=source)
    select.ygrid.grid_line_color = None
    select.add_tools(range_tool)
    select.toolbar.active_multi = range_tool
    return components(column(plot, select))


def build_candlestick_graph(source):
    # These lines are there to color. The red and green bars for down and up days
    increasing = source.close > source.open
    decreasing = source.open > source.close
    w = 12 * 60 * 60 * 1000

    # TOOLS = "pan, wheel_zoom, box_zoom, reset, save"
    title = 'EUR to USD chart'

    p = figure(x_axis_type="datetime", plot_height=200, title=title)
    p.sizing_mode = "scale_both"
    p.xaxis.major_label_orientation = pi / 4
    p.grid.grid_line_alpha = 0.3
    p.segment(source.time, source.high, source.time, source.low, color="black")
    p.vbar(source.time[increasing], w, source.open[increasing], source.close[increasing],
           fill_color="#D5E1DD", line_color="black")
    p.vbar(source.time[decreasing], w, source.open[decreasing], source.close[decreasing], fill_color="#F2583E",
           line_color="black")
    return components(p)
