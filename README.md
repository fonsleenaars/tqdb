# TQDB
TQDB is a Python parser written for the extracted content of Titan Quest, currently owned by [Nordic Games][ng].

## Titan Quest
Although the base game Titan Quest was released in 2006 and the expansion Immortal Throne in 2007, I, as many others kept playing it throughout the years. With the recent pick up by Nordic Games there are changes being made to the database that are no longer reflect in the other databases that are still around (most notably [GameBanshee][gb]).

That, and a desire to create a smoother equipment database running on some more modern technologies, prompted me to start breaking down the ARZ and ARC files that make up the in-game content for Titan Quest.

The result is two files containing all in-game information:
  - A single JSON file containing the data (equipment, sets, skills, boss loot, etc.)
  - A single sprite image along with a CSS sprite sheet containing all the graphics for the equipment available in the JSON file.

## Setup
During the setup we're going to assume the following paths:
- Repository: `c:/tqdb`
- TQ Install: `c:/Steam/SteamApps/Common/Titan Quest - Anniversary Edition/`

The `data` directory needs to be created in your repository, so for this setup that would be `c:/tqdb/data`. Every time a directory needs to be created in the `data` directory, and is listed as `data/database` in the instructions, that means the full path would be: `c:/tqdb/data/database.`

### Python
Python 3.6 or higher and Pipenv are required to run this project. To get started with a clean setup, open up a shell, navigate to your local repository, and run:  
- `pipenv clean`
- `pipenv install`

### 1. ARZ Database

1. Make sure the `data/database` directory exists in your local repository.
2. Using the `ARZExtractor.exe` provided in the utils folder, extract the `database.arz` found in the `Database` folder in your Titan Quest install directory.

 **Source**: database.arz
 **Target**: data/database

### 2. Templates

1. Make sure the `data/database` directory exists in your local repository.
2. Open up a prompt, change directory to your TQ install.
3. Run the following command:  
`ArchiveTool.exe Toolset/Templates.arc -extract C:/tqdb/data/database`

### 3. Text Resources

1. Make sure the `data/resources` directory exists in your local repository.
2. Choose a language you want to extract, and create the folder for it in the `resources` directory.  
For example, english would be: `data/resources/en`.  
The available locales are:
    - `ch` - Simplified Chinese
    - `cz` - Czech
    - `de` - German
    - `en` - English
    - `es` - Spanish
    - `fr` - French
    - `it` - Italian
    - `jp` - Japanese
    - `ko` - Korean
    - `pl` - Polish
    - `ru` - Russian
    - `uk` - Ukrainian
3. Open up a prompt, change directory to your TQ install.
4. Run the following command:  
`ArchiveTool.exe Text/Text_EN.arc -extract C:/tqdb/data/resources/en`  
Replace the locale in both the arc file name and the directory to that of your choosing.

### 4. Textures

1. Make sure the following folders exist in your local repository:
  - `data/textures/Items`
  - `data/textures/XPack/Items`
  - `data/textures/XPack2/Items`
2. Open up a prompt, change directory to your TQ install.
3. Run the following commands:
    - `ArchiveTool.exe Resources/Items.arc -extract C:/tqdb/data/textures/Items`
    - `ArchiveTool.exe Resources/XPack/Items.arc -extract C:/tqdb/data/textures/XPack/Items`
    - `ArchiveTool.exe Resources/XPack2/Items.arc -extract C:/tqdb/data/textures/XPack2/Items`

### 5. Quests

1. Make sure the `data/quests` folder exists in your local repository.
2. Open up a prompt, change directory to your TQ install.
3. Run the following command:  
`ArchiveTool.exe Resources/Quests.arc -extract C:/tqdb/data/quests`

## Running the parser
`pipenv run python ./run.py` - Runs the parser with the default english locale  
`pipenv run python ./run.py --locale fr` - Runs the parser with the french locale

You can specify any of the two letter locales that are mentioned in the setup.

Running the project will take several minutes. Each time a category of work is completed a message will be printed.

Example output:
```
10:52 Parsed affixes in 3.3582386547089422 seconds.
10:54 Parsed creatures in 164.8914079976941 seconds.
10:56 Parsed equipment in 69.75900988261375 seconds.
10:56 Parsed quest rewards in 1.4686661400843093 seconds.
10:56 Parsed sets in 0.37698949130347614 seconds.
10:56 Writing output to files...
```

There will also be messages about missing tags, bitmaps, or other unexpected values found in the records. These are used for debugging purposes.

## Miscellaneous

### DBR Parser
Titan Quest works with so called DBR files (Database Records). These files are basically dictionaries of all properties of whatever the file is referencing. The file is comma separated, with the following formats:

```
key,value1;value2;value3,  
key,value1,  
key,value1  
```

These values can thus easily be parsed into a usable dictionary or collection. The keys for these files are checked based on the Template used for the DBR file, which is defined in the `templateName` key, and indirectly in its `Class` key as well.

### TextureViewer
This parser uses the TextureViewer program created by Max McGuire to convert the TEX files into transparent PNGs. I included the program, the DLL and the readme in its entirety in the repo.

### ReactJS Website implementation
I have created a React wrapper of the parsed JSON result on [tq-db.net][tqdb]. This wesite allows for some easy navigation and filtering of the data set. You can report any issues you find on the website on this repository's issue tracker.

[ng]: <https://www.nordicgames.at/index.php/product/titan_quest_gold_edition>
[gb]: <https://www.gamebanshee.com/titanquest/>
[tqdb]: <https://www.tq-db.net>
