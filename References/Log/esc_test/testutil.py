class Test:
  def __init__(self, *sources, key=None, description=""):
    self.sources = sources
    self.description = description
    self.key = key

  def __str__(self):
    s = ""
    s += "TEST (%s)\n" % self.key
    s += "Sources:\n"
    for source in self.sources:
      s += "\t%s - %s\n" % (source, source.filename)

    s += self.description
    return s

