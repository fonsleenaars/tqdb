# TQDB
TQDB is a Python parser written for the extracted database.arz from Titan Quest: Immortal Throne, currently owned by [Nordic Games][ng].
My python is a bit rusty so please feel free to PR any and all mistakes or bad practices I've implemented. If you have any suggestions 
for further info to extract from Titan Quest I look forward to discussing those. 

### Titan Quest: Immortal Throne
Although the base game Titan Quest was released in 2006 and the expansion Immortal Throne in 2007, I, as many others kept playing it throughout
the years. With the recent pick up by Nordic Games there are changes being made to the database that are no longer reflect in the other databases 
that are still around (most notably [GameBanshee][gb]).

That, and a desire to make a smoother equipment database running on some more modern technologies, prompted me to start breaking down the ARZ and ARC 
files that make up the in-game database for Titan Quest.

The result is a few Python files that can achieve the following results:
  - Create a single JSON file containing all the **equipment data** (armor, weapons, relics, artifacts) - around 1MB in size.
  - Create a single JSON file containing all the **set data** (name, bonuses, set members) - around 70KB in size.
  - Create a single JSON file containing all the **skill data** (masteries, pet skills, mob skills) - around 1MB in size.
  - Create a folder containing all the bitmap images of the above listed equipment data
  - Subsequently turn that folder containing all the bitmap images into a single sprite image (5MB in size), including a CSS sprite sheet.
  
### Extracting ARZ and ARC
TODO: Instructions
  
### DBR Parser
Titan Quest works with so called DBR files (Database Records). These files are basically dictionaries of all properties of whatever the file
is referencing. The file is comma separated, with the following format:

> key,value1;value2;value3,  
> key,value1,  
> key,value1

These values can thus easily be parsed into a usable dictionary or collection. It should be noted that a key, value pairing will be inconsistently present, 
meaning the parser checks for its presence and assumes all present keys, have usable values (i.e. non-zero/non-empty). 

The parser file has its own lists that it uses as reference materials for the currently supported results, you'll see those listed at the top of *dbr_parser.py*

### Supporting JSON files
I currently have a script that needs to be run before all the others, that generates some supporting JSON \(*tqdb-support-json.py*\). 
This file requires the extracted resource: text_en.arc from the Resources folder in your Titan Quest: Immortal Throne folder. 

Run this file once before running the main parser. This python script will generate the following files, to be used by the equipment parser:
  - sets.json
  - tags.json
  - skills.json
 
The only unmentioned JSON here is the **tags.json** which contains a reference list for all the tags that are used to identify unique equipment, sets, and more
that are used in the DBR files.

### Main equipment and set parser
Parameters for the main parser:

**Required** Full path to locally extracted database.arz folder
The main parser (*tqdb-parser.py*) needs the **full path** to your locally extracted database.arz folder (ex: "C:\Users\Foo\Bar\database") as its first parameter

**Optional (-rarity)** Comma separated list of the classifications you want to output (Rare,Epic,Legendary are default)

**Optional (-bitmap)** Full path to locally extracted Items.arc folder (from Titan Quest Immortal Throne/Resources) 

### Sprite creator (CSS and single PNG file)
The last script (*tqdb-sprite.py*) will take the **full path** to the newly created bitmap folder (currently set to "uibitmaps") and create a single
PNG from it, ordered by texture sizes (ex 32x32, 64x64). It will create a sprite.css file alongside it, that has a reference to the tags of the equipment names.

### TextureViewer
The *tqdb-parser.py* script uses the TextureViewer program created by Max McGuire in case the -bitmap option is specified. I included the program, the DLL and the
readme in its entirey in the repo.

### ReactJS Website implementation
I've currently put the JSON outputs of these parsers to use on [tqdb][tq-db.net], and will continue to develop the website over the next few weeks.

[ng]: <http://www.nordicgames.at/index.php/product/titan_quest_gold_edition>
[gb]: <http://www.gamebanshee.com/titanquest/>
[tqdb]: <http://www.tq-db.net>
