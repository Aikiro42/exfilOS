from core.file import File
from core.colors import color
from core.const import bcolors

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document

class TextEditor:
  @staticmethod
  def edit(file: File) -> str:
    # validate file
    if file.isDir:
      print(f"ERROR: Cannot edit '{file.path}': File is directory.")
      return
    
    # editor-related variables
    session = PromptSession(erase_when_done=True)
    print(color(f"EDITING: {file.name} ({file.path})", bcolors.INFO))
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
        default=file.data,
        prompt_continuation=prompt_continuation,
        bottom_toolbar="Ctrl+C: Exit")

    except KeyboardInterrupt:
      pass
    
    return session.default_buffer.text

