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
  - Subsequently turn that folder containing all the bitmap images into a single sprite image (6MB in size), including a CSS sprite sheet.
  
### Extracting ARZ and ARC
Extracting the existing Titan Quest Resources (such as the Items.arc and Text_EN.arc files) is done using the provided ArchiveTool in the Titan Quest 
Immortal Throne folder. 

Run the program in a prompt or shell:

> ArchiveTool.exe Resources\Items.arc -extract C:\ExtractToThisFolder\

The above command will extract all resources inside the packed Items.arc to the desired folder. 
The ArchiveTool usage can be further explored by simply running the program without any parameters.

The parser requires the **Text_EN.arc** and **Items.arc** to be extracted, to be used as the 2nd and 3rd parameter in the usage.
Both files can be found in the Resources folder of your TQ:IT directory.

TODO: ARZ Instructions
  
### DBR Parser
Titan Quest works with so called DBR files (Database Records). These files are basically dictionaries of all properties of whatever the file
is referencing. The file is comma separated, with the following format:

> key,value1;value2;value3,  
> key,value1,  
> key,value1

These values can thus easily be parsed into a usable dictionary or collection. It should be noted that a key, value pairing will be inconsistently present, 
meaning the parser checks for its presence and assumes all present keys, have usable values (i.e. non-zero/non-empty). 

The parser uses a constants (*constants.py*) file that contains reference materials for the currently supported results.

### Equipment, set and skill parser:
> Usage: tqdb-parser.py database-path resources-path textures-path

Parameters for the main parser:

**Required** Full path to locally extracted database.arz folder  
The parser needs the **full path** to your locally extracted database.arz folder (ex: "C:\Users\Foo\Bar\database")

**Required** Full path to locally extracted ARC resources  
The parser needs the **full path** to your locally extracted text_en.arc resources folder (ex: "C:\Users\Foo\Bar\resources")

**Required** Full path to locally extracted ARC textures  
The parser needs the **full path** to your locally extracted items.arc textures folder (ex: "C:\Users\Foo\Bar\textures")

### TextureViewer
The *tqdb-parser.py* script uses the TextureViewer program created by Max McGuire to convert the TEX files into transparent PNGs. I included the program, the DLL and the readme in its entirety in the repo.

### ReactJS Website implementation
I've currently put the JSON outputs of these parsers to use on [tq-db.net][tqdb], and will continue to develop the website over the next few weeks.

[ng]: <http://www.nordicgames.at/index.php/product/titan_quest_gold_edition>
[gb]: <http://www.gamebanshee.com/titanquest/>
[tqdb]: <http://www.tq-db.net>
