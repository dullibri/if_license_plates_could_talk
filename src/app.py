import visualization.app
import data

if __name__ == '__main__':
    app = visualization.app.VisApp()
    server = app.app.server
    app.run()
