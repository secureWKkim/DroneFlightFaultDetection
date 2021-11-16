import threading
import webbrowser
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, ColumnDataSource
from bokeh.layouts import gridplot
from bokeh.models import HoverTool


def generate_bokeh_dashboard(fields, title, cols=3, port=5006, update_queue=None):  # cols 모름
    def make_document(doc):
        data = {'time': []}
        for field in fields:
            field_score = 'SCORE_%s' % field
            field_flag = 'FLAG_%s' % field
            data[field] = []
            data[field_score] = []
            data[field_flag] = []
        source = ColumnDataSource(data=data)

        # Add figure for each field
        figures = []
        for field in fields:
            fig = figure(title=field, tools='pan,wheel_zoom,xbox_select,reset', x_axis_type='datetime',
                         plot_width=600, plot_height=300)  # tools: 각각 무슨 역할 하는지는 모름
            fig.line('time', field, source=source)
            hover = HoverTool(  # 뭔진 모른다. 나중에 공부
                tooltips=[
                    ("time", "@time{%F %T}"),
                    ("value", "@%s" % field),
                    ("score", "@%s" % field_score),
                ],
                formatters={"time": "datetime"},
                mode='vline'
            )
            fig.add_tools(hover)

            if figures: # share the x-axis across all figures
                fig.x_range = figures[0].x_range

            figures.append(fig)

        grid = gridplot(figures, ncols=cols, sizing_mode='scale_width')
        doc.title = title
        doc.add_root(grid)

        def update():
            """ Check the queue for updates sent by the restreamer thread
                and pass them over to the bokeh data source """
            data = update_queue.get().to_dict('list')
            source.stream(data)

        if update_queue:  # Update every second
            doc.add_periodic_callback(update, 1000)


    app = Application(FunctionHandler(make_document))
    # Otherwise start the bokeh server in a thread and open browser
    server = Server({'/': app}, port=port)
    dashboard_thread = threading.Thread(target=server.io_loop.start, daemon=True)
    dashboard_thread.start()
    webbrowser.open('http://localhost:%s' % port)