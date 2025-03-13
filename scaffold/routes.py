from klein import Klein
from twisted.web.server import Request
from twisted.web.resource import IResource

from scaffold.params import Params

class Routes(object):
  klein = Klein()

  def __init__(self, params : Params):
    self.params = params

  def resource(self) -> IResource:
    return self.klein.resource()

  @klein.route("/")
  def home(self, request: Request):
    return "welcome"

