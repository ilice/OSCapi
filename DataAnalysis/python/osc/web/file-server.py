import web


urls = (
    '/hello/(.*)', 'hello',
)
app = web.application(urls, globals())


class hello:
    def __init__(self):
        pass

    def GET(self, name):
        if not name:
            name = 'World'
        return 'Hello, ' + name + '!'


if __name__ == "__main__":
    app.run()
