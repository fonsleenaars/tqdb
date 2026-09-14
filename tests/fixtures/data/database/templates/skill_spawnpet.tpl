Group
{
	name = "fixture"

	Variable
	{
		name = "Include File"
		class = "static"
		type = "include"
		defaultValue = "database\Templates\TemplateBase\Skill_Base.tpl"
	}

	Variable
	{
		name = "Include File"
		class = "static"
		type = "include"
		defaultValue = "database\Templates\TemplateBase\Skill_Activated.tpl"
	}

	Variable
	{
		name = "Include File"
		class = "static"
		type = "include"
		defaultValue = "database\Templates\TemplateBase\Skill_Spawning.tpl"
	}

	Variable
	{
		name = "Class"
		class = "static"
		type = "string"
		defaultValue = "Skill_SpawnPet"
	}

	Variable
	{
		name = "FileDescription"
		class = "variable"
		type = "string"
	}

	Variable
	{
		name = "spawnObjectsTimeToLive"
		class = "array"
		type = "real"
	}
}
