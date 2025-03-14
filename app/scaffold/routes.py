from klein import Klein
from twisted.web.server import Request
from twisted.web.resource import IResource

from scaffold.params import Params

from jinja2 import Environment, FileSystemLoader
import datetime, pytz

class Routes(object):
  klein = Klein()

  def __init__(self, params : Params):
    self.params = params
    self.j2env = Environment(
      loader = FileSystemLoader(self.params.path("templates")),
      autoescape = True
    )

  def resource(self) -> IResource:
    return self.klein.resource()

  @klein.route("/welcome")
  def home(self, request: Request):    
    template = self.j2env.get_template("welcome.txt.j2")
    rendering = template.render(
      now = self.params.now().strftime("%B %d, %Y %H:%M %Z"),
      url = self.params.url() + request.uri.decode()
    )  

    request.setHeader(b'content-type', b'text/plain')
    request.write(rendering.encode('utf8'))
    request.finish()

    return

