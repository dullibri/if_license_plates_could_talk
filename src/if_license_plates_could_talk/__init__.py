try:
    from . import visualization

    app = visualization.app.VisApp()
    server = app.app.server
except:
    pass
