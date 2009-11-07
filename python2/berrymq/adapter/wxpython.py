import wx
import wx.lib.newevent
import berrymq

(BerryMQEvent, EVT_BERRYMQ_MSG) = wx.lib.newevent.NewEvent()


class wxPythonAdapter(object):
    def __init__(self, window, id_filter):
        self.window = window
        berrymq.regist_method(id_filter, self.listener)
        print "wxPythonAdapter, %s" % id_filter
    
    def listener(self, message):
    	print message.id
        event = BerryMQEvent(id=message.id, 
                             args=message.args, kwargs=message.kwargs)
        wx.PostEvent(self.window, event)
