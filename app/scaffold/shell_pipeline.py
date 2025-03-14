
from twisted.internet import reactor, protocol
from twisted.internet.defer import Deferred
from twisted.internet.interfaces import IReactorTime

class ShellProcessProtocol(protocol.ProcessProtocol):

  def __init__(self, d : Deferred, stdin = b""):
    self.d = d
    self.stdin = stdin
    self.stdout = b""
    
  def connectionMade(self):
    self.transport.write(self.stdin)
    self.transport.closeStdin()

  def outReceived(self, data):
    self.stdout = self.stdout + data

  def processEnded(self, _):
    self.transport.loseConnection()
    self.d.callback(self.stdout)


class ShellPipeline(object):
  proto = ShellProcessProtocol
  
  def __init__(self):
    self.d = Deferred()
    self.deferred_result = Deferred()

  def chain(self, args):
    self.d.addCallback(self._chain, args)

  def _chain(self, stdin, args):
    d = Deferred()
    p = self.proto(d, stdin)

    reactor.spawnProcess(p, args[0], args)
    return d

  def run(self, stdin = b""):
    self.d.addCallback(self.finalize)
    IReactorTime(reactor).callLater(0, self.d.callback, stdin)
    return self.deferred_result

  def finalize(self, result):
    self.deferred_result.callback(result.decode())


if __name__ == '__main__':
  import sys
  import shlex

  chain = [
    """ /usr/bin/find . -type f -not -path "*/__pycache__/*" -print """,
    """ /usr/bin/xargs -I% /usr/bin/md5sum %""",
    """ /usr/bin/sort """,
    """ /usr/bin/md5sum """
  ]
 
  pipe = ShellPipeline()
  for cmd in chain:
    args = shlex.split(cmd)
    pipe.chain(args)
  d = pipe.run()

  d.addCallback(lambda r: print(r.strip(), file=sys.stderr))
  d.addCallback(lambda _: reactor.stop())

  # reactor.callWhenRunning(pipe.run)
  reactor.run()
