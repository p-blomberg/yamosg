#! /usr/bin/env python

import random, os.path
import pygame
from pygame.locals import *

SCREENRECT	 = Rect(0, 0, 640, 480)

#see if we can load more than standard BMP
if not pygame.image.get_extended():
	raise SystemExit, "Sorry, extended image module required"

def load_image(file):
	"loads an image, prepares it for play"
	file = os.path.join('data', file)
	try:
		surface = pygame.image.load(file)
	except pygame.error:
		raise SystemExit, 'Could not load image "%s" %s'%(file, pygame.get_error())
	return surface.convert()

def load_images(*files):
	imgs = []
	for file in files:
		imgs.append(load_image(file))
	return imgs

class Station(pygame.sprite.Sprite):
	def __init__(self, pos_x, pos_y):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.rect = self.image.get_rect()
		self.rect.centerx = pos_x
		self.rect.centery = pos_y
		
	def update(self, pan_x, pan_y):
		return

class Target(pygame.sprite.Sprite):
	def __init__(self, game_x, game_y, health=100):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.rect = self.image.get_rect()
		self.game_x=game_x
		self.game_y=game_y
		self.health=health
		
	def update(self, pan_x, pan_y):
		self.rect.centerx = self.game_x+pan_x
		self.rect.centery = self.game_y+pan_y

class Ship(pygame.sprite.Sprite):
	def __init__(self, pos_x=0, pos_y=0):	
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.rect = self.image.get_rect()
		self.rect.centerx = pos_x
		self.rect.centery = pos_y
	
	def update(self, pan_x, pan_y):
		self.rect.move_ip(1,0)

class Builder(pygame.sprite.DirtySprite):
	def __init__(self, target):
		pygame.sprite.DirtySprite.__init__(self, self.containers)
		self.image = target.image
		self.rect = self.image.get_rect()
		self.target = target
	
	def update(self, pan_x, pan_y):
		return

	def move(self, pos_x, pos_y):
		self.rect.centerx = pos_x
		self.rect.centery = pos_y

class Button(pygame.sprite.Sprite):
	def __init__(self, image, pos_x, pos_y, target):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.left = pos_x
		self.rect.top = pos_y
		self.target = target
	
	def update(self, pan_x, pan_y):
		return

	def check_click(self, pos):
		if self.rect.left < pos[0] and self.rect.top < pos[1] and \
			self.rect.left+self.rect.width > pos[0] and self.rect.top+self.rect.height > pos[1]:
			return True
		else:
			return False

def main(winstyle = 0):
	# Initialize pygame
	pygame.init()
	if pygame.mixer and not pygame.mixer.get_init():
		print 'Warning, no sound'
		pygame.mixer = None

	# Set the display mode
	winstyle = 0	# |FULLSCREEN
	bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
	screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

	#Load images, assign to sprite classes
	#(do this before the classes are used, after screen setup)
	Ship.image = load_image('ship.gif')
	Station.image = load_image('station.gif')
	Target.image = load_image('target.gif')
	img_button_station = load_image('button_station.gif')
	img_button_ship = load_image('button_ship.gif')

	#decorate the game window
	pygame.display.set_caption('The MOSG')
	pygame.mouse.set_visible(1)

	#create the background
	bgdtile = load_image('background.jpg')
	background = pygame.Surface((SCREENRECT.width, SCREENRECT.height-100))
	for x in range(0, SCREENRECT.width, bgdtile.get_width()):
		background.blit(bgdtile, (x, 0))
	screen.blit(background, (0,0))
	pygame.display.flip()

	# Create sprite groups
	ships = pygame.sprite.Group()
	stations = pygame.sprite.Group()
	buttons = pygame.sprite.Group()
	targets = pygame.sprite.Group()
	all = pygame.sprite.RenderUpdates()
	Ship.containers = ships, all
	Station.containers = stations, all
	Button.containers = buttons, all
	Builder.containers = all
	Target.containers = targets, all

	#Create Some Starting Values
	clock = pygame.time.Clock()

	# create Buttons
	btn_station=Button(img_button_station, 10, SCREENRECT.height-90, Station)
	btn_ship=Button(img_button_ship, 70, SCREENRECT.height-90, Ship)

	# just some variables
	panel_y=SCREENRECT.height-100
	pan_x=0
	pan_y=0

	# create target
	Target(150,150)
	Target(250,150)



	while True:

		# clear/erase the last drawn sprites
		all.clear(screen, background)

		#update all the sprites
		all.update(pan_x, pan_y)

		# get and handle input
		for event in pygame.event.get():
			if event.type == QUIT or \
				(event.type == KEYDOWN and event.key == K_ESCAPE):
					return
			if event.type == MOUSEBUTTONUP and event.button == 1:
				pan_init=None

			if event.type == MOUSEMOTION and pygame.mouse.get_pressed()[0]==True:
				# Panorate
				print 'pan!'
				print 'x:',pan_x,', y:',pan_y
				change=pygame.mouse.get_rel()
				pan_x+=change[0]
				pan_y+=change[1]
				print 'x:',pan_x,', y:',pan_y

			if event.type == MOUSEBUTTONDOWN and event.button == 1:
				# Init pan
				pan_init=pygame.mouse.get_rel()
				# Find out if click is on a button
				abuttonwasclicked=False
				for button in buttons:
					if button.check_click(pygame.mouse.get_pos()):
						abuttonwasclicked=True
						print 'a button was clicked'
						try:
							all.remove(builder)
						except NameError: pass
						builder=Builder(button.target)
						break
				if abuttonwasclicked==False:
					try:
						if pygame.mouse.get_pos()[1] < panel_y-builder.image.get_height()/2:
							builder.target(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
						else:
							print 'click in button area, but not on a button'
					except NameError: pass

		# update mouse position - draw the builder
		try:
			if pygame.mouse.get_pos()[1] < panel_y-builder.image.get_height()/2:
				builder.move(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
			else:
				# Hide the builder when cursor is over button area
				builder.move(-500,0)
		except NameError: pass

		#draw the scene
		dirty = all.draw(screen)
		pygame.display.update(dirty)

		#cap the framerate
		clock.tick(40)

#call the "main" function if running this script
if __name__ == '__main__': main()

