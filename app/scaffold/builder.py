# usage: builder.py [-h] [--production]
#
# launch static content server
#
# options:
#   -h, --help    show this help message and exit
#   --production

# pipenv run python3 scaffold/builder.py


import sys
from twisted.application import service
from twisted.logger import jsonFileLogObserver, textFileLogObserver

from scaffold.params import Params
from scaffold.website import Website

class WebsiteBuilder(object):
  def __init__(self, params : Params):
    self.application = service.Application('web')
    self.production = False
    self.observer = None
    self.params = params
  
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
      params = self.params
    )

    return website
    

if __name__ == '__main__':
  import argparse  
  import sys

  from twisted.internet import reactor

  parser = argparse.ArgumentParser(description = 'launch static content server')
  parser.add_argument('--production', action='store_true')
  parser.add_argument('--config', required = True)

  args = parser.parse_args()
  params = Params.from_path(args.config)

  website = (
      WebsiteBuilder(params)
      .set_production(args.production)
      .build()
  )

  reactor.run()

  # Note: exit_code == 1 indicates stale code
  exit_code = website.exit_code
  sys.exit(exit_code)
   
