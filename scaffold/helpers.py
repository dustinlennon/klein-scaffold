import os
from types import SimpleNamespace

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


class Helpers(object):
  def __init__(self, cfg):
    self._env_prefix   = cfg.env_prefix
    self._install_path = cfg.install_path
    self._hostname     = cfg.defaults.hostname
    self._port         = cfg.defaults.port
    self._interface    = cfg.defaults.interface

  @classmethod
  def from_path(cls, config_path):
    cfg = get_config(config_path)
    return cls(cfg)

  @property
  def hostname(self):
    return os.environ.get(f"{self._env_prefix}_HOST", self._hostname)

  @property
  def port(self):
    return os.environ.get(f"{self._env_prefix}_PORT", self._port)

  @property
  def interface(self):
    return os.environ.get(f"{self._env_prefix}_INTERFACE", self._interface)

  def build_url(self, *args, relative = False):
    root = os.environ.get(f"{self._env_prefix}_ROOT_URL", "").strip("/")
    path = "/".join([root, *args]).strip("/")

    if relative == False:
      scheme = "http"
      url = f"{scheme}://{self.hostname}:{self.port}/{path}"

    return url

  def build_path(self, *args):
    pth = os.path.sep.join([self._install_path] + list(args))
    return pth

