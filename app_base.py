import sys
import os

import wx

# displayhook to avoid etting global underscore to the value of the last expression
def _displayhook(value):
    if value is not None:
        print(repr(value))

# Map the underscore function to wx.GetTranslation
import builtins
builtins.__dict__["_"] = wx.GetTranslation

import app_const as appC

from wx.lib.mixins.inspection import InspectionMixin

class AppBase(wx.App, InspectionMixin):
    def OnInit(self):
        self.Init()
        sys.displayhook = _displayhook

        self.appName = "Logic Simulatorinator"

        self.doConfig()

        self.locale = None # Initialise to None
        wx.Locale.AddCatalogLookupPathPrefix('locale') # Look up file folder "locale"

        # Check LANG environment variable
        lang_env = os.environ.get('LANG')
        lang_code = None
        
        if lang_env:
            lang_code = lang_env.split("_")[0]
        else:
            pass
        
        # Change language
        if lang_code:
            self.updateLang(lang_code)
            self.appConfig.write(key=u'Language', value=lang_code)
            self.appConfig.Flush()
        else:
            self.updateLang(self.appConfig.Read(u"Language"))

        return True
    
    def doConfig(self):
        '''Setup application configuration file'''
        sp = wx.StandardPaths.Get()
        self.configLoc = sp.GetUserConfigDir() # # return the directory of user config
        self.configLoc = os.path.join(self.configLoc, self.appName)

        if not os.path.exists(self.configLoc):
            os.mkdir(self.configLoc)

        # AppConfig
        self.appConfig = wx.FileConfig(appName=self.appName,
                                       vendorName=u'GF2_group8',
                                       localFilename=os.path.join(
                                       self.configLoc, "AppConfig"))
        
        lang_env = os.environ.get('LANG')
        lang_code = None
        
        if lang_env:
            lang_code = lang_env.split("_")[0]
            self.appConfig.Write(key=u'Language', value=lang_code)
        else:
            # default to English if LANG is not set
            self.appConfig.Write(key=u'Language', value=u'en')
        
        def updateLang(self, lang_code):
            """Update the language of the application."""
            if lang_code in appC.supLang:
                selLang = appC.supLang[lang]

                wx.MessageBox(_("Language changed to %s") % lang_code, _("Info"))
            else:
                selLang = wx.LANGUAGE_ENGLISH
                wx.MessageBox(_("Language %s is not supported, defaulted to English.") % lang_code, _("Error"))
            
            self.locale = wx.Locale(selLang)
            if self.locale.IsOk():
                self.locale.AddCatalog(appC.langDomain)
            else:
                self.locale = None
        

