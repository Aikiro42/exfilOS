from core.file import File
from core.colors import color
from core.const import bcolors

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document

class TextEditor:
  def __init__(self, file: File | None):
    self.file = file

  def start(self) -> str:
    # validate file
    if self.file is None:
      print("ERROR: File not loaded.")
      return
    if self.file.isDir:
      print(f"ERROR: Cannot edit '{self.file.path}': File is directory.")
      return
    
    # editor-related variables
    session = PromptSession(erase_when_done=True)
    print(color(f"EDITING: {self.file.name} ({self.file.path})", bcolors.INFO))
    def prompt_continuation(width, line_number, wrap_count):
      if wrap_count > 0:
        return ANSI(color(" " * (width - 3) + " > ", bcolors.GRAY))
      else:
        text = ("%i > " % (line_number + 1)).rjust(width)
        return ANSI(color("%s", bcolors.GRAY)) % text
    try:
      session.prompt(
        ANSI(color("1 > ", bcolors.GRAY)),
        multiline=True,
        default=self.file.data,
        prompt_continuation=prompt_continuation,
        bottom_toolbar="Ctrl+C: Exit")

    except KeyboardInterrupt:
      pass
    
    return session.default_buffer.text

