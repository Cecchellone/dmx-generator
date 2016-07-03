"""Subclass of MainFrameBase, which is generated by wxFormBuilder."""

import wx
import gui
import sys
import time
import colorsys

# need to install this from http://pyserial.sourceforge.net/
import serial

#local goodness
import pollingthread

# Implementing MainFrameBase
class MainFrame( gui.MainFrameBase ):
    def __init__( self, parent ):
	gui.MainFrameBase.__init__( self, parent )
        portname = "COM20"
        #setup serial port for DMX, blocking write, two stopbits, 250Kbaud
        ser = serial.Serial(port=portname,
                            baudrate=250000,
                            writeTimeout = None,
                            stopbits=serial.STOPBITS_TWO)
        print "opened port " + portname + " for DMX"

        sys.stdout.flush()
        self.r = 0
        self.g = 0
        self.b = 0
        self.y = 0
        self.dmx = pollingthread.HW_Interface(ser,0.1)


		
    def m_btHelloClick( self, event ):
        self.m_btPython.Enable(True)
        self.m_rtMain.AppendText("Hello")
	
    def m_btPythonClick( self, event ):
        self.m_rtMain.AppendText(" Python!")
	
    def m_mniOpenClick( self, event ):
        fdlg = wx.FileDialog(self,"Choose a file","Open file",wx.EmptyString,"*.*",wx.FD_OPEN | wx.FD_FILE_MUST_EXIST);
        if fdlg.ShowModal() != wx.ID_OK:
            return;
        self.m_rtMain.LoadFile(fdlg.GetPath())
			
    def m_mniSaveClick( self, event ):
        fdlg = wx.FileDialog(self,"Choose a file","Save file",wx.EmptyString,"*.*",wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT);
        if fdlg.ShowModal() != wx.ID_OK:
            return;
        self.m_rtMain.SaveFile(fdlg.GetPath())
			
    def m_mniExitClick( self, event ):
        self.Close()
	
    def m_mniAboutClick( self, event ):
        wx.MessageBox("oneminutepython template. ","oneminutepython")
	
	
###################################################### new stuff below
    def m_btLedOnOnButtonClick(self,evt):
        """pressed the "send this" button so send "this" """
        print 'sent "this"' # print string to console
        self.send_color()

    def m_btLedOffOnButtonClick(self,evt):
        """pressed the "send this" button so send "this" """
        print 'sent "this"' # print string to console
        sys.stdout.flush()
        self.dmx.set_rgba((0,0,0,0))

    def m_btSVROffOnButtonClick(self,evt):
        self.dmx.set_server(False)

    def m_btSVROnOnButtonClick(self,evt):
        self.dmx.set_server(True)


    def m_HSVOnScroll(self,evt):
        h = self.m_Hslider.GetValue()/100.0
        s = self.m_Sslider.GetValue()/100.0
        v = self.m_Vslider.GetValue()/100.0

        if self.m_RGBY_select.GetSelection() == 0:
            self.r, self.g, self.b = colorsys.hsv_to_rgb(h,s,v)
            self.y = 0
        elif self.m_RGBY_select.GetSelection() == 1:
            self.r, self.g, self.b, self.y = self.hsv_to_rgby_naive(h,s,v)
        elif self.m_RGBY_select.GetSelection() == 2:
            self.r, self.g, self.b, self.y = self.hsv_to_rgby(h,s,v)


        self.m_Rslider.SetValue(self.r*100)
        self.m_Gslider.SetValue(self.g*100)
        self.m_Bslider.SetValue(self.b*100)
        self.m_Yslider.SetValue(self.y*100)
        self.send_color()

    def m_RGBOnScroll(self,evt):
        """pressed the "send slider" button so send the slider value"""
        self.send_color()

    def send_color(self):
        #outstr = "Slider = %d" % slider
        #print outstr # print string to console
        self.r = self.m_Rslider.GetValue()
        self.g = self.m_Gslider.GetValue()
        self.b = self.m_Bslider.GetValue()
        self.y = self.m_Yslider.GetValue()
        base = []
        if self.m_NWtoggle.GetValue():
            base.append(1)
        if self.m_SWtoggle.GetValue():
            base.append(5)
        if self.m_SEtoggle.GetValue():
            base.append(10)
        if self.m_NEtoggle.GetValue():
            base.append(14)
        if len(base) == 0:
            base = [1, 5, 10, 14]
        self.dmx.base = base
        self.dmx.set_rgba((self.r,self.g,self.b,self.y))
        

    def hsv_to_rgby_naive(self, h, s, v):
        """Naive implementation of hsv colorspace to red, green, blue and amber channels
        hsv inputs and rgby outputs all floats between 0 and 1"""
        if s == 0.0:
            return v, v, v, v
        i = int(h*8.0) # what hue range are we in?

                                # v is top flat
        f = (h*8.0) - i         # local slope
        b = v*(1.0 - s)         # bottom flat
        d = v*(1.0 - s*f)       # downslope  
        u = v*(1.0 - s*(1.0-f)) # upslope
        i = i%8
        if i == 0:
            return v, b, b, u  # max r, a up
        if i == 1:
            return d, b, b, v  # max a, r down
        if i == 2:
            return b, u, b, v  # max a, g up
        if i == 3:
            return b, v, b, d  # max g, a down
        if i == 4:
            return b, v, u, b  # max g, b up
        if i == 5:
            return b, d, v, b  # max b, g down
        if i == 6:
            return u, b, v, b  # max b, r up
        if i == 7:
            return v, b, d, b  # max r, b down

    def hsv_to_rgby(self, h, s, v):
        """Improved implementation of hsv colorspace to red, green, blue and amber channels
        red and amber squashed into 1/3 the hue range (instead of 1/2 as in naive)
        hsv inputs and rgby outputs all floats between 0 and 1"""
        # offset h so 0 is pure red, needed to keep code pretty
        h = h - 1.0/12.0
        if h < 0:
            h += 1.0

        if s == 0.0:
            return v, v, v, v
        i = int(h*6.0) # what hue range are we in?

                                # v is top flat
        f = (h*6.0) - i         # slope for 1/6 hue range

        b = v*(1.0 - s)         # bottom flat
        d = v*(1.0 - s*f)       # downslope  
        u = v*(1.0 - s*(1.0-f)) # upslope

        i2 = int(h*12.0)        # what hue subrange are we in?
        f2 = (h*12.0) - i2      # slope for 1/12 hue range
        d2 = v*(1.0 - s*f2)       # steep downslope  
        u2 = v*(1.0 - s*(1.0-f2)) # steep upslope

        i2 = i2 % 12

        if i2 == 0:
            return d2, b, b, v  # max a, r down steep
        if i2 == 1: 
            return b, u2, b, v  # max a, g up steep
        if i2 == 2 or i2 == 3:
            return b, v, b, d   # max g, a down slow
        if i2 == 4 or i2 == 5:
            return b, v, u, b   # max g, b up slow
        if i2 == 6 or i2 == 7:
            return b, d, v, b   # max b, g down slow
        if i2 == 8 or i2 == 9:
            return u, b, v, b   # max b, r up slow
        if i2 == 10:
            return v, b, d2, b  # max r, b down steep 
        if i2 == 11:
            return v, b, b, u2  # max r, a up steep
