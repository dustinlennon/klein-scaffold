import os
from types import SimpleNamespace
from urllib.parse import urlparse, urljoin, urlunparse, ParseResult

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def get_config(config_path):
  with open(config_path) as f:
    config = load(f, Loader=Loader)
    if config is not None:
      config = _preprocess(config)
  return config

def _preprocess(d):
  obj = d
  if isinstance(d, list):
    dx = []
    for o in d:
      dx.append( _preprocess(o) )
    obj = dx
  elif isinstance(d, dict):
    dx = {}
    for k,v in d.items():
      dx[k] = _preprocess(v)
    obj = SimpleNamespace(**dx)

  return obj


class Params(object):
  def __init__(self, cfg):
    self._env_prefix    = cfg.env_prefix
    self._install_path  = cfg.install_path

    self.interface = os.environ.get(f"{self._env_prefix}_INTERFACE", cfg.env_defaults.interface)

    url_root       = os.environ.get(f"{self._env_prefix}_URL_ROOT",  cfg.env_defaults.url_root)
    self._url_root = url_root

    parsed_url        = urlparse(url_root)
    self._parsed_url  = parsed_url

    self.hostname = parsed_url.hostname
    self.port     = parsed_url.port or 80


  @classmethod
  def from_path(cls, config_path):
    cfg = get_config(config_path)
    return cls(cfg)

  def url(self, *args, relative = False) -> str:
    rel_path = "/".join([a.strip("/") for a in args])

    if relative:
      result = "/" + rel_path

    else:
      path      = self._parsed_url.path.rstrip("/")
      path_ext  = "/".join([path, rel_path])
      url       = self._parsed_url._replace(path = path_ext)
      result    = urlunparse(url)

    return result

  def path(self, *args):
    pth = os.path.sep.join([self._install_path] + args)
    return pth

# if __name__ == '__main__':
#   self = Params.from_path("config.yaml")

#   args = ["foo", "bar"]
#   self.url(*args)