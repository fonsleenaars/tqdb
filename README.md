# TQDB
TQDB is a Python parser written for the extracted database.arz from Titan Quest: Immortal Throne, currently owned by [Nordic Games][ng].

### Titan Quest: Immortal Throne
Although the base game Titan Quest was released in 2006 and the expansion Immortal Throne in 2007, I, as many others kept playing it throughout the years. With the recent pick up by Nordic Games there are changes being made to the database that are no longer reflect in the other databases that are still around (most notably [GameBanshee][gb]).

That, and a desire to make a smoother equipment database running on some more modern technologies, prompted me to start breaking down the ARZ and ARC files that make up the in-game database for Titan Quest.

The result is a few Python files that can achieve the following results:
  - Create a single JSON file containing the data (equipment, sets, skills, boss loot, etc.) - around 2MB in size.
  - Create a single sprite image (6MB in size) along with a CSS sprite sheet containing all the graphics for the equipment available in the JSON file.

### Extracting ARZ and ARC
During this section we're going to assume the following paths for your repository and your TQ Install directory:  
`C:\tq-db`  
`C:\Steam\SteamApps\Common\Titan Quest - Anniversary Edition\`

**ARZ Database**  

1. Make sure the **data/database** directory exists in your repository.
2. Using the ARZ extractor provided in the *utils* folder, extract the database.arz found in the Database folder in your Titan Quest install directory.  

 **Source**: database.arz*  
 **Target**: data/database

**Text Resources**  

1. Make sure the **data/resources** directory exists in your repository.
2. Open up a prompt, change directory to your TQ install.
3. Run the following command:  
`ArchiveTool.exe Text\Text_EN.arc -extract C:\tq-db\data\resources`

**Textures**  

1. Make sure the following folders exist in your data directory:  
  1. data/textures/Items
  2. data/textures/XPack/Items
  3. data/textures/XPack2/Items
2. Open up a prompt, change directory to your TQ install.
3. Run the following commands:
`ArchiveTool.exe Resources\Items.arc -extract C:\tqdb\data\textures\Items`  
`ArchiveTool.exe Resources\XPack\Items.arc -extract  
C:\tqdb\data\textures\XPack\Items`  
`ArchiveTool.exe Resources\XPack2\Items.arc -extract C:\tqdb\data\textures\XPack2\Items`

### DBR Parser
Titan Quest works with so called DBR files (Database Records). These files are basically dictionaries of all properties of whatever the file
is referencing. The file is comma separated, with the following format:

> key,value1;value2;value3,  
> key,value1,  
> key,value1

These values can thus easily be parsed into a usable dictionary or collection. It should be noted that a key, value pairing will be inconsistently present, meaning the parser checks for its presence and assumes all present keys, have usable values (i.e. non-zero/non-empty).

### Equipment, set and skill parser:
> usage: run.py [-h] [-d DIR] [-c CATEGORIES [CATEGORIES ...]]
>
> TQ:IT Database parser
>
> optional arguments:
>
>  -h, --help            show this help message and exit
>
>  -d DIR, --dir DIR     Specify a file or directory to parse
>
>  -c CATEGORIES [CATEGORIES ...], --categories CATEGORIES [CATEGORIES ...]
>                        Specify the categories to parse. You can choose from:
>                        affixes, bosses, equipment, sets, skills

### TextureViewer
This parser uses the TextureViewer program created by Max McGuire to convert the TEX files into transparent PNGs. I included the program, the DLL and the readme in its entirety in the repo.

### ReactJS Website implementation
I've currently put the JSON outputs of these parsers to use on [tq-db.net][tqdb], and will continue to develop the website over the next few weeks.

[ng]: <http://www.nordicgames.at/index.php/product/titan_quest_gold_edition>
[gb]: <http://www.gamebanshee.com/titanquest/>
[tqdb]: <http://www.tq-db.net>
