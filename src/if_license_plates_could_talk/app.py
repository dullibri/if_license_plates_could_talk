import visualization.app

app = visualization.app.VisApp()
server = app.app.server


def main():
    app.run()


if __name__ == "__main__":
    main()
