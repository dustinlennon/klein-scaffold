# pipenv run twistd -ny server.tac

from twisted.application import service
from scaffold.builder import WebsiteBuilder
from scaffold.params import Params

application = service.Application('web')
params = Params.from_path("app/config.yaml")

website = (
    WebsiteBuilder(params)
    .set_application(application)
    .set_production(True)
    .build()
)

