from tornado import gen, httpclient, web, escape, ioloop, concurrent
from cachetools import cached

cache = {}


@cached(cache=cache)
@concurrent.return_future
def get_step(step_id, callback):
    print "aAAA"
    step = httpclient.HTTPClient().fetch("https://stepik.org:443/api/steps/" + str(step_id))
    callback(escape.json_decode(step.body)['steps'][0])


class Handler(web.RequestHandler):
    @gen.coroutine
    def get(self):
        try:
            lesson_id = self.request.query_arguments['lesson'][0]
        except Exception:
            self.write("Bad request")  # TODO
            return

        http_client = httpclient.AsyncHTTPClient()
        try:
            response = yield http_client.fetch("https://stepik.org:443/api/lessons/" + lesson_id)
        except httpclient.HTTPError as e:
            raise web.HTTPError(e.code)
        except Exception as e:
            print e
            raise web.HTTPError(500)

        step_ids = escape.json_decode(response.body)['lessons'][0]['steps']
        steps = yield [get_step(step_id) for step_id in step_ids]
        text_steps = [
            step['id'] for step in steps
            if step is not None and step['block']['name'] == 'text'
        ]
        self.write(escape.json_encode(text_steps))
        print cache

app = web.Application([
    (r"/", Handler),
])
app.listen(8888)

ioloop.IOLoop.current().start()
