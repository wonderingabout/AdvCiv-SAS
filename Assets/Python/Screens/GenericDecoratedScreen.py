# ccgs: Stripped-down version of MNAI's InterfaceUtils.py
# lfgr 09/2019: Full-screen Advisors
from CvPythonExtensions import *

import CvUtil


ArtFileMgr = CyArtFileMgr()


class GenericDecoratedScreen( object ) :

	EXIT_ID = "Exit"

	def getScreen( self ) :
		raise NotImplementedError( "Subclasses of GenericAdvisor must implement getScreen()" )

	def initDimensions( self ) :
		screen = self.getScreen()

		if screen.getXResolution() > 1024 :
			self.wScreen = max( 1024, screen.getXResolution() )
			self.hScreen = max( 720, screen.getYResolution() )
			screen.setDimensions( 0, 0, self.wScreen, self.hScreen )

		self.xExitButton = self.wScreen - 30
		# ccgs: Was -42. Want it to be closer to the center of the footer.
		self.yExitButton = self.hScreen - 37

		return self.wScreen, self.hScreen # For convenience

	def addBackgroundHeaderFooter( self, szHeaderText ) :
		wScreen, hScreen = self.wScreen, self.hScreen
		screen = self.getScreen()

		self.hHeader = 55
		self.hFooter = 55
		self.yFooter = hScreen - self.hFooter
		self.yMainArea = self.hHeader
		self.hMainArea = self.hScreen - self.hHeader - self.hFooter

		# Background
		screen.addDDSGFC("BackgroundPicture",
				ArtFileMgr.getInterfaceArtInfo("SCREEN_BG_OPAQUE").getPath(),
				0, 0, wScreen, hScreen, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		self.BACKGR = "Background"

		# Header
		screen.addPanel( "TopPanel", u"", u"", True, False, 0, 0, wScreen, self.hHeader,
				PanelStyles.PANEL_STYLE_TOPBAR )
		screen.setLabel( "TitleHeader", self.BACKGR, u"<font=4>" + szHeaderText + u"</font>",
				CvUtil.FONT_CENTER_JUSTIFY, wScreen / 2, 8, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1 )

		# Footer
		screen.addPanel( "BottomPanel", u"", u"", True, False, 0, self.yFooter,
				wScreen, self.hFooter, PanelStyles.PANEL_STYLE_BOTTOMBAR )

	def addExitButton( self ) :
		screen = self.getScreen()
		szExitText = CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper()
		screen.setText( self.EXIT_ID, self.BACKGR, u"<font=4>" + szExitText + "</font>",
				CvUtil.FONT_RIGHT_JUSTIFY, self.xExitButton, self.yExitButton, 0,
				FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		screen.setActivation( self.EXIT_ID, ActivationTypes.ACTIVATE_MIMICPARENTFOCUS )
