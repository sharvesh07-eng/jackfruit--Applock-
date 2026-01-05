import wx
import math

class AppLocker(wx.Frame):
    def __init__(self):
        super().__init__(None, title="App Locker")
        self.SetBackgroundColour(wx.BLACK)
        self.ShowFullScreen(True) 

        self.correct_password = None  # Will be set by user when Password is selected
        self.correct_pin = "1234"
        self.correct_pattern = [1, 2, 3, 4]  # setting password pattern and pin

        self.attempts = 0
        self.max_attempts = 5  # number of attempts before lockout

        self.input_text = None
        self.canvas = None

        self.setup_ui()

    # ---------- UI ----------
    def setup_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        top_panel = wx.Panel(self)
        top_panel.SetBackgroundColour(wx.BLACK)
        top_sizer = wx.BoxSizer(wx.VERTICAL)  # box to contain elements (select security type text)

        label = wx.StaticText(top_panel, label="Select Security Type:")
        label.SetForegroundColour(wx.WHITE)
        label.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
        top_sizer.Add(label, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        radio_panel = wx.Panel(top_panel)
        radio_panel.SetBackgroundColour(wx.BLACK)
        radio_sizer = wx.BoxSizer(wx.VERTICAL)  # box to contain radio buttons

        self.radio_password = wx.RadioButton(radio_panel, label="Password", style=wx.RB_GROUP, size=(150, -1))
        self.radio_pin = wx.RadioButton(radio_panel, label="PIN", size=(150, -1))
        self.radio_pattern = wx.RadioButton(radio_panel, label="Pattern", size=(150, -1))  # radio buttons for each security type

        for rb in (self.radio_password, self.radio_pin, self.radio_pattern):
            rb.SetForegroundColour(wx.WHITE)
            rb.SetBackgroundColour(wx.BLACK)
            rb.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
            rb.Bind(wx.EVT_RADIOBUTTON, self.on_security_type_change)
            radio_sizer.Add(rb, 0, wx.ALL | wx.ALIGN_CENTER, 5)  # colour and font for radio buttons

        self.radio_pin.SetValue(True)  # PIN by default

        radio_panel.SetSizer(radio_sizer)
        top_sizer.Add(radio_panel, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        top_panel.SetSizer(top_sizer)

        self.input_panel = wx.Panel(self)  # panel to actually take the input
        self.input_panel.SetBackgroundColour(wx.BLACK)
        self.input_sizer = wx.BoxSizer(wx.VERTICAL)
        self.input_panel.SetSizer(self.input_sizer)

        self.refresh_input_ui()

        main_sizer.Add(top_panel, 0, wx.ALL | wx.EXPAND, 20)
        main_sizer.Add(self.input_panel, 1, wx.ALL | wx.EXPAND, 40)

        self.SetSizer(main_sizer)
        self.Layout()

    def get_security_type(self):
        if self.radio_password.GetValue():
            return "password"
        if self.radio_pin.GetValue():
            return "pin"
        return "pattern"  # chosen type is returned 

    def on_security_type_change(self, event):
        stype = self.get_security_type()
        if stype == "password" and self.correct_password is None:
            # Prompt user to set password immediately when Password radio is selected
            dlg = wx.PasswordEntryDialog(self, "Enter your password for this session:", "Set Password")
            if dlg.ShowModal() == wx.ID_OK:
                self.correct_password = dlg.GetValue()
                wx.MessageBox(f"Password set successfully! You can now unlock with this password.", "Password Set", wx.OK | wx.ICON_INFORMATION)
            else:
                # User cancelled, switch back to PIN
                self.radio_pin.SetValue(True)
                wx.MessageBox("Password setup cancelled. Switched to PIN mode.", "Cancelled", wx.OK | wx.ICON_WARNING)
        self.refresh_input_ui()  # when chosen type is changed, it refreshes the input UI

    def refresh_input_ui(self):
        self.input_sizer.Clear(True)
        stype = self.get_security_type()

        if stype == "password":
            if self.correct_password is None:
                # Should not happen due to on_security_type_change check
                lbl = wx.StaticText(self.input_panel, label="Please select Password again to set it first.")
                lbl.SetForegroundColour(wx.WHITE)
                lbl.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
                self.input_sizer.Add(lbl, 0, wx.ALL | wx.ALIGN_CENTER, 10)
                self.input_panel.Layout()
                return
            
            style = wx.TE_CENTER | wx.TE_PASSWORD  # centers the text and masks password
            self.input_text = wx.TextCtrl(self.input_panel, style=style)
            self.input_text.SetFont(wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
            self.input_sizer.Add(self.input_text, 0, wx.ALL | wx.ALIGN_CENTER, 10)
            self.input_text.SetFocus()  # text input for password

            btn = wx.Button(self.input_panel, label="Unlock")
            btn.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
            btn.Bind(wx.EVT_BUTTON, self.on_check_input)
            self.input_sizer.Add(btn, 0, wx.ALL | wx.ALIGN_CENTER, 10)  # unlock button 

        elif stype == "pin":
            style = wx.TE_CENTER  # centers the text for PIN
            self.input_text = wx.TextCtrl(self.input_panel, style=style)
            self.input_text.SetFont(wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
            self.input_sizer.Add(self.input_text, 0, wx.ALL | wx.ALIGN_CENTER, 10)
            self.input_text.SetFocus()  # text input for PIN

            btn = wx.Button(self.input_panel, label="Unlock")
            btn.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
            btn.Bind(wx.EVT_BUTTON, self.on_check_input)
            self.input_sizer.Add(btn, 0, wx.ALL | wx.ALIGN_CENTER, 10)  # unlock button 

        else:  # pattern
            lbl = wx.StaticText(self.input_panel, label="Draw Pattern to Unlock:")
            lbl.SetForegroundColour(wx.WHITE)
            lbl.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
            self.input_sizer.Add(lbl, 0, wx.ALL | wx.ALIGN_CENTER, 10)  # label for pattern is created

            self.canvas = PatternCanvas(self.input_panel)  # canvas for user to draw
            self.canvas.SetMinSize((300, 300))
            self.input_sizer.Add(self.canvas, 0, wx.ALL | wx.ALIGN_CENTER, 10)

            btn = wx.Button(self.input_panel, label="Unlock")  # unlock button for pattern
            btn.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
            btn.Bind(wx.EVT_BUTTON, self.on_check_input)
            self.input_sizer.Add(btn, 0, wx.ALL | wx.ALIGN_CENTER, 10)

            clear_btn = wx.Button(self.input_panel, label="Clear Pattern")  # button to clear the pattern
            clear_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
            clear_btn.Bind(wx.EVT_BUTTON, lambda e: self.canvas.clear_pattern())  # lambda function to call clear pattern function
            self.input_sizer.Add(clear_btn, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.input_panel.Layout()

    # ---------- logic ----------
    def on_check_input(self, event):
        if self.attempts >= self.max_attempts:
            return  # if number of attempts are exceeded, the app lock shuts down

        stype = self.get_security_type()  # gets the chosen security type

        if stype == "password":
            if self.correct_password is None:
                wx.MessageBox("Password not set! Please select Password option first.", "Error", wx.OK | wx.ICON_ERROR)
                return
            entered = self.input_text.GetValue()  # user input
            if entered == self.correct_password:
                wx.MessageBox("Access granted!", "Success", wx.OK | wx.ICON_INFORMATION) 
                self.Close()
            else:
                self.handle_wrong_attempt()  # calls the function to handle wrong attempts
                self.input_text.Clear() 
        elif stype == "pin":
            entered = self.input_text.GetValue()  # user input
            if entered == self.correct_pin:
                wx.MessageBox("Access granted!", "Success", wx.OK | wx.ICON_INFORMATION) 
                self.Close()
            else:
                self.handle_wrong_attempt()  # calls the function to handle wrong attempts
                self.input_text.Clear()
        else:  # pattern
            if self.canvas.pattern_input == self.correct_pattern:
                wx.MessageBox("Access granted!", "Success", wx.OK | wx.ICON_INFORMATION) 
                self.Close()  # checks the pattern 
            else:
                self.handle_wrong_attempt()
                self.canvas.clear_pattern()  # calls the function to handle wrong attempts

    def handle_wrong_attempt(self):
        self.attempts += 1 
        remaining = self.max_attempts - self.attempts  # decreases number of available attempts by 1 if wrong attempt
        if remaining <= 0:
            wx.MessageBox("Access denied!\nMaximum attempts reached. Exiting.",
                          "Error", wx.OK | wx.ICON_ERROR)   # if all attempts are used
            self.Close()
        else:
            wx.MessageBox("Access denied! Try again.\nAttempts left: %d" % remaining,
                          "Error", wx.OK | wx.ICON_ERROR)  # if attempts are still left

class PatternCanvas(wx.Panel): 
    def __init__(self, parent):  # input panel as parent
        super().__init__(parent)
        self.SetBackgroundColour(wx.BLACK)  # background colour for drawing area

        self.pattern_input = []  # stores the visited nodes
        self.node_centers = {} 
        self.visited_nodes = set()  # already visited nodes are stored here
        self.drawing = False  # indicate if drawing is in progress

        self.bind_events()
        self.init_nodes()

    def bind_events(self):
        self.Bind(wx.EVT_PAINT, self.on_paint)  # to repaint the canvas
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)  # left mouse button
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)  # left mouse button released
        self.Bind(wx.EVT_MOTION, self.on_motion)  # mouse movement

    def init_nodes(self):
        r = 20  # radius of each node
        gap = 100  # gap between nodes
        start_x, start_y = 50, 50  # starting position for first node
        idx = 1  # index for each node
        for row in range(3):
            for col in range(3):
                x = start_x + col * gap
                y = start_y + row * gap
                self.node_centers[idx] = (x, y)  # position of each node
                idx += 1  # index is increased

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush(wx.BLACK))  # brush is selected for background
        dc.Clear()

        r = 20
        dc.SetPen(wx.Pen(wx.WHITE, 2))  # pen to draw nodes

        for idx, (x, y) in self.node_centers.items():
            if idx in self.visited_nodes:
                dc.SetBrush(wx.Brush(wx.CYAN))  # cyan if node is visited
            else:
                dc.SetBrush(wx.Brush(wx.BLACK))  # black if not 
            dc.DrawCircle(x, y, r)

        dc.SetPen(wx.Pen(wx.CYAN, 3))
        for i in range(1, len(self.pattern_input)):
            x1, y1 = self.node_centers[self.pattern_input[i - 1]]
            x2, y2 = self.node_centers[self.pattern_input[i]]
            dc.DrawLine(x1, y1, x2, y2)  # draws line between visited nodes

    def on_left_down(self, event):  # if left button is pressed, a new pattern starts
        self.pattern_input[:] = []  # clears pattern input
        self.visited_nodes.clear()  # clears visited nodes
        self.drawing = True  # drawing is in progress
        self.check_node(event.GetX(), event.GetY())  # checks whether mouse is over a node
        self.Refresh() 

    def on_left_up(self, event):
        self.drawing = False  # when mouse button is released drawing stops 

    def on_motion(self, event):
        if self.drawing and event.LeftIsDown():  # if drawing is true and left button is down motion is tracked
            self.check_node(event.GetX(), event.GetY())  # checks mouse position
            self.Refresh() 

    def check_node(self, x, y):
        for idx, (nx, ny) in self.node_centers.items():  # checks if mouse is over a node
            if math.hypot(x - nx, y - ny) <= 25 and idx not in self.visited_nodes:  # if mouse is within 25 pixels the node is considered visited
                self.pattern_input.append(idx)  # adds the node to pattern input
                self.visited_nodes.add(idx)  # adds the node to visited nodes
                break

    def clear_pattern(self):
        self.pattern_input[:] = []  # clears input pattern
        self.visited_nodes.clear()  # clears selected patterns
        self.Refresh() 

if __name__ == "__main__":
    app = wx.App() 
    frame = AppLocker()
    frame.Show()
    app.MainLoop()
