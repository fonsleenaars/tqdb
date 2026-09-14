Group
{
	name = "fixture"

	Variable
	{
		name = "Include File"
		class = "static"
		type = "include"
		defaultValue = "database\templates\Actor.tpl"
	}

	Variable
	{
		name = "Include File"
		class = "static"
		type = "include"
		defaultValue = "database\Templates\TemplateBase\CharacterBio.tpl"
	}

	Variable
	{
		name = "Class"
		class = "static"
		type = "string"
		defaultValue = "Character"
	}

	Group
	{
		name = "nested"

		Variable
		{
			name = "charLevel"
			class = "array"
			type = "int"
		}

		Variable
		{
			name = "characterRacialProfile"
			class = "array"
			type = "string"
		}
	}
}
