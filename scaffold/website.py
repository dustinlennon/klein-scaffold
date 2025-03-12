# usage: server.py [-h] [--production]
#
# launch static content server
#
# options:
#   -h, --help    show this help message and exit
#   --production

# pipenv run python3 website/website.py


import sys

from twisted.application import strports, service
from twisted.application.internet import TimerService
from twisted.application.service import IService
from twisted.internet import reactor
from twisted.internet.interfaces import IReactorTime
from twisted.logger import Logger, LogPublisher, ILogObserver, jsonFileLogObserver, textFileLogObserver
from twisted.web.http import proxiedLogFormatter
from twisted.web.server import Site

import shlex

from scaffold import routes
from scaffold.shell_pipeline import ShellPipeline
from scaffold.helpers import get_config, Helpers

class WebsiteBuilder(object):
  def __init__(self, helpers):
    self.application = service.Application('web')
    self.port = helpers.port
    self.interface = helpers.interface
    self.production = False
    self.observer = None
    self.helpers = helpers
  
  def set_production(self, production):
    self.production = production
    return self

  def set_application(self, application):
    self.application = application
    return self

  def set_observer(self, observer):
    self.observer = observer
    return self

  def build(self):
    if self.observer is None and self.production == False:
      self.observer = textFileLogObserver(sys.stdout)

    elif self.observer is None and self.production == True:
      log_file = open("twistd.log", "a")
      self.observer = jsonFileLogObserver(log_file)

    website = Website(
      observer = self.observer,
      application = self.application,
      production = self.production,
      port = self.port,
      interface = self.interface,
      helpers = self.helpers
    )

    return website
    
  
class Website(routes.Routes):
  log = Logger()

  def __init__(
    self, *, 
    observer : ILogObserver, 
    application,
    production,
    port,
    interface,
    helpers
  ):

    self.publisher = self.log.observer or LogPublisher()
    self.publisher.addObserver(observer)

    self.application = application
    self.service_collection = service.IServiceCollection(self.application)

    self.production = production
    self.port       = port
    self.interface  = interface

    self.helpers    = helpers

    self.fingerprint(cb = self.fp_init)
    self.exit_code = 0

  @property
  def services(self) -> list[IService]:
    return [
      self.service_web,
      self.service_exit_on_change
    ]

  @property
  def service_web(self):
    site = Site( self.resource(), logFormatter = proxiedLogFormatter )
    site.displayTracebacks = not self.production

    service = strports.service(
      f"tcp:port={self.port}:interface={self.interface}",
      site
    )
    return service

  @property
  def service_exit_on_change(self):
    service = TimerService(1, self.fingerprint, self.fp_test)
    return service

  def start_services(self):
    for s in self.services:
      s.setServiceParent(self.service_collection)
      s.startService()

  def fingerprint(self, cb, eb = None):
    chain = [
      """ /usr/bin/find . -type f -not -path "*/__pycache__/*" -print """,
      """ /usr/bin/xargs -I% /usr/bin/md5sum %""",
      """ /usr/bin/sort """,
      """ /usr/bin/md5sum -z """
    ]
  
    pipe = ShellPipeline()
    for cmd in chain:
      args = shlex.split(cmd)
      pipe.chain(args)
    d = pipe.run()

    d.addCallbacks(cb, eb)
    return d

  def fp_test(self, md5):
    if self.production == False and self._md5 != md5:
      self.log.error("halting: md5 changed")
      self.exit_code = 1
      IReactorTime(reactor).callLater(0, reactor.stop)

  def fp_init(self, md5):
    self._md5 = md5
    reactor.callWhenRunning(self.start_services)


if __name__ == "__main__":
  import argparse  
  import sys

  parser = argparse.ArgumentParser(description = 'launch static content server')
  parser.add_argument('--production', action='store_true')
  parser.add_argument('--config', required = True)

  args = parser.parse_args()
  helpers = Helpers.from_path(args.config)

  builder = WebsiteBuilder(helpers)
  website = builder.build()

  reactor.run()

  # Note: exit_code == 1 indicates stale code
  exit_code = website.exit_code
  sys.exit(exit_code)
   
