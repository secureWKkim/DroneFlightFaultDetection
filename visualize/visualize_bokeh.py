import threading
import webbrowser
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, ColumnDataSource
from bokeh.layouts import gridplot


def generate_bokeh_dashboard(fields, title, cols=3, port=5006, update_queue=None):  # cols 모름
    def make_document(doc):
        data = {}
        for field in fields:
            data[field] = []
        source = ColumnDataSource(data=data) # real-time data

        # Add figure for each field
        figures = []
        for field in fields:
            fig = figure(title=field, tools='pan,wheel_zoom,xbox_select,reset', x_axis_type='datetime',
                         plot_width=600, plot_height=300)
            fig.line('TIMESTAMP', field, source=source)
            if figures:  # share the x-axis across all figures
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

    app = Application(FunctionHandler(make_document))  # curdoc 역할
    server = Server({'/': app}, port=port)
    dashboard_thread = threading.Thread(target=server.io_loop.start, daemon=True)
    dashboard_thread.start()
    webbrowser.open('http://localhost:%s' % port)