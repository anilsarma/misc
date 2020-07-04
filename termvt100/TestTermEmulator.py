import TermEmulator as term

class MyHandler:
    def __init__(self):
        self.emulator = term.V102Terminal(80, 80)
        self.emulator.SetCallback(term.V102Terminal.CALLBACK_SCROLL_UP_SCREEN, self.OnTermEmulatorScrollUpScreen)
        self.emulator.SetCallback(term.V102Terminal.CALLBACK_UPDATE_LINES, self.OnTermEmulatorUpdateLines)
        self.emulator.SetCallback(term.V102Terminal.CALLBACK_UPDATE_CURSOR_POS, self.OnTermEmulatorUpdateCursorPos)
        self.emulator.SetCallback(term.V102Terminal.CALLBACK_UPDATE_WINDOW_TITLE, self.OnTermEmulatorUpdateWindowTitle)
        self.emulator.SetCallback(term.V102Terminal.CALLBACK_UNHANDLED_ESC_SEQ, self.OnTermEmulatorUnhandledEscSeq)



    def OnTermEmulatorScrollUpScreen(self):
        blankLine = "\n"

        for i in range(self.emulator.GetCols()):
            blankLine += ' '
        print("OnTermEmulatorScrollUpScreen:" + blankLine)
        # lineLen =  len(self.txtCtrlTerminal.GetLineText(self.linesScrolledUp))
        #lineLen = self.termCols
        #self.txtCtrlTerminal.AppendText(blankLine)
        #self.linesScrolledUp += 1
        #self.scrolledUpLinesLen += lineLen + 1

    def OnTermEmulatorUpdateLines(self):
        print("OnTermEmulatorUpdateLines")

        screen = self.emulator.GetRawScreen()
        screenRows = self.emulator.GetRows()
        screenCols = self.emulator.GetCols()

        dirtyLines = self.emulator.GetDirtyLines()
        for row in dirtyLines:
            text  = ""
            for col in range(screenCols):
                text += screen[row][col]
            style, fgcolor, bgcolor = self.emulator.GetRendition(row,  col)
            print(" -- dirty {} {}  {} {} {} -- {}".format(row, col, style, fgcolor, bgcolor, text))


    def OnTermEmulatorUpdateCursorPos(self):
        row, col = self.emulator.GetCursorPos()
        print("OnTermEmulatorUpdateCursorPos row={}, col={}".format(row, col))

    def OnTermEmulatorUpdateWindowTitle(self):
        print("OnTermEmulatorUpdateWindowTitle")

    def OnTermEmulatorUnhandledEscSeq(self, escSeq):
        print("Unhandled escape sequence: [" + escSeq)
if __name__ == "__main__":
    print("hello world")
    xterm = MyHandler()
