import math, sys, os, json
from PIL import Image, ImageDraw



### Change these two constanta to manipulate the purpose of this program.

# Lets the program be able to be opened by itself. This will disable some automation, and you will have to copy the result and perform some checks manually.
STANDALONE_MODE = False
# A list of stuff to convert. Leave empty to convert everything. Allowed values: "sprites", "maps", "levels", "fonts", "particles", "sounds".
CONVERSION_SCOPE = []



#
#  UTILITY
#

#
#  Converts case LIKE THIS to case LikeThis.
#

def convert_pascal(line):
	return "".join(word[0].upper() + word[1:].lower() for word in line.split(" "))

#
#  Removes all preceeding whitespaces from the given line.
#

def unindent(line):
	char = 0
	while char < len(line):
		if not line[char] in [" ", "\t"]:
			return line[char:]
		char += 1

#
# Fix paths for unixlike systems
#

def fix_path(path):
	path = path.replace("\\", "/")
	if path.__contains__("data/maps"):
		path = path.replace("InTheShadowofthePyramids","InTheShadowOfThePyramids") \
			.replace("InnerSanctumoftheTemple","InnerSanctumOfTheTemple") \
			.replace("flightofthesacredibis","FlightOfTheSacredIbis") \
			.replace("DescenttotheUnderworld","DescentToTheUnderworld") \
			.replace("inundationofthenile","InundationOfTheNile") \
			.replace("danceofthecrocodiles","DanceOfTheCrocodiles") \
			.replace("RasJourneytotheWest","RasJourneyToTheWest") \
			.replace("ThePillarofOsiris","ThePillarOfOsiris") \
			.replace("ScrollofThoth","ScrollOfThoth") \
			.replace("PooloftheLotusBlossom","PoolOfTheLotusBlossom")

	return path

#
#  Takes a file from a given path and returns its contents as a list of lines.
#

def get_contents(path):
	path = fix_path(path) # MacOS hack
	file = open(path, "r")
	contents = file.read()
	file.close()
	return contents.split("\n")

#
#  Stores given data in JSON format in a given file.
#

def store_contents(path, contents):
	file = open(path, "w")
	file.write(json.dumps(contents, indent = 4))
	file.close()

#
#  Attempts to create a folder with a given name if it doesn't exist yet.
#

def try_create_dir(path):
	try:
		os.makedirs(path)
	except:
		pass

#
#  Changes i.e. "data\sprites\game\shooter.spr" to "images/game/shooter.png".
#

def resolve_path_image(path):
	return fix_path(path).replace("data/sprites", "images")[:-4] + ".png"

#
#  Changes i.e. "data\sprites\game\shooter.spr" to "sprites/game/shooter.json".
#

def resolve_path_sprite(path):
	return fix_path(path).replace("data/sprites", "sprites")[:-4] + ".json"

#
#  Changes i.e. "data\fonts\score4.font" to "fonts/score4.json".
#

def resolve_path_font(path):
	return fix_path(path).replace("data/fonts", "fonts")[:-5] + ".json"

#
#  Changes i.e. "data\sound\collapse_1.ogg" to "sounds/collapse_1.ogg".
#

def resolve_path_sound(path):
	return fix_path(path).replace("data/sound", "sounds")

#
#  If both values are identical, return that value. If not, return a random value generator dictionary, eg. {"type":"randomInt","min":1,"max":3}
#

def collapse_random_number(a, b, is_float):
	if a == b:
		return a
	else:
		return {"type":"randomFloat" if is_float else "randomInt","min":a,"max":b}

#
#  Changes i.e. "level_1_1" to "level_101".
#

def rename_level(name):
	try:
		words = name.split("_")
		a = int(words[1])
		b = int(words[2])
		return "level_" + str(a * 100 + b)
	except:
		return name



#
#  ACTUAL PROCEDURES
#

#
#  Takes images "img" (*.jpg) and "alpha" (*.tga) and returns a combined *.png file.
#

def combine_alpha(img, alpha = None):
	combine = alpha != None

	px = img.load()
	if combine:
		px_alpha = alpha.convert(mode = "L").load()

	result = Image.new("RGBA" if combine else "RGB", img.size)
	px_result = result.load()

	for i in range(img.size[0]):
		for j in range(img.size[1]):
			px_result[i, j] = (px[i, j][0], px[i, j][1], px[i, j][2], px_alpha[i, j]) if combine else (px[i, j][0], px[i, j][1], px[i, j][2])

	return result

#
#  As above, but with paths instead to save typing. WARNING: extensions are needed!
#

def combine_alpha_path(img_path, alpha_path, result_path):
	output_path = "/".join(result_path.split("/")[:-1])
	if not os.path.exists(output_path):
		os.makedirs(output_path)

	try:
		img = Image.open(fix_path(img_path))
	except:
		print("Unknown image: " + img_path)
		return False

	try:
		alpha = Image.open(fix_path(alpha_path))
	except:
		alpha = None
	combine_alpha(img, alpha).save(result_path)

	return True

#
#  As above, but these are read from a *.spr file. Also generates a sprite file.
#

def combine_alpha_sprite(sprite_path, out_sprite_path, out_image_path, internal = False):
	sprite_data = {"path":"","frame_size":{"x":1,"y":1},"states":[],"internal":internal,"batched":False}

	contents = get_contents(sprite_path)
	result = combine_alpha_path(contents[0], contents[1], out_image_path)
	if not result:
		return

	sprite_data["path"] = "/".join(out_image_path.split("/")[1:])
	sprite_data["frame_size"]["x"] = int(contents[2].split(" ")[0])
	sprite_data["frame_size"]["y"] = int(contents[2].split(" ")[1])
	for i in range(int(contents[3])):
		n = 4 + i * 2
		state = {"pos":{"x":0,"y":0},"frames":{"x":1,"y":1}}
		state["pos"]["x"] = int(contents[n + 1].split(" ")[0])
		state["pos"]["y"] = int(contents[n + 1].split(" ")[1])
		state["frames"]["x"] = int(contents[n])
		sprite_data["states"].append(state)

	# hacks for various sprites
	if sprite_path == "data/sprites/particles/speed_shot_beam.spr":
		sprite_data["states"][0]["frames"]["x"] = 1

	result_path = out_sprite_path
	output_path = "/".join(result_path.split("/")[:-1])
	if not os.path.exists(output_path):
		os.makedirs(output_path)
	store_contents(result_path, sprite_data)

#
#  Takes (path.obj) file contents and returns a list of vertices in {x:, y:} form.
#

def convert_path(contents):
	vertices = []
	vertex_order = []

	for line in contents:
		words = line.split(" ")
		if words[0] == "v":
			vertices.append({"x":float(words[1]),"y":-float(words[2]),"hidden":False})
		if words[0] == "f":
			for i in range(len(words) - 1):
				vertex_order.append(int(words[i + 1]))

	result = []
	for vertex_id in vertex_order:
		result.append(vertices[vertex_id - 1])

	result.reverse()

	return result

#
#  Takes (level_x_y.lvl) file contents and returns level data.
#

def convert_level(contents):
	level_data = {
		"map":"",
		"music":"level",
		"dangerMusic":"danger",
		"powerupGenerator":"vanilla_powerup.json",
		"gemGenerator":"vanilla_gem.json",
		"colorGeneratorNormal":"default",
		"colorGeneratorDanger":"danger",
		"matchEffect":"match",
		"objectives":[
			{
				"type": "destroyedSpheres",
				"target": 0
			}
		],
		"pathsBehavior":[
			{
				"colors":[],
				"colorStreak":0,
				"spawnRules":{"type":"waves","amount":0},
				"spawnDistance":0,
				"dangerDistance":0.75,
				"speeds":[]
			},
			{
				"colors":[],
				"colorStreak":0,
				"spawnRules":{"type":"waves","amount":0},
				"spawnDistance":0,
				"dangerDistance":0.75,
				"speeds":[]
			}
		]
	}

	viseMaxSpeed = 0
	viseMidMaxSpeed = 0
	viseMidMinSpeed = 0
	viseMinSpeed = 0
	viseSpeedMaxBzLerp = [0, 0]
	viseSpeedMidBzLerp = [0, 0]
	viseSpeedMinBzLerp = [0, 0]
	midStartDistance1 = 0
	midStartDistance2 = 0
	midEndDistance1 = 0
	midEndDistance2 = 0

	for line in contents:
		line = unindent(line)
		if line == None:
			continue
		words = line.split(" ")
		if words[0] == "mapFile":
			level_data["map"] = convert_pascal(" ".join(words[2:])[1:-1]).replace("'", "")
		if words[0][:11] == "spawnColor_" and words[2] == "true":
			level_data["pathsBehavior"][0]["colors"].append(int(words[0][11:]))
			level_data["pathsBehavior"][1]["colors"].append(int(words[0][11:]))
		if words[0] == "spawnStreak":
			level_data["pathsBehavior"][0]["colorStreak"] = min(int(words[2]) / 300, 0.45)
			level_data["pathsBehavior"][1]["colorStreak"] = min(int(words[2]) / 300, 0.45)
		if words[0] == "winCondition":
			level_data["objectives"][0]["target"] = int(words[2])
		if words[0] == "viseGroupCount":
			level_data["pathsBehavior"][0]["spawnRules"]["amount"] = int(words[2])
			level_data["pathsBehavior"][1]["spawnRules"]["amount"] = int(words[2])
		if words[0] == "viseSpawnDistance_1":
			level_data["pathsBehavior"][0]["spawnDistance"] = float(words[2])
		if words[0] == "viseSpawnDistance_2":
			level_data["pathsBehavior"][1]["spawnDistance"] = float(words[2])
		if words[0] == "viseMaxSpeed":
			viseMaxSpeed = float(words[2])
		if words[0] == "viseMidMaxSpeed":
			viseMidMaxSpeed = float(words[2])
		if words[0] == "viseMidMinSpeed":
			viseMidMinSpeed = float(words[2])
		if words[0] == "viseMinSpeed":
			viseMinSpeed = float(words[2])
		if words[0] == "viseSpeedMaxBzLerp":
			viseSpeedMaxBzLerp = [float(words[2]), float(words[3])]
		if words[0] == "viseSpeedMidBzLerp":
			viseSpeedMidBzLerp = [float(words[2]), float(words[3])]
		if words[0] == "viseSpeedMinBzLerp":
			viseSpeedMinBzLerp = [float(words[2]), float(words[3])]
		if words[0] == "midStartDistance_1":
			midStartDistance1 = float(words[2])
		if words[0] == "midStartDistance_2":
			midStartDistance2 = float(words[2])
		if words[0] == "midEndDistance_1":
			midEndDistance1 = float(words[2])
		if words[0] == "midEndDistance_2":
			midEndDistance2 = float(words[2])

	level_data["pathsBehavior"][0]["speeds"].append({"distance":0,"speed":viseMaxSpeed,"transition":{"type":"bezier","point1":viseSpeedMaxBzLerp[0],"point2":viseSpeedMaxBzLerp[1]}})
	level_data["pathsBehavior"][0]["speeds"].append({"distance":midStartDistance1,"speed":viseMidMaxSpeed,"transition":{"type":"bezier","point1":viseSpeedMidBzLerp[0],"point2":viseSpeedMidBzLerp[1]}})
	level_data["pathsBehavior"][0]["speeds"].append({"distance":midEndDistance1,"speed":viseMidMinSpeed,"transition":{"type":"bezier","point1":viseSpeedMinBzLerp[0],"point2":viseSpeedMinBzLerp[1]}})
	level_data["pathsBehavior"][0]["speeds"].append({"distance":1,"speed":viseMinSpeed})

	level_data["pathsBehavior"][1]["speeds"].append({"distance":0,"speed":viseMaxSpeed,"transition":{"type":"bezier","point1":viseSpeedMaxBzLerp[0],"point2":viseSpeedMaxBzLerp[1]}})
	level_data["pathsBehavior"][1]["speeds"].append({"distance":midStartDistance2,"speed":viseMidMaxSpeed,"transition":{"type":"bezier","point1":viseSpeedMidBzLerp[0],"point2":viseSpeedMidBzLerp[1]}})
	level_data["pathsBehavior"][1]["speeds"].append({"distance":midEndDistance2,"speed":viseMidMinSpeed,"transition":{"type":"bezier","point1":viseSpeedMinBzLerp[0],"point2":viseSpeedMinBzLerp[1]}})
	level_data["pathsBehavior"][1]["speeds"].append({"distance":1,"speed":viseMinSpeed})

	return level_data

#
#  Takes all files from given path and converts them to the Sphere Matcher Engine format. A slash after the path is important!
#

def convert_map(input_path, output_path):
	if not os.path.exists(output_path):
		os.makedirs(output_path)

	map_data = {"name":"","paths":[],"sprites":[]}

	contents = get_contents(input_path + "map.ui")

	for line in contents:
		line = unindent(line)
		if line == None:
			continue
		words = line.split(" ")

		if words[0] == "MapName":
			map_data["name"] = " ".join(words[2:])[1:-1]

		if words[0] == "Sprite":
			is_global = input_path.replace("/", "\\").lower() != ("\\".join(words[2].split("\\")[:-1]) + "\\").lower()
			sprite_name = (words[2].replace("\\", "/").replace("data/sprites", "sprites")[:-4]) if is_global else words[2].split("\\")[-1][:-4]
			if not is_global:
				combine_alpha_sprite(input_path + sprite_name + ".spr", output_path + sprite_name + ".json", output_path + sprite_name + ".png", True)
			sprite = {"x":0,"y":0,"path":sprite_name + ".json","internal":not is_global,"background":True}
			map_data["sprites"].append(sprite)

		if words[0] == "GLSprite":
			is_global = input_path.replace("/", "\\").lower() != ("\\".join(words[5].split("\\")[:-1]) + "\\").lower()
			background = words[4] == "GamePieceHShadow"
			sprite_name = (words[5].replace("\\", "/").replace("data/sprites", "sprites")[:-4]) if is_global else words[5].split("\\")[-1][:-4]
			if not is_global:
				combine_alpha_sprite(input_path + sprite_name + ".spr", output_path + sprite_name + ".json", output_path + sprite_name + ".png", True)
			sprite = {"x":int(words[2]),"y":int(words[3]),"path":sprite_name + ".json","internal":not is_global,"background":background}
			map_data["sprites"].append(sprite)

		if words[0] == "Path":
			path = convert_path(get_contents(input_path + words[2].split("\\")[-1]))
			map_data["paths"].append(path)

		if words[0] == "Node":
			map_data["paths"][int(words[2])][int(words[3])]["hidden"] = True

	store_contents(output_path + "config.json", map_data)

#
#  Takes the given path to .font file and converts it to OpenSMCE format.
#

def convert_font(input_path, output_path):
	font_data = {"type":"image","image":"","characters":{}}

	contents = get_contents(input_path)

	image_name = contents[0].replace("\\", "/").replace("data/bitmaps", "images")[:-4]
	combine_alpha_path(contents[0].replace("\\", "/"), contents[1].replace("\\", "/"), "output/" + image_name + ".png")
	font_data["image"] = image_name + ".png"

	for i in range((len(contents) - 4) // 2):
		char = contents[i * 2 + 4]
		params = contents[i * 2 + 5].split(" ")
		font_data["characters"][char] = {"offset":int(params[0]),"width":int(params[2])}

	store_contents(output_path, font_data)

#
#  Takes .ui file contents and returns UI script data. Rule tables stored separately are used to automatically fill all things that are hardcoded in the original engine.
#

def convert_ui(contents, rule_table, name = "root"):
	ui_data = {"inheritShow":True,"inheritHide":True,"type":"none","pos":{"x":0,"y":0},"alpha":1,"children":{},"animations":{},"sounds":{}}
	sub_anim_uis = {}

	child_scan = False
	child_scan_level = 0
	child_name = ""
	child_type = "none"
	child_contents = []

	for line in contents:
		line = unindent(line)
		if line == None:
			continue

		if child_scan:
			child_contents.append(line)
			if line == "{":
				child_scan_level += 1
			if line == "}":
				child_scan_level -= 1 # protection for nested children
				if child_scan_level == 0:
					child_scan = False
					if child_name == "Background":
						ui_data["children"][child_name] = {"inheritShow":True,"inheritHide":True,"type":"none","pos":{"x":0,"y":0},"alpha":1,"children":{"Background":"ui/background.json"},"animations":{},"sounds":{}}
					else:
						full_child_name = name + "." + child_name
						print(full_child_name + ":")
						print("\n".join(child_contents))
						child_data = convert_ui(child_contents, rule_table, full_child_name)
						child_data["type"] = child_type
						ui_data["children"][child_name] = child_data
			continue

		words = line.split(" ")
		if words[0] == "//":
			continue # we don't want comments

		if words[0] == "X":
			ui_data["pos"]["x"] = int(words[2])
		if words[0] == "Y":
			ui_data["pos"]["y"] = int(words[2])
		if words[0] == "AnimIn" and words[1] == "Sound":
			ui_data["sounds"]["in_"] = "sounds/" + words[3] + ".ogg"
		if words[0] == "AnimOut" and words[1] == "Sound":
			ui_data["sounds"]["out"] = "sounds/" + words[3] + ".ogg"
		if words[0] == "Depth":
			ui_data["layer"] = words[2]
		if words[0] == "Text":
			ui_data["text"] = " ".join(words[2:])[1:-1]
		if words[0] == "Sprite":
			ui_data["sprite"] = resolve_path_sprite(words[2])
		if words[0] == "Sprite2":
			ui_data["sprite"] = [ui_data["sprite"], resolve_path_sprite(words[2])]
		if words[0] == "Font":
			ui_data["font"] = resolve_path_font(words[2])
		if words[0] == "Justify":
			ui_data["align"] = {"LEFT":{"x":0,"y":0},"CENTER":{"x":0.5,"y":0},"RIGHT":{"x":1,"y":0}}[words[2]]
		if words[0] == "Smooth":
			ui_data["smooth"] = words[2] == "True"
		if words[0] == "MinX":
			ui_data["bounds"] = [int(words[2]), 0]
		if words[0] == "MaxX":
			ui_data["bounds"][1] = int(words[2])
		if words[0] == "File":
			ui_data["path"] = words[2].replace("\\", "/").replace("data/psys", "particles")[:-5] + ".json"
		if words[0] == "Child":
			if len(words) < 4:
				continue
			child_types = {
				"uiNonVisualWidget":"none",
				"uiVisualWidget":"sprite",
				"uiTextWidget":"text",
				"uiButton":"spriteButton",
				"uiToggleButton":"spriteButtonCheckbox",
				"uiSliderButton":"spriteButtonSlider",
				"uiProgressBar":"spriteProgress",
				"uiProgressBar_Giza":"spriteProgress",
				"uiParticleSystem":"particle"
			}
			if words[3] in child_types:
				child_type = child_types[words[3]]
			else:
				print("Unknown type! " + words[3])
				child_type = "none"
			child_scan = True
			child_scan_level = 0
			child_name = words[1]
			child_contents = []



		if words[0] == "SubAnimIn":
			if words[2] == "Widget":
				sub_ui = ui_data
				sub_ui_nav = words[4].split(".")[1:]
				for nav in sub_ui_nav:
					sub_ui = sub_ui["children"][nav]
				sub_anim_uis[words[1]] = sub_ui
			if words[2] == "SpriteDepth":
				sub_anim_uis[words[1]]["layer"] = words[4]
			if words[2] == "Style":
				style_types = {"AlphaFade":"fade","SpriteMask":"fade","BezierLerp":"move"}
				if words[4] in style_types:
					style_type = style_types[words[4]]
				else:
					print("Unknown style type! " + words[4])
					style_type = "none"
				sub_anim_uis[words[1]]["animations"]["in_"] = {"type":style_type}
				sub_anim_uis[words[1]]["animations"]["out"] = {} # placeholder filled later
			if words[2] == "Time":
				sub_anim_uis[words[1]]["animations"]["in_"]["time"] = int(words[4]) / 1000
			if words[2] == "Loc" and sub_anim_uis[words[1]]["animations"]["in_"]["type"] == "move":
				sub_anim_uis[words[1]]["animations"]["in_"]["startPos"] = {"x":int(words[4]),"y":int(words[5])}
				sub_anim_uis[words[1]]["animations"]["out"]["endPos"] = {"x":int(words[4]),"y":int(words[5])}
			if words[2] == "AlphaStart" and sub_anim_uis[words[1]]["animations"]["in_"]["type"] == "fade":
				sub_anim_uis[words[1]]["animations"]["in_"]["startValue"] = int(words[4]) / 255
				sub_anim_uis[words[1]]["alpha"] = int(words[4]) / 255
			if words[2] == "AlphaTarget" and sub_anim_uis[words[1]]["animations"]["in_"]["type"] == "fade":
				sub_anim_uis[words[1]]["animations"]["in_"]["endValue"] = int(words[4]) / 255
		if words[0] == "SubAnimOut":
			if words[2] == "Style":
				style_types = {"AlphaFade":"fade","SpriteMask":"fade","BezierLerp":"move"}
				if words[4] in style_types:
					style_type = style_types[words[4]]
				else:
					print("Unknown style type! " + words[4])
					style_type = "none"
				sub_anim_uis[words[1]]["animations"]["out"]["type"] = style_type
			if words[2] == "Time":
				sub_anim_uis[words[1]]["animations"]["out"]["time"] = int(words[4]) / 1000
			if words[2] == "Loc" and sub_anim_uis[words[1]]["animations"]["in_"]["type"] == "move":
				sub_anim_uis[words[1]]["animations"]["in_"]["endPos"] = {"x":int(words[4]),"y":int(words[5])}
				sub_anim_uis[words[1]]["animations"]["out"]["startPos"] = {"x":int(words[4]),"y":int(words[5])}
			if words[2] == "AlphaStart" and sub_anim_uis[words[1]]["animations"]["in_"]["type"] == "fade":
				sub_anim_uis[words[1]]["animations"]["out"]["startValue"] = int(words[4]) / 255
			if words[2] == "AlphaTarget" and sub_anim_uis[words[1]]["animations"]["in_"]["type"] == "fade":
				sub_anim_uis[words[1]]["animations"]["out"]["endValue"] = int(words[4]) / 255

	if name in rule_table:
		for key in rule_table[name]:
			ui_data[key] = rule_table[name][key]

	return ui_data

#
#  Takes .psys file contents and returns particle spawner data. THIS IS USED ONLY INTERNALLY AND THE RESULT NEEDS TO BE CHANGED TO MAKE SURE IT WORKS IN THE ENGINE???
#

def convert_psys(contents):
	particle_data = []

	spawner_name = None
	spawner_data = None
	spawner_flags = []

	lifespan_min = 0.0
	lifespan_max = 0.0
	spawn_radius_min_x = 0
	spawn_radius_min_y = 0
	spawn_radius_max_x = 0
	spawn_radius_max_y = 0
	start_vel_min_x = 0
	start_vel_min_y = 0
	start_vel_max_x = 0
	start_vel_max_y = 0
	dev_delay = 0
	dev_angle_min = 0
	dev_angle_max = 0
	emitter_vel_min_x = 0
	emitter_vel_min_y = 0
	emitter_vel_max_x = 0
	emitter_vel_max_y = 0

	for line in contents:
		line = unindent(line)
		if line == None:
			continue
		words = line.split(" ")
		if words[0] == "//":
			continue # we don't want comments

		if spawner_name == None:
			if words[0] == "Emitter":
				spawner_name = words[1]
				spawner_data = {
					"name":spawner_name,
					"pos":{"x":0,"y":0},
					"speed":{"x":0,"y":0},
					"acceleration":{"x":0,"y":0},
					"lifespan":None,
					"spawnCount":1,
					"spawnMax":1,
					"spawnDelay":None,
					"particleData":{
						"speedMode":"loose",
						"spawnScale":{"x":0,"y":0},
						"speed":{"x":0,"y":0},
						"acceleration":{"x":0,"y":0},
						"lifespan":None,
						"sprite":"",
						"animationFrameCount":1,
						"animationSpeed":0,
						"animationLoop":False,
						"animationFrameRandom":False,
						"fadeInPoint":0,
						"fadeOutPoint":1,
						"posRelative":False,
						"rainbow":False,
						"rainbowSpeed":0
					}
				}
			else:
				print("Unknown type: " + words[0])
			continue

		if words[0] == "}":
			spawner_data["particleData"]["lifespan"] = collapse_random_number(lifespan_min, lifespan_max, True)
			spawner_data["particleData"]["spawnScale"]["x"] = collapse_random_number(spawn_radius_min_x, spawn_radius_max_x, True)
			spawner_data["particleData"]["spawnScale"]["y"] = collapse_random_number(spawn_radius_min_y, spawn_radius_max_y, True)
			spawner_data["particleData"]["speed"]["x"] = collapse_random_number(start_vel_min_x, start_vel_max_x, True)
			spawner_data["particleData"]["speed"]["y"] = collapse_random_number(start_vel_min_y, start_vel_max_y, True)
			spawner_data["speed"]["x"] = collapse_random_number(emitter_vel_min_x, emitter_vel_max_x, True)
			spawner_data["speed"]["y"] = collapse_random_number(emitter_vel_min_y, emitter_vel_max_y, True)

			if "EF_LIFESPAN_INFINITE" in spawner_flags:
				spawner_data["particleData"]["lifespan"] = None
			if "EF_ELIFESPAN_INFINITE" in spawner_flags:
				spawner_data["lifespan"] = None
			if "EF_POS_RELATIVE" in spawner_flags:
				spawner_data["particleData"]["posRelative"] = True
			if "EF_VEL_POSRELATIVE" in spawner_flags:
				spawner_data["particleData"]["speedMode"] = "radius"
			if "EF_SPRITE_ANIM_LOOP" in spawner_flags:
				spawner_data["particleData"]["animationLoop"] = True
			if "EF_SPRITE_RANDOM_FRAME" in spawner_flags:
				spawner_data["particleData"]["animationFrameRandom"] = True
			if "EF_VEL_DEVIATION" in spawner_flags:
				spawner_data["particleData"]["directionDeviationTime"] = dev_delay
				spawner_data["particleData"]["directionDeviationSpeed"] = collapse_random_number(dev_angle_min / 360 * math.pi * 2, dev_angle_max / 360 * math.pi * 2, True)
			if "EF_VEL_ORBIT" in spawner_flags:
				spawner_data["particleData"]["posRelative"] = True
				spawner_data["particleData"]["speedMode"] = "circle"
				spawner_data["particleData"]["speed"] = spawner_data["particleData"]["speed"]["x"]
				spawner_data["particleData"]["acceleration"] = spawner_data["particleData"]["acceleration"]["x"]

			particle_data.append(spawner_data)
			spawner_name = None
			continue

		if words[0] == "Flags":
			spawner_flags = " ".join(words[2:]).split(" | ")
		if words[0] == "StartParticles":
			spawner_data["spawnCount"] = int(words[2])
		if words[0] == "MaxParticles":
			spawner_data["spawnMax"] = int(words[2])
		if words[0] == "ParticleRate" and float(words[2]) > 0:
			spawner_data["spawnDelay"] = 1 / float(words[2])
		if words[0] == "Sprite":
			spawner_data["particleData"]["sprite"] = resolve_path_sprite(words[2])
			sprite_contents = get_contents(words[2])
			spawner_data["particleData"]["animationFrameCount"] = int(sprite_contents[4])
		if words[0] == "Palette":
			spawner_data["particleData"]["colorPalette"] = words[2].replace("\\", "/").replace("data/bitmaps", "images")[:-4] + ".png"
		if words[0] == "ColorRate":
			if "EF_USE_COLOR_RATE" in spawner_flags:
				spawner_data["particleData"]["colorPaletteSpeed"] = 1000 / float(words[2])
		if words[0] == "AnimRate":
			spawner_data["particleData"]["animationSpeed"] = float(words[2])
		if words[0] == "FadeInEndTime":
			spawner_data["particleData"]["fadeInPoint"] = float(words[2])
		if words[0] == "FadeOutStartTime":
			spawner_data["particleData"]["fadeOutPoint"] = float(words[2])
		if words[0] == "LifespanMin":
			lifespan_min = float(words[2])
		if words[0] == "LifespanMax":
			lifespan_max = float(words[2])
		if words[0] == "PosX":
			spawner_data["pos"]["x"] = float(words[2])
		if words[0] == "PosY":
			spawner_data["pos"]["y"] = float(words[2])
		if words[0] == "SpawnRadiusMin":
			spawn_radius_min_x = float(words[2])
			spawn_radius_min_y = float(words[3])
		if words[0] == "SpawnRadiusMax":
			spawn_radius_max_x = float(words[2])
			spawn_radius_max_y = float(words[3])
		if words[0] == "StartVelMin":
			start_vel_min_x = float(words[2])
			start_vel_min_y = float(words[3])
		if words[0] == "StartVelMax":
			start_vel_max_x = float(words[2])
			start_vel_max_y = float(words[3])
		if words[0] == "Acc":
			spawner_data["particleData"]["acceleration"]["x"] = float(words[2])
			spawner_data["particleData"]["acceleration"]["y"] = float(words[3])
		if words[0] == "DevDelay":
			dev_delay = float(words[2])
		if words[0] == "DevAngle":
			dev_angle_min = float(words[2])
			dev_angle_max = float(words[3])
		if words[0] == "EmitterVelMin":
			emitter_vel_min_x = float(words[2])
			emitter_vel_min_y = float(words[3])
		if words[0] == "EmitterVelMax":
			emitter_vel_max_x = float(words[2])
			emitter_vel_max_y = float(words[3])
		if words[0] == "EmitterAcc":
			spawner_data["acceleration"]["x"] = float(words[2])
			spawner_data["acceleration"]["y"] = float(words[3])
		if words[0] == "EmitterLifespan":
			spawner_data["lifespan"] = collapse_random_number(float(words[2]), float(words[3]), True)

	return particle_data

#
#  Takes (sounds.sl3) file contents and generates sound events that can be saved.
#

def convert_sounds(contents):
	mapping = {
		"collapse_1":{"name":"sphere_destroy_1"},
		"collapse_2":{"name":"sphere_destroy_2"},
		"collapse_3":{"name":"sphere_destroy_3"},
		"collapse_4":{"name":"sphere_destroy_4"},
		"collapse_5":{"name":"sphere_destroy_5"},
		"collide_spheres_path":{"name":"sphere_group_join"},
		"collide_spheres_shot":{"name":"sphere_hit_normal"},
		"launch_sphere":{"name":"sphere_shoot_normal"},
		"click":{"name":"button_click"},
		"highlight":{"name":"button_hover"},
		"catch_coin":{"name":"collectible_catch_coin"},
		"catch_gem":{"name":"collectible_catch_gem"},
		"catch_powerup_fireball":{"name":"collectible_catch_powerup_bomb"},
		"catch_powerup_lightning":{"name":"collectible_catch_powerup_lightning"},
		"catch_powerup_wild":{"name":"collectible_catch_powerup_wild"},
		"catch_powerup_shot_speed":{"name":"collectible_catch_powerup_shotspeed"},
		"catch_powerup_color_bomb":{"name":"collectible_catch_powerup_colorbomb"},
		"collapse_scarab":{"name":"sphere_destroy_vise"},
		"launch_wild":{"name":"sphere_shoot_wild"},
		"spawn_coin":{"name":"collectible_spawn_coin"},
		"spawn_gem":{"name":"collectible_spawn_gem"},
		"spawn_powerup":{"name":"collectible_spawn_powerup"},
		"catch_powerup_reverse":{"name":"collectible_catch_powerup_reverse"},
		"catch_powerup_slow":{"name":"collectible_catch_powerup_slow"},
		"catch_powerup_stop":{"name":"collectible_catch_powerup_stop"},
		"launch_fireball":{"name":"sphere_shoot_fire"},
		"launch_lightning":{"name":"sphere_shoot_lightning"},
		"collapse_fireball":{"name":"sphere_hit_fire"},
		"warning":{"name":"warning"},
		"bonus_scarab_collapse":{"name":"bonus_scarab"},
		"bonus_scarab_move":{"name":"bonus_scarab_loop","loop":True},
		"progress_complete":{"name":"ui_progress_complete"},
		"bullet_reload":{"name":"shooter_fill"},
		"bullet_swap":{"name":"shooter_swap"},
		"level_complete":{"name":"ui_level_complete"},
		"game_over":{"name":"ui_game_over"},
		"game_win":{"name":"ui_game_win"},
		"foul":{"name":"level_lose"},
		"level_intro":{"name":"ui_level_start"},
		"dialog_extro":{"name":"ui_dialog_hide"},
		"dialog_intro":{"name":"ui_dialog_show"},
		"highscore":{"name":"ui_highscore"},
		"extra_life":{"name":"ui_extra_life"},
		"spheres_roll":{"name":"sphere_roll","loop":True},
		"stage_complete":{"name":"ui_stage_complete"},
		"spawn_new_group":{"name":"sphere_chain_spawn"},
		"new_record":{"name":"ui_level_record"},
		"score_tally":{"name":"ui_score_tally"},
		"level_advance":{"name":"level_advance"}
	}

	events = {}
	name = ""
	param_mode = False

	for line in contents:
		line = unindent(line)
		if line == None:
			continue
		words = line.split(" ")
		if words[0][:2] == "//":
			continue # we don't want comments

		if line == "{":
			param_mode = True
		elif line == "}":
			param_mode = False
		else:
			if param_mode:
				event = events[name]
				if words[0] == "volume":
					event["volume"] = float(words[2])
				else:
					print("Unknown sound parameter: " + words[0] + " in sound event: " + name)
			else:
				if not words[0] in mapping:
					print("Unknown sound event: " + words[0])
					continue
				data = mapping[words[0]]
				name = data["name"]

				event = {}
				event["path"] = resolve_path_sound(words[3])
				if "loop" in data:
					event["loop"] = data["loop"]

				events[name] = event

	events["warning_loop"] = {"path":None}

	return events

#
#  Entry point of the application.
#

def main():
	global CONVERSION_SCOPE

	# Utility (temps)

	# convert_map("data/maps/KhufusRevengest/", "output/maps/KhufusRevengest/")
	# store_contents("output/levels/khufus_revengest.json", convert_level(get_contents("data/levels/KhufusRevengest.lvl")))
	#convert_map("data/maps/Demo/", "output/maps/Demo/")
	#store_contents("output/levels/level_0_0.json", convert_level(get_contents("data/levels/level_0_0.lvl")))







	# rule_tables = json.loads("".join(get_contents("rule_tables.txt")))



	###############################################################################################   MAIN START

	# not that much of a constant? shhhhhh
	if CONVERSION_SCOPE == []:
		CONVERSION_SCOPE = ["sprites", "maps", "levels", "fonts", "particles", "sounds"]
	counter = 0



	if "sprites" in CONVERSION_SCOPE:
		counter += 1
		print("\n\n\n\nConverting sprites (" + str(counter) + "/" + str(len(CONVERSION_SCOPE)) + ")...")

		### CONVERT SPRITES
		for r, d, f in os.walk("data/sprites"):
			for directory in d:
				for r, d, f in os.walk("data/sprites/" + directory):
					for file in f:
						print(directory + "/" + file)
						sprite_path = "data/sprites/" + directory + "/" + file
						combine_alpha_sprite(sprite_path, "output/" + resolve_path_sprite(sprite_path), "output/" + resolve_path_image(sprite_path))

		# one more lone splash background is needed
		combine_alpha_path("data/bitmaps/splash/background.jpg", None, "output/images/splash/background.png")

		# and some palettes, too
		combine_alpha_path("data/bitmaps/powerups/wild_pal.jpg", None, "output/images/powerups/wild_pal.png")
		for n in ["blue", "green", "orange", "pink", "purple", "red", "yellow"]:
			combine_alpha_path("data/bitmaps/particles/gem_bloom_" + n + ".jpg", None, "output/images/particles/gem_bloom_" + n + ".png")

		# and that blinking cursor thingy
		combine_alpha_sprite("data/fonts/dialog_body_cursor.spr", "output/sprites/fonts/dialog_body_cursor.json", "output/images/fonts/dialog_body_cursor.png")

		print("Done!")



	if "maps" in CONVERSION_SCOPE:
		counter += 1
		print("\n\n\n\nConverting maps (" + str(counter) + "/" + str(len(CONVERSION_SCOPE)) + ")...")

		### CONVERT MAPS
		for r, d, f in os.walk("data/maps"):
			for directory in d:
				print(directory)
				convert_map("data/maps/" + directory + "/", "output/maps/" + directory + "/")
		print("Done!")



	if "levels" in CONVERSION_SCOPE:
		counter += 1
		print("\n\n\n\nConverting levels (" + str(counter) + "/" + str(len(CONVERSION_SCOPE)) + ")...")

		### CONVERT LEVELS
		try_create_dir("output/config/levels/")

		for r, d, f in os.walk("data/levels"):
			for file in f:
				if file == "powerups.txt":
					continue
				print(file)
				store_contents("output/config/levels/" + rename_level(file[:-4]) + ".json", convert_level(get_contents("data/levels/" + file)))
		print("Done!")



	if "fonts" in CONVERSION_SCOPE:
		counter += 1
		print("\n\n\n\nConverting fonts (" + str(counter) + "/" + str(len(CONVERSION_SCOPE)) + ")...")

		### CONVERT FONTS
		try_create_dir("output/fonts/")

		for r, d, f in os.walk("data/fonts"):
			for file in f:
				if file == "dialog_body_cursor.spr":
					continue
				print(file)
				convert_font("data/fonts/" + file, "output/fonts/" + file[:-5] + ".json")
		print("Done!")



	if "particles" in CONVERSION_SCOPE:
		counter += 1
		print("\n\n\n\nConverting particles (" + str(counter) + "/" + str(len(CONVERSION_SCOPE)) + ")...")

		### CONVERT PSYS
		try_create_dir("output/particles/")

		for n in [
			"powerup_wild","powerup_coin","powerup_lightning","powerup_reverse","powerup_slow","powerup_speed_shot","powerup_stop","powerup_bomb",
			"powerup_bomb_color_1","powerup_bomb_color_2","powerup_bomb_color_3","powerup_bomb_color_4","powerup_bomb_color_5","powerup_bomb_color_6","powerup_bomb_color_7",
			"gem_1","gem_2","gem_3","gem_4","gem_5","gem_6","gem_7","gem_8","gem_9","gem_10","gem_11","gem_12","gem_13","gem_14","gem_15",
			"collapse_ball_1","collapse_ball_2","collapse_ball_3","collapse_ball_4","collapse_ball_5","collapse_ball_6","collapse_ball_7",
			"collapse_wild","collapse_vise","extra_life","level_score","level_stat","lightning_beam","powerup_catch","warning",
			"idle_ball_bomb","idle_ball_lightning","idle_ball_wild","speed_shot_beam",
			"collapse_ball_bomb",
			"shooter1","shooter2","warning2",
			"high_score",
			"level","stage_complete","stage_complete2"
		]:
			print(n)
			store_contents("output/particles/" + n + ".json", convert_psys(get_contents("data/psys/" + n + ".psys")))



	if "sounds" in CONVERSION_SCOPE:
		counter += 1
		print("\n\n\n\nConverting sounds (" + str(counter) + "/" + str(len(CONVERSION_SCOPE)) + ")...")

		### CONVERT SOUNDS
		try_create_dir("output/sound_events/")

		events = convert_sounds(get_contents("data/sound/sounds.sl3"))

		for n in events:
			print(n)
			store_contents("output/sound_events/" + n + ".json", events[n])

	###############################################################################################   MAIN END









	### CONVERT UI (WIP)
	# for name in ["profile_dup"]:
		# # if name + ".ui" in rule_tables["ui"]:
			# # rule_table = rule_tables["ui"][name + ".ui"]
		# # else:
		# rule_table = {}
		# store_contents("output/ui/" + name + ".json", convert_ui(get_contents("data/uiscript/" + name + ".ui"), rule_table))



	#combine_alpha_path("warning.jpg", "warning_alpha.tga", "warning.png")
	#combine_alpha_path("warning2.jpg", "", "warning_gem.png")

	if STANDALONE_MODE:
		print("Everything is done!")
		input("Press ENTER...")



if STANDALONE_MODE or sys.argv[0] == "main.py":
	if sys.argv[0] == "main.py":
		# Never let the shell converter script to convert only some of the game files.
		CONVERSION_SCOPE = []
	main()
else:
	print("Could not launch the script... Probably you have launched the wrong file.")
	print("Launch convert.bat instead.")
	print()
	print("If you see this message when you've launched convert.bat,")
	print("it means there's probably a bug in either of these files.")
	print("Contact me for support, and don't forget to screenshot the following information:")
	print()
	print("sys.argv[0] = " + sys.argv[0])
	print()
	print()
	print()
	input("Press ENTER to leave this window.")
	exit(69)