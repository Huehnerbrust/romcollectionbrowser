
import xbmc, xbmcgui

import util, config
from util import *

ACTION_MOVEMENT_UP = (3,)
ACTION_MOVEMENT_DOWN = (4,)
ACTION_MOVEMENT = (3, 4, 5, 6, 159, 160)

ACTION_EXIT_SCRIPT = (10,)
ACTION_CANCEL_DIALOG = ACTION_EXIT_SCRIPT + (9,)

CONTROL_BUTTON_EXIT = 5101
CONTROL_BUTTON_OK = 5300
CONTROL_BUTTON_CANCEL = 5310

CONTROL_LIST_ROMCOLLECTIONS = 5210
CONTROL_LIST_SCRAPEMODE = 5220
CONTROL_LIST_FUZZYFACTOR = 5260
CONTROL_LIST_SCRAPER1 = 5270
CONTROL_LIST_SCRAPER2 = 5280
CONTROL_LIST_SCRAPER3 = 5290


class ImportOptionsDialog(xbmcgui.WindowXMLDialog):
	
	selectedControlId = 0
	
	def __init__(self, *args, **kwargs):
		# Don't put GUI sensitive stuff here (as the xml hasn't been read yet)
		Logutil.log('init ImportOptions', util.LOG_LEVEL_INFO)
		
		self.gui = kwargs[ "gui" ]
		
		self.doModal()
		
	
	def onInit(self):
		Logutil.log('onInit ImportOptions', util.LOG_LEVEL_INFO)
		
		#Rom Collections
		romCollectionList = ['All']
		for rcId in self.gui.config.romCollections.keys():
			romCollection = self.gui.config.romCollections[rcId]
			romCollectionList.append(romCollection.name)
		self.addItemsToList(CONTROL_LIST_ROMCOLLECTIONS, romCollectionList)
		
		#Scraping modes
		options = ['Automatic: Accurate',
					'Automatic: Guess Matches',
					'Interactive: Select Matches']
		self.addItemsToList(CONTROL_LIST_SCRAPEMODE, options)

		sitesInList = self.getAvailableScrapers()
		
		self.addItemsToList(CONTROL_LIST_SCRAPER1, sitesInList)
		self.addItemsToList(CONTROL_LIST_SCRAPER2, sitesInList)
		self.addItemsToList(CONTROL_LIST_SCRAPER3, sitesInList)
		
		#set initial scraper values
		sitesInRomCollection = []
		#use scraper config of first non-MAME rom collection
		for rcId in self.gui.config.romCollections.keys():
			romCollection = self.gui.config.romCollections[rcId]
			if romCollection.name != 'MAME':
				sitesInRomCollection = romCollection.scraperSites
				break
			
		self.selectScrapersInList(sitesInRomCollection, sitesInList)
			
	
	def onAction(self, action):
		if (action.getId() in ACTION_CANCEL_DIALOG):
			self.close()
	
	
	def onClick(self, controlID):
		if (controlID == CONTROL_BUTTON_EXIT): # Close window button
			self.close()
		
		#OK
		elif (controlID == CONTROL_BUTTON_OK):
			self.close()
			self.doImport()
			#self.gui.updateDB()
		#Cancel
		elif (controlID == CONTROL_BUTTON_CANCEL):
			self.close()
		#Rom Collection list
		elif(self.selectedControlId in (5211,5212)):
			print "RC"						
			control = self.getControlById(CONTROL_LIST_ROMCOLLECTIONS)
			selectedRomCollection = str(control.getSelectedItem().getLabel())
			
			#set initial scraper values
			sitesInRomCollection = []
			#get selected Rom Collection
			for rcId in self.gui.config.romCollections.keys():
				romCollection = self.gui.config.romCollections[rcId]
				if(selectedRomCollection == 'All' and romCollection.name != 'MAME'):
					sitesInRomCollection = romCollection.scraperSites
					break
				elif romCollection.name == selectedRomCollection:
					sitesInRomCollection = romCollection.scraperSites
					break
				
			sitesInList = self.getAvailableScrapers()
			self.selectScrapersInList(sitesInRomCollection, sitesInList)
			
			
	def onFocus(self, controlId):
		self.selectedControlId = controlId
	
	
	def getControlById(self, controlId):
		try:
			control = self.getControl(controlId)
		except:
			return None
		
		return control
	
	
	def addItemsToList(self, controlId, options):
		control = self.getControlById(controlId)
		control.setVisible(1)
		control.reset()
				
		items = []
		for option in options:
			items.append(xbmcgui.ListItem(option, '', '', ''))
							
		control.addItems(items)
		
		
	def setRadioButtonValue(self, controlId, setting):
		control = self.getControlById(controlId)		
		value = self.gui.Settings.getSetting(setting).upper() == 'TRUE'
		control.setSelected(value)
	
	
	def getAvailableScrapers(self):
		#Scrapers
		sitesInList = ['None']		
		#get all scrapers
		scrapers = self.gui.config.tree.findall('Scrapers/Site')
		for scraper in scrapers:
			name = scraper.attrib.get('name')
			if(name != None):
				sitesInList.append(name)
				
		return sitesInList
	
	
	def selectScrapersInList(self, sitesInRomCollection, sitesInList):
		if(len(sitesInRomCollection) >= 1):
			self.selectScraperInList(sitesInList, sitesInRomCollection[0].name, CONTROL_LIST_SCRAPER1)			
		else:
			self.selectScraperInList(sitesInList, 'None', CONTROL_LIST_SCRAPER1)
		if(len(sitesInRomCollection) >= 2):
			self.selectScraperInList(sitesInList, sitesInRomCollection[1].name, CONTROL_LIST_SCRAPER2)
		else:
			self.selectScraperInList(sitesInList, 'None', CONTROL_LIST_SCRAPER2)
		if(len(sitesInRomCollection) >= 2):
			self.selectScraperInList(sitesInList, sitesInRomCollection[2].name, CONTROL_LIST_SCRAPER3)
		else:
			self.selectScraperInList(sitesInList, 'None', CONTROL_LIST_SCRAPER3)
			
	
	
	def selectScraperInList(self, options, siteName, controlId):
		for i in range(0, len(options)):
			option = options[i]
			if(siteName == option):
				control = self.getControlById(controlId)
				control.selectItem(i)
				break
		
			
	def doImport(self):
		
		#get selected Scraping mode
		control = self.getControlById(CONTROL_LIST_SCRAPEMODE)
		scrapingMode = control.getSelectedPosition()
		
		Logutil.log('Selected scraping mode: ' +str(scrapingMode), util.LOG_LEVEL_INFO)
		
		
		romCollections = self.setScrapersInConfig()
								
		self.gui.doImport(scrapingMode, romCollections)
		
		
	def setScrapersInConfig(self):
		
		#read selected Rom Collection
		control = self.getControlById(CONTROL_LIST_ROMCOLLECTIONS)
		romCollItem = control.getSelectedItem()
		selectedRC = romCollItem.getLabel()
		
		#TODO add id to list and select rc by id
		if(selectedRC == 'All'):		
			romCollections = self.gui.config.romCollections
		else:
			romCollections = {}
			for romCollection in self.gui.config.romCollections.values():
				if(romCollection.name == selectedRC):
					romCollections[romCollection.id] = romCollection
					break
				
		
		#TODO ignore MAME and offline scrapers
		for rcId in romCollections.keys():
			
			romCollection = self.gui.config.romCollections[rcId]
			
			try:
				platformId = config.consoleDict[romCollection.name]
			except:
				platformId = '0'
			
			sites = []
			site = self.getScraperFromConfig(CONTROL_LIST_SCRAPER1, platformId)
			if(site != None):
				sites.append(site)
			site = self.getScraperFromConfig(CONTROL_LIST_SCRAPER2, platformId)
			if(site != None):
				sites.append(site)
			site = self.getScraperFromConfig(CONTROL_LIST_SCRAPER2, platformId)
			if(site != None):
				sites.append(site)
				
			romCollection.scraperSites = sites
			romCollections[rcId] = romCollection
		
		return romCollections 
		
	
	def getScraperFromConfig(self, controlId, platformId):
		
		control = self.getControlById(controlId)
		scraperItem = control.getSelectedItem()
		scraper = scraperItem.getLabel()
		
		site, errorMsg = self.gui.config.readScraper(scraper, platformId, '', '', self.gui.config.tree)
		return site
				