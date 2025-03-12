from klein import Klein
from twisted.web.server import Request
from twisted.web.resource import IResource
from scaffold import helpers

class Routes(object):
  klein = Klein()

  def resource(self) -> IResource:
    return self.klein.resource()

  @klein.route("/")
  def home(self, request: Request):
    return "welcome"

