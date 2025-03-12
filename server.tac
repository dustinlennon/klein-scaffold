# pipenv run twistd -ny server.tac

from twisted.application import service
from scaffold.website import WebsiteBuilder
from scaffold.helpers import Helpers

application = service.Application('web')
helpers = Helpers.from_path("config.yaml")

website = (
    WebsiteBuilder(helpers)
    .set_application(application)
    .set_production(True)
    .build()
)

