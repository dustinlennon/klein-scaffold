from twisted.application import strports, service
from twisted.application.internet import TimerService
from twisted.application.service import IService
from twisted.internet import reactor
from twisted.internet.interfaces import IReactorTime, IReactorCore
from twisted.logger import Logger, LogPublisher, ILogObserver
from twisted.web.http import proxiedLogFormatter
from twisted.web.server import Site

import shlex

from scaffold.params import Params
from scaffold.routes import Routes
from scaffold.shell_pipeline import ShellPipeline
   
  
class Website(Routes):
  log = Logger()

  def __init__(
    self, *, 
    observer : ILogObserver, 
    application,
    production,
    params : Params
  ):
    super().__init__(params)

    self.publisher = self.log.observer or LogPublisher()
    self.publisher.addObserver(observer)

    self.application = application
    self.service_collection = service.IServiceCollection(self.application)

    self.production = production

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
      f"tcp:port={self.params.port}:interface={self.params.interface}",
      site
    )
    return service

  @property
  def service_exit_on_change(self):
    if self.production:
      op = lambda cb, eb = None: None
    else:
      op = self.fingerprint
      
    service = TimerService(1, op, self.fp_test)
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
    if self._md5 != md5:
      self.log.error("halting: md5 changed")
      self.exit_code = 1
      IReactorTime(reactor).callLater(0, reactor.stop)

  def fp_init(self, md5):
    self._md5 = md5
    IReactorCore(reactor).callWhenRunning(self.start_services)
