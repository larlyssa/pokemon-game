import random
try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
   

WIDTH = 480
HEIGHT = 480
BORDERS = [35, 407, 59, 422]
intro_end = False
current_volume = 1.0
moving_left = False
moving_right = False

class ImageInfo:
    """
    Processes image information
    """
    def __init__(self, center, size, image, animated = False, lifespan = 0):
        self.center = center
        self.size = size
        self.image = image

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size
                          
    def draw(self, canvas, location):
        canvas.draw_image(self.image, self.center, self.size, location, self.size)

class Loader:
    """
    Slightly modified version of simplegui_lib_loader (December 12, 2013)
    Credit to Olivier Pirson for the base structure.
    http://www.opimedia.be/
    
    Help to load images and sounds from Internet
    and wait finished.
    With SimpleGUICS2Pygame,
    `SimpleGUICS2Pygame.load_image()` and `SimpleGUICS2Pygame.load_sound()`
    wait automatically until loading is completed.
    But in CodeSkulptor, the browser load images and sounds asynchronously.
    (With SimpleGUI it is **impossible to verify that the sounds are loaded**.
    So `Loader` begin load sounds, and next begin load images.
    It wait each image is loaded,
    and considers that all downloads are completed.)
    """

    _interval = 100
    """
    Interval in ms betweed two check.
    """

    def __init__(self, frame, progression_bar_width,
                 after_function, background_screen = None, max_waiting=5000):
        """
        Set an empty loader.
        :param frame: simplegui.Frame
        :param progression_bar_width: (int or float) >= 0
        :param after_function: function () -> *
        :param max_waiting: (int or float) >= 0
        """
        assert (isinstance(progression_bar_width, int)
                or isinstance(progression_bar_width, float)), \
            type(progression_bar_width)
        assert progression_bar_width >= 0, progression_bar_width

        # assert callable(after_function), type(after_function)

        self._frame = frame
        self._progression_bar_width = progression_bar_width
        self._after_function = after_function
        self._max_waiting = max_waiting
        self.background_screen = background_screen
        self._images = {}
        self._sounds = {}

        self.__max_waiting_remain_started = False

    def _draw_loading(self, canvas):
        """
        Draw waiting message on the canvas
        when images and sounds loading.
        :param canvas: simplegui.Canvas
        """
        nb = self.get_nb_images() + self.get_nb_sounds()

        size = 30
        
        canvas.draw_image(self.background_screen, [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT], [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
        if (self._progression_bar_width > 0) and (nb > 0):
            percent = (self.get_nb_images_loaded()
                       + self.get_nb_sounds_loaded())*100.0/nb

            y = 450
            canvas.draw_line((0, y),
                             (self._progression_bar_width, y), 20, 'White')
            if percent > 0:
                canvas.draw_line((0, y),
                                 (self._progression_bar_width*percent/100.0,
                                  y),
                                 20, 'Green')

        canvas.draw_text('Loading... %d%%' % int(percent),
                         (10, 430),
                         size, 'White')

        if self.__max_waiting_remain_started:
            nb = int(round(self.__max_waiting_remain/1000.0))
            canvas.draw_text('Abort after %d second%s...'
                             % (nb, ('s' if nb > 1
                                     else '')),
                             (10, 50 + size*2*3.0/4),
                             size, 'White')
                             


    def add_image(self, url, name=None):
        """
        Add an image from `url`
        and give it a name.
        **Execute `Loader.load()` before use images.**
        If `name` == `None`
        then "filename" of url is used.
        Example:
        If `url` == `'http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png'`
           and `name` == `None`
        then `'asteroid_blue.png'` is used.
        :param url: str
        :param name: None or str
        :param wait: bool
        """
        assert isinstance(url, str), type(url)
        assert (name is None) or isinstance(name, str), type(name)

        self._images[(url.split('/')[-1] if name is None
                      else name)] = url

    def add_sound(self, url, name=None):
        """
        Add a sound from `url`
        and give it a `name`.
        **Execute `Loader.load()` before use sounds.**
        If `name` == `None`
        then "filename" of `url` is used.
        Example:
        If `url` == `'http://commondatastorage.googleapis.com/codeskulptor-assets/Epoq-Lepidoptera.ogg'`
           and `name` == `None`
        then `'Epoq-Lepidoptera.ogg'` is used.
        :param url: str
        :param name: None or str
        :param wait: bool
        """
        assert isinstance(url, str), type(url)
        assert (name is None) or isinstance(name, str), type(name)

        self._sounds[(url.split('/')[-1] if name is None
                      else name)] = url

    def get_image(self, name):
        """
        If an image named `name` exist
        then return it,
        else return `None`
        :param name: str
        :raise: Exception if Loader.load() was not executed
                since the addition of this image.
        :return: None or simplegui.Image
        """
        assert isinstance(name, str), type(name)

        image = self._images.get(name)

        if isinstance(image, str):
            raise Exception(
                "load() not executed since the addition of the image '%s'!"
                % name)

        return image

    def get_nb_images(self):
        """
        Return the number of images (loaded or not).
        :return: int >= 0
        """
        return len(self._images)

    def get_nb_images_loaded(self):
        """
        Return the number of loaded images.
        It is the number of begin loading by `Loader.load()`
        **and** fully completed.
        :return: int >= 0
        """
        return len([None for name in self._images
                    if ((not isinstance(self._images[name], str))
                        and (self._images[name].get_width() > 0))])

    def get_nb_sounds(self):
        """
        Return the number of sounds (loaded or not).
        :return: int >= 0
        """
        return len(self._sounds)

    def get_nb_sounds_loaded(self):
        """
        Return the number of loaded sounds.
        It is the number of begin loading by `Loader.load()`,
        **but not necessarily completed**.
        Because with SimpleGUI of CodeSkulptor
        it is **impossible to verify that the sounds are loaded**.
        :return: int >= 0
        """
        return len([None for name in self._sounds
                    if not isinstance(self._sounds[name], str)])

    def get_sound(self, name):
        """
        If a sound named `name` exist
        then return it,
        else return `None`
        :param name: str
        :raise: Exception if load() was not executed
                since the addition of this sound.
        :return: None or simplegui.Sound
        """
        assert isinstance(name, str), type(name)

        sound = self._sounds.get(name)

        if isinstance(sound, str):
            raise Exception(
                "load() not executed since the addition of the sound '%s'!"
                % name)

        return sound

    def load(self):
        """
        **Start loading** of all images and sounds added
        since last `Loader.load()` execution.
        * In standard Python with SimpleGUICS2Pygame:
        draw a progression bar on canvas
        and wait until the loading is finished.
        * In SimpleGUI of CodeSkulptor: *don't* wait.
        """
        try:
            from simplegui import load_image, load_sound

            SIMPLEGUICS2PYGAME = False
        except ImportError:
            from SimpleGUICS2Pygame.simpleguics2pygame import load_image, \
                load_sound

            SIMPLEGUICS2PYGAME = True

        self._SIMPLEGUICS2PYGAME = SIMPLEGUICS2PYGAME

        if SIMPLEGUICS2PYGAME:
            handler_saved = self._frame._canvas._draw_handler
            self._frame._canvas._draw_handler = self._draw_loading

        for name in self._sounds:
            if SIMPLEGUICS2PYGAME:
                self._frame._canvas._draw()
            if isinstance(self._sounds[name], str):
                self._sounds[name] = load_sound(self._sounds[name])

        for name in self._images:
            if SIMPLEGUICS2PYGAME:
                self._frame._canvas._draw()
            if isinstance(self._images[name], str):
                self._images[name] = load_image(self._images[name])

        if SIMPLEGUICS2PYGAME:
            self._frame._canvas._draw()
            self._frame._canvas._draw_handler = handler_saved

    def pause_sounds(self):
        """
        Pause all sounds.
        """
        for name in self._sounds:
            if not isinstance(self._sounds[name], str):
                self._sounds[name].pause()

    def wait_loaded(self):
        """
        Draw a progression bar on canvas
        and wait until all images and sounds are fully loaded.
        Then execute `self._after_function`.
        After `self._max_waiting` milliseconds,
        abort and execute `self._after_function`.
        See details in `get_nb_sounds_loaded()` documentation.
        """
        if (((self.get_nb_images_loaded() == self.get_nb_images())
             and (self.get_nb_sounds_loaded() == self.get_nb_sounds()))
                or (self._max_waiting <= 0)):
            self._after_function()
            return

        def check_if_loaded():
            """
            If all images and sounds are loaded
            then stop waiting and execute `self._after_function`.
            """
            self.__max_waiting_remain -= Loader._interval

            if (((self.get_nb_images_loaded() == self.get_nb_images())
                 and (self.get_nb_sounds_loaded() == self.get_nb_sounds()))
                    or (self.__max_waiting_remain <= 0)):
                self.__max_waiting_remain = 0
                self.__timer.stop()
                self._frame.set_draw_handler(lambda canvas: None)

                del self.__timer

                self._after_function()

        self.__max_waiting_remain_started = True
        self.__max_waiting_remain = self._max_waiting

        try:
            from simplegui import create_timer
        except ImportError:
            from SimpleGUICS2Pygame.simpleguics2pygame import create_timer

        self._frame.set_draw_handler(self._draw_loading)
        self.__timer = create_timer(Loader._interval, check_if_loaded)
        self.__timer.start()

class Character:
    """
    Enables character movement and proper image display
    """
    def __init__(self, tiled_image, image_info, name, inventory = []):
        self.tiled_image = tiled_image
        self.image_info = image_info
        self.row_number = 0
        self.image_center = image_info.get_center()
        self.image_size = image_info.get_size()
        self.pos = [WIDTH / 2, HEIGHT / 2]
        self.vel = [0, 0]
        self.col = 0
        self.name = name
        self.inventory = inventory
    def walk_down(self):
            self.row_number = 0
            self.vel[1] = 1
    def walk_left(self):
        self.row_number = 1
        self.vel[0] = -1
    def walk_right(self):
        self.row_number = 2
        self.vel[0] = 1
        
    def walk_up(self):
        self.row_number = 3
        self.vel[1] = -1
            
    def draw(self, canvas):
        #Ensures the proper subset of the tiled image is shown based on character direction
        canvas.draw_image(self.tiled_image, [self.image_center[0] + self.image_size[0] * self.col,
                                             self.image_center[1] + self.image_size[1] * self.row_number],
                          self.image_size,
                          self.pos, [self.image_size[0] / 1.5, self.image_size[1] / 1.5])

    def update(self):
        #Keeps track of map borders and updates character position
        """
        The map borders are hardcoded seperately from the 'Building' class because
        inversing the top and the bottom borders in the class to make up for the lack
        of box shape prevents the 'if' statements from finding longitudes at which the 
        character / moving object is BETWEEN. No choice but to hardcode.
        """
        global borders
        if self.pos[1] == BORDERS[0] or self.pos[1] == BORDERS[1]:
            self.vel[1] = 0
            if self.pos[1] == BORDERS[0]:
                self.pos[1] += 1
            elif self.pos[1] == BORDERS[1]:
                self.pos[1] -= 1
        if self.pos[0] == BORDERS[2] or self.pos[0] == BORDERS[3]:
            self.vel[1] = 0
            if self.pos[0] == BORDERS[2]:
                self.pos[0] += 1
            elif self.pos[0] == BORDERS[3]:
                self.pos[0] -= 1
                
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

class Building:
    """
    Prevents the character from walking on top of buildings, trees, etc.
    """
    def __init__(self, borders, map_end = False, door = None, interactive = None, map_change_info = []):
        global character
        self.borders = borders #upper = self.borders[0], lower = self.borders[1], left = self.borders[2], right = self.borders[3]
        self.moving_object = character
        self.interactive = interactive
        self.map_end = map_end
        self.door = door
        self.map_change_info = map_change_info #map_change_info[0] = map ; map_change_info[1] = map_info ; map_change_info[2] = map_string
        
    def border_control(self):
        global latitude
        if not self.map_end:
            if (latitude == self.borders[2]) and (self.moving_object.pos[1] >= self.borders[0] and self.moving_object.pos[1] <= self.borders[1]):
                self.moving_object.vel[0] = 0
                latitude -= 1
                
            if (latitude == self.borders[3]) and (self.moving_object.pos[1] >= self.borders[0] and self.moving_object.pos[1] <= self.borders[1]):
                self.moving_object.vel[0] = 0
                latitude += 1
                
            if (self.moving_object.pos[1] == self.borders[0]) and (latitude >= self.borders[2]) and (latitude <= self.borders[3]):  
                self.moving_object.vel[1] = 0
                self.moving_object.pos[1] -= 1   
            
            if (self.moving_object.pos[1] == self.borders[1]) and (latitude >= self.borders[2]) and (latitude <= self.borders[3]):  
                self.moving_object.vel[1] = 0
                self.moving_object.pos[1] += 1             
           
        else:
            if self.moving_object.pos[0] == self.borders[2] and (self.moving_object.pos[1] >= self.borders[0] and self.moving_object.pos[1] <= self.borders[1]):
                self.moving_object.vel[0] = 0
                self.moving_object.pos[0] -= 1
                
            if (self.moving_object.pos[0] == self.borders[3]) and (self.moving_object.pos[1] >= self.borders[0] and self.moving_object.pos[1] <= self.borders[1]):
                self.moving_object.vel[0] = 0
                self.moving_object.pos[0] += 1
                
            if (self.moving_object.pos[1] == self.borders[0]) and (self.moving_object.pos[0] >= self.borders[2]) and (self.moving_object.pos[0] <= self.borders[3]):  
                self.moving_object.vel[1] = 0
                self.moving_object.pos[1] -= 1

            if (self.moving_object.pos[1] == self.borders[1]) and (self.moving_object.pos[0] >= self.borders[2]) and (self.moving_object.pos[0] <= self.borders[3]):  
                self.moving_object.vel[1] = 0
                self.moving_object.pos[1] += 1
                
    def doors(self):
        #Sets the doors of buildings to change maps or to initiate a dialogue sequence
        global latitude, background_image, background_info, current_background, current_dialog, dialog, dialog_place, l1_textscroller, l2_textscroller
        
        #If the center of the map walking into a door/event sequence
        if not self.map_end and self.door != None:			
            if (self.moving_object.pos[1] == (self.borders[1] + 1) or self.moving_object.pos[1] == (self.borders[1] - 1)) and (latitude >= self.door[0]) and (latitude <= self.door[1]):  
				
				#If not a person, change the map; otherwise initiate a dialog sequence
				if self.interactive == None:
					map_change(self.map_change_info[0], self.map_change_info[2], self.map_change_info[1], self.moving_object)
				else:
					current_dialog = Dialog(self.interactive)
		
		#If at the edge of the map walking into a door/event sequence			
        elif self.door != None:
            if (self.moving_object.pos[1] == (self.borders[1] + 1) or self.moving_object.pos[1] == (self.borders[1] - 1)) and (self.moving_object.pos[0] >= self.door[0]) and (self.moving_object.pos[0] <= self.door[1]):  
                
                #If not a person, change the map; otherwise initiate a dialog sequence
                if self.interactive == None:
                    map_change(self.map_change_info[0], self.map_change_info[2], self.map_change_info[1], self.moving_object)
                else:
					current_dialog = Dialog(self.interactive)
				
class Dialog:
    """
	Implements the usage of messages and dialogue throughout the game.
    """
    def __init__(self, dialog_list):
		global dialog_place, l1_textscroller, l2_textscroller, dialog
		self.dialog = dialog_list
		dialog = True
		for i in range(len(self.dialog)):
			if type(self.dialog[i]) is str:
				self.dialog[i] = self.dialog[i].upper()
 
    def dialog_handler(self, canvas):
		global dialog_place, l1_textscroller, l2_textscroller, name_choose, textbox_info, text_timer
		if dialog_place < len(self.dialog):
			textbox_info.draw(canvas, [WIDTH / 2, 400])
			text_timer.start()
			if type(self.dialog[dialog_place]) is str:
				canvas.draw_text(self.dialog[dialog_place][0:l1_textscroller], [30, 390], 14, "Black", "monospace")
			else:
				self.dialog[dialog_place]()
		else:
			text_timer.stop()
		if dialog_place + 1 < len(self.dialog): 
			if type(self.dialog[dialog_place]) is str:
				canvas.draw_text(self.dialog[dialog_place + 1][0:l2_textscroller], [30, 415], 14, "Black", "monospace")
			else:
				self.dialog[dialog_place]()

class Item:
	def __init__(self, name, effect, price, base_level):
		self.name = name
		self.price = price
		self.effect = effect
		self.base_level = base_level
	def __str__(self):
		return self.name
	def use(self, pokemon):
		pass
		#pokemon.effect[0] += effect[1]	
def border_control(building_set):
    #Calls border controls in the Building Limits Class
    for item in building_set:
        item.border_control()
        item.doors()

def map_change(map, map_string, map_info, moving_object):
    #Changes the background map
    global outside_location, latitude, background_image, background_info, current_background, BORDERS
    current_background = map_string
    background_image = map
    background_info = map_info
    if map_string == "map":
        latitude = background_info.center[0] + background_info.size[0]
        if outside_location[1] == 240:
            latitude = outside_location[0]
            moving_object.pos[1] = outside_location[2]
        else:
            moving_object.pos[0] = outside_location[1]
            moving_object.pos[1] = outside_location[2]
        BORDERS = [35, 407, 59, 422]
    else:
		BORDERS[0] = (HEIGHT / 2) - background_info.get_center()[1] + 80
		BORDERS[1] = background_info.get_center()[1] + (HEIGHT / 2)
		BORDERS[2] = (WIDTH / 2) - background_info.get_center()[0] + 3
		BORDERS[3] = (WIDTH / 2) + background_info.get_center()[0] - 3
		outside_location = [latitude, moving_object.pos[0], moving_object.pos[1]]
		moving_object.pos = [WIDTH / 2, background_info.center[1] + (HEIGHT / 2) - 20]
                     
def game_key_down(key):
    #Key down handler; primarily controls movement.
    global latitude, moving_left, moving_right, dialog, dialog_place, l1_textscroller, l2_textscroller, inventory_shown, buying, mart_scroll_position, master_items
    if dialog and key != simplegui.KEY_MAP['space']:
		dialog = False
    if key == simplegui.KEY_MAP['space'] and dialog:
        dialog_place += 2
        l1_textscroller = 1
        l2_textscroller = 0
    if not dialog:
		dialog_place = 0
		l1_textscroller = 1
		l2_textscroller = 0   
    if buying:
		if key == simplegui.KEY_MAP['x']:
			buying = False
		if key == simplegui.KEY_MAP['up']: #and mart_scroll_position > 0:
			mart_scroll_position -= 1
		if key == simplegui.KEY_MAP['down']: # and mart_scroll_position < len(master_items) -1:
			mart_scroll_position += 1 
    else:
		if key == simplegui.KEY_MAP['i']:
			inventory_shown = True
		if key == simplegui.KEY_MAP['left']:
			moving_left = True
			timer.start()
		elif key == simplegui.KEY_MAP['right']:
			moving_right = True
			timer.start()
		elif key == simplegui.KEY_MAP['up']:
			character.walk_up()
			timer.start()
		elif key == simplegui.KEY_MAP['down']:
			character.walk_down()  
			timer.start() 

def game_key_up(key):
    #Stops walking animation and stops movement.
    global moving_left, moving_right, inventory_shown
    if key == simplegui.KEY_MAP['i']:
		inventory_shown = False
    if key == simplegui.KEY_MAP['left']:
        moving_left = False
        timer.stop()
        character.vel[0] = 0
    if key == simplegui.KEY_MAP['right']:
        moving_right = False
        timer.stop()
        character.vel[0] = 0
    if key == simplegui.KEY_MAP['up'] or key == simplegui.KEY_MAP['down']:
        character.vel[1] = 0
        timer.stop()
        
def movement_timer():
    #Controls walking animation
    character.col += 1
    if character.col == 4:
        character.col = 0
        
def within(inp, number, num_range):
	return inp > number - num_range and inp < number + num_range

def choose_name():
	global name_choose
	name_choose = True
	
def mart_buying():
	global buying, mart_line_counter, mart_scroll_position
	mart_line_counter = 0
	mart_scroll_position = 0
	buying = True
	
def change_volume(new_vol):
    #Input handler for the volume changer
    global current_sound, current_volume
    current_volume = float(new_vol) / 10
    current_sound.set_volume(current_volume)

def game_draw(canvas):
    #Decides between map scrolling and character movement based on character position.
    #Also controls display of text and images
    global latitude, moving_left, moving_right, current_background, dialog, current_dialog, text_timer, dialog_place, inventory_shown, buying, master_items
    global mart_scroll_position, mart_line_counter
    #Displays the current map and coordinates
    if current_background == "map":    
        canvas.draw_image(background_image, [latitude, background_info.center[1]], 
                          background_info.get_size(), background_info.get_center(), background_info.get_size())
    else:
        background_info.draw(canvas, [WIDTH / 2, HEIGHT / 2])
    
    canvas.draw_text("Pos: (" + str(character.pos[0]) + ", " + str(character.pos[1]) + ") , Latitude: " + str(latitude), [125, 460], 28, "White")
    
    #Draws and updates the location and orientation of the character
    character.draw(canvas)
    character.update()
    
    if dialog:
        current_dialog.dialog_handler(canvas)
        text_timer.start()
    
    #Controls whether the character moves itself or the map scrolls
    if moving_left and (latitude > background_info.center[0]) and (character.pos[0] == WIDTH / 2 or character.pos[0] == WIDTH / 2 - 1) and (current_background == "map"):
        latitude -= 1
        character.vel[0] = 0
        character.row_number = 1
    
    elif moving_right and (latitude < (background_info.center[0] + background_info.size[0])) and (character.pos[0] == WIDTH / 2 or character.pos[0] == WIDTH / 2 - 1) and (current_background == "map"):
        latitude += 1
        character.row_number = 2
        character.vel[0] = 0
    
    elif moving_left:
        character.walk_left()
    
    elif moving_right:
        character.walk_right()
    
    #Controls the appearance of the inventory
    if inventory_shown:
		canvas.draw_polygon([(300, 20), (460, 20), (460, 460), (300, 460)], 6, "Black", "White")
		canvas.draw_text("INVENTORY:", (310, 45), 20, "Black", 'monospace')
		for i in range(len(character.inventory)):
			canvas.draw_text(character.inventory[i][0], (310, 70 + 20 * i), 14, "Black", 'monospace')
			canvas.draw_text(str(character.inventory[i][1]), (430, 70 + 20 * i), 14, "Black", 'monospace')
	
    if buying:
		canvas.draw_polygon([(300, 20), (460, 20), (460, 460), (300, 460)], 6, "Black", "White")
		canvas.draw_text("Mart:", (310, 45), 20, "Black", 'monospace')
		for item in master_items:
			canvas.draw_text(str(item), (310, 70 + 20 * mart_line_counter), 14, "Black", 'monospace')
			canvas.draw_text(str(item.price), (415, 70 + 20 * mart_line_counter), 14, "Black", 'monospace')
			mart_line_counter += 1
		canvas.draw_polygon([(310, 55 + mart_scroll_position * 20), (450, 55 + mart_scroll_position * 20), (450, 75 + mart_scroll_position * 20), (310, 75 + mart_scroll_position * 20)], 4, "Black")
    #Controls the borders of objects on screen
    if current_background == "map":    
        border_control(map_building_set)
    elif current_background == "center":
        border_control(center_building_set)
    elif current_background == "mart":
        border_control(mart_building_set)
    elif current_background == "gym":
		border_control(gym_building_set)
    elif current_background == "house":
        border_control(house_building_set)

def game_init():
	"""
    Initializes the game itself after character creation
    """
    #initialize globals 
	global character, map_info, character_info, pkcmap_info, pokemart_info, current_volume, inventory_shown
	global map_building_set, center_building_set, dialog, gym_building_set, house_building_set, buying
	global mart_building_set, current_background, background_image, BORDERS, name, master_items
	global background_info, current_sound, latitude, outside_location, timer, name, gymmap_info
	
	#initializes the master list of items
	potion = Item("Potion", ("health", 20), 300, 0)
	super_potion = Item("Super Potion", ("health", 50), 700, 12)
	pokeball = Item("Pokeball", ("capture", 1), 200, 0)
	great_ball = Item("Great Ball", ("capture", 2), 600, 12)
	hyper_potion = Item("Hyper Potion", ("health", 70), 1200, 23)
	revive = Item("Revive", ("revive", .5), 1500, 25)
	max_revive = Item("Max Revive", ("revive", 1), 2000, 30)
	master_items = [potion, super_potion, hyper_potion, revive, max_revive, pokeball, great_ball]
						
    #initializes the ImageInfo classes of the images
	map_info = ImageInfo([240, 240], [480, 480], game_loader.get_image("map_image"))
	character_info = ImageInfo([32, 32], [64, 64], game_loader.get_image("character_image"))	
	pkcmap_info = ImageInfo([325 / 2, 295 / 2], [325, 295], game_loader.get_image("pokecenter_map"))
	pokemart_info = ImageInfo([352 / 2, 264 / 2], [352, 264], game_loader.get_image("pokemart_map"))
	gymmap_info = ImageInfo([289 / 2, 256 / 2], [289, 256], game_loader.get_image("gym map"))
	house_info = ImageInfo([354 / 2, 270 / 2], [354, 270], game_loader.get_image("house"))
	
	#Creates the character
	character = Character(game_loader.get_image("character_image"), character_info, name)

	#Buildings on the main map
	four_trees = Building([BORDERS[0], 138, 375, 490])
	pokecenter = Building([69, 172, 541, 658], False, [585, 593], None, [game_loader.get_image("pokecenter_map"), pkcmap_info, "center"])
	house = Building([236, 348, 541, 661], False, [616, 625], None , [game_loader.get_image("house"), house_info, "house"])
	gym = Building([247, 357, 265, 410], True, [342, 353], None, [game_loader.get_image("gym map"), gymmap_info, "gym"])
	pokemart = Building([81, 178, 277, 397], True, [321, 331], None, [game_loader.get_image("pokemart_map"), pokemart_info, "mart"])
	sign = Building([196, 236, 108, 157], True, [108, 157], ["Beware of the tall grass,", "it may be hiding wild pokemon!"])
	map_building_set = set([four_trees, pokecenter, house, gym, pokemart, sign])

	#Pokecenter Buildings
	center_counter = Building([BORDERS[0], 214, 103, 345], True, [215, 232], ["Welcome to the Pokemon Center!", "Come back when you have pokemon,", "and I can help them!"])
	center_exit = Building([370, 370, 203, 243], True, [203, 243], None, [game_loader.get_image("map_image"), map_info, "map"])
	center_pc = Building([BORDERS[0], 174, 346, 361], True, [346, 361], ["Welcome to the Pokemon Center PC.", "Please come back when you have pokemon.", "Then I can store them!"])
	center_building_set = set([center_counter, center_exit, center_pc])

	#Pokemart Buildings
	mart_table = Building([274, 323, 87, 169], True)
	mart_counter = Building([BORDERS[0], 258, BORDERS[2], 203], True, [137, 151], ["What would you like to buy?", mart_buying])
	mart_exit = Building([353, 353, 221, 259], True, [221, 259], None, [game_loader.get_image("map_image"), map_info, "map"])
	mart_shelves = Building([204, 321, 376, BORDERS[3]], True)
	mart_building_set = set([mart_table, mart_counter, mart_exit, mart_shelves])	
	
	#Gym buildings
	gym_exit = Building([350, 350, 200, 278], True, [200, 259], None, [game_loader.get_image("map_image"), map_info, "map"])
	gym_stair1 = Building([BORDERS[0], 230, 150, 200], True)
	gym_stair2 = Building([BORDERS[0], 230, 280, 328], True)
	norman = Building([193, 196, 234, 246], True, [234, 246], ["Hello " + name + ".", "Come back when you're stronger.", "Then you can battle me!"])
	gym_building_set = [gym_exit, gym_stair1, gym_stair2, norman]	
	
	#House buildings
	house_exit = Building([356, 356, 221, 264], True, [221, 264], None, [game_loader.get_image("map_image"), map_info, "map"])
	ruby = Building([219, 276, 213, 266], True, [213, 266], ["Hi " + name + "! I'm Ruby!"])
	house_table = Building([222, 301, 300, 378], True)
	house_chairs = Building([220, 300, 383, 411], True)
	house_building_set = [house_exit, ruby, house_table, house_chairs]
		
	#Creates the timer
	timer = simplegui.create_timer(150, movement_timer)
	
	#initializes the background image/music
	current_background = "map"
	background_image = game_loader.get_image("map_image")
	background_info = map_info
	current_sound.pause()
	current_sound = game_loader.get_sound("littleroot_theme")
	current_sound.play()
	current_sound.set_volume(current_volume)
	
	#Tracks the placement of the background image for map scrolling
	latitude = background_info.center[0] + background_info.size[0]

	#tracks location of the character while inside a building
	outside_location = [latitude, WIDTH / 2, HEIGHT / 2]

	#Asserts that a dialog box, inventory screen, buying screen, etc. will be shown at initialization
	dialog = False
	inventory_shown = False
	buying = False
	
	#Sets the handlers
	frame.set_draw_handler(game_draw)
	frame.set_keydown_handler(game_key_down)
	frame.set_keyup_handler(game_key_up)
          
def name_inp_handler(input):
  #Controls name input during character creation
	global name, dialog_place, l1_textscroller, l2_textscroller, name_choose
	name = input
	dialog_place += 2
	l1_textscroller = 0
	l2_textscroller = 0
	name_choose = False

def text_timer():
    #every tick add another letter to animate the textboxes
    global l1_textscroller, dialog_place, l2_textscroller
    if dialog_place < len(current_dialog.dialog):
		if type(current_dialog.dialog[dialog_place]) is str:
			if l1_textscroller <= len(current_dialog.dialog[dialog_place]):
				l1_textscroller += 1
            
    if dialog_place + 1 < len(current_dialog.dialog) and l1_textscroller >= len(current_dialog.dialog[dialog_place]):
        if type(current_dialog.dialog[dialog_place + 1]) == str:
            if l2_textscroller <= len(current_dialog.dialog[dialog_place + 1]):
                l2_textscroller += 1

def intro_keydown(key):	
    #Keydown Handler
    global dialog_place, l1_textscroller, l2_textscroller, name_choose, name, intro_dialog, intro_end, current_volume
    if name_choose:
        if key == simplegui.KEY_MAP['down']:
            intro_dialog.append("NICE TO MEET YOU " + name + "!")
            intro_dialog.append("GET READY TO ENTER THE WORLD OF POKEMON!")
            dialog_place += 1
            l1_textscroller = 0
            l2_textscroller = 0
            name_choose = False
            intro_end = True
        else:
			name += chr(key).upper()
    if key == simplegui.KEY_MAP['space']:
		Abutton = intro_loader.get_sound("A-button")
		Abutton.set_volume(current_volume)
		Abutton.play()
		if intro_end:
		  #Stops the intro and loads the main game
			game_loader.add_image("http://i.imgur.com/AOGtJXY.jpg", "map_image")
			game_loader.add_image("http://i.imgur.com/X7rwD5S.png", "character_image")
			game_loader.add_image("http://i.imgur.com/S55Faqx.jpg", "pokecenter_map")
			game_loader.add_image("http://i.imgur.com/CAlO95H.png", "pokemart_map")
			game_loader.add_image("http://i.imgur.com/TmLgJHG.png", "gym map")
			game_loader.add_image("http://i.imgur.com/uo8KFqZ.png", "house")
			game_loader.add_sound("https://www.dropbox.com/s/jus36w1y0sfjukr/Littleroot.ogg?dl=1", "littleroot_theme")
			text_timer.stop()
			game_loader.load()
			game_loader.wait_loaded()
        
		else:

			if dialog_place + 1 < len(current_dialog.dialog):
				if l1_textscroller < len(current_dialog.dialog[dialog_place]) or l2_textscroller <= len(current_dialog.dialog[dialog_place + 1]):
					l1_textscroller = len(current_dialog.dialog[dialog_place]) - 1
					l2_textscroller = len(current_dialog.dialog[dialog_place + 1]) - 1
				else:
					dialog_place += 2
					l1_textscroller = 0
					l2_textscroller = 0

def intro_draw(canvas):
    #Draw handler during the intro
    global background_info, introimg_info, textbox_info, explosion_info
    background_info.draw(canvas, [WIDTH / 2, HEIGHT / 2])
    current_dialog.dialog_handler(canvas)
    if name_choose:
		canvas.draw_text(name, [30, 390], 14, "black", "monospace")

def intro_init():
    #Initializes the introduction
    global current_background,  background_image, background_info, introduction_image, intro_end, name, current_dialog
    global introimg_info, textbox_info, explosion_info, dialog_place, l1_textscroller, l2_textscroller, name_choose
    global text_timer, intro_dialog, current_sound, name, current_volume
    introimg_info = ImageInfo([WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT], intro_loader.get_image("introduction_image"))
    textbox_info = ImageInfo([460 / 2, 83 / 2], [460, 83], intro_loader.get_image("textbox_image"))
    explosion_info = ImageInfo([64, 64], [128, 128], intro_loader.get_image("explosion_image"), True, 24)
    
    current_background = "intro"
    background_image = intro_loader.get_image("introduction_image")
    background_info = introimg_info
    
    dialog_place = 0
    l1_textscroller = 1
    l2_textscroller = 0
    name_choose = False   
    name = ""
    text_timer = simplegui.create_timer(20, text_timer)
    text_timer.start()
    
    intro_dialog = ["hi! sorry to keep you waiting.",
               'welcome to the world of pokemon!',
               'my name is professor birch.',
               'but everyone calls me the pokemon professor.',
               'this is what we call a "pokemon".',
               'this world is widely inhabited by creatures known',
               'as pokemon.',
               'it is my job to research them in order to uncover',
               'their secrets.',
               "and what about you?",
               "What's your name?",
               "(Type then press the down arrow to continue)",
               choose_name]
    
    #Sets intial dialog and sounds          
    current_dialog = Dialog(intro_dialog)
    current_sound = intro_loader.get_sound("Welcome") 
    current_sound.set_volume(current_volume)
    current_sound.play()
    #Adds a volume manager
    frame.add_input("Change Volume (0 to 10):", change_volume, 50)
        
    frame.set_draw_handler(intro_draw)
    frame.set_keydown_handler(intro_keydown)

#Creates the window
frame = simplegui.create_frame("Pokemon Emerald", WIDTH, HEIGHT)

title_screen = simplegui.load_image("http://i.imgur.com/9usiau1.jpg")

background_image = title_screen

#loading screen
game_loader = Loader(frame, WIDTH, game_init, background_image)
intro_loader = Loader(frame, WIDTH, intro_init, background_image)

#Loads images for the Introduction
intro_loader.add_image("http://i.imgur.com/t4qlRQW.jpg", "introduction_image")
intro_loader.add_image("http://i.imgur.com/mCAOj2C.jpg", "textbox_image")
intro_loader.add_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png", "explosion_image")
intro_loader.add_sound("https://www.dropbox.com/s/i2rvb057eb0c3ed/A-Button.ogg?dl=1", "A-button")
intro_loader.add_sound("https://www.dropbox.com/s/gy2q2egsc5n8m8e/Intro.ogg?dl=1", "Welcome")

#Start the loading sequence for the Introduction
intro_loader.load()
intro_loader.wait_loaded()

#Starts the frame
frame.start()
