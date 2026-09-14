Group
{
	name = "fixture"

	Variable
	{
		name = "Include File"
		class = "static"
		type = "include"
		defaultValue = "database\Templates\TemplateBase\Parameters_Character.tpl"
	}

	Variable
	{
		name = "Class"
		class = "static"
		type = "string"
		defaultValue = "LootRandomizer"
	}

	Variable
	{
		name = "FileDescription"
		class = "variable"
		type = "string"
	}

	Variable
	{
		name = "lootRandomizerName"
		class = "variable"
		type = "string"
	}

	Variable
	{
		name = "itemClassification"
		class = "picklist"
		type = "string"
	}

	Variable
	{
		name = "levelRequirement"
		class = "variable"
		type = "int"
	}
}
