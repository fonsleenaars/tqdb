Group
{
	name = "fixture"

	Variable
	{
		name = "Include File"
		class = "static"
		type = "include"
		defaultValue = "database\Templates\Character.tpl"
	}

	Variable
	{
		name = "Include File"
		class = "static"
		type = "include"
		defaultValue = "database\Templates\TemplateBase\MonsterSkillManager.tpl"
	}

	Variable
	{
		name = "Include File"
		class = "static"
		type = "include"
		defaultValue = "database\Templates\TemplateBase\CharacterLoot.tpl"
	}

	Variable
	{
		name = "Class"
		class = "static"
		type = "string"
		defaultValue = "Monster"
	}

	Variable
	{
		name = "FileDescription"
		class = "variable"
		type = "string"
	}

	Variable
	{
		name = "monsterClassification"
		class = "picklist"
		type = "string"
	}
}
