Group
{
	name = "fixture"

	Variable
	{
		name = "Class"
		class = "static"
		type = "string"
		defaultValue = "LootItemTable_DynWeight"
	}

	Variable
	{
		name = "defaultWeight"
		class = "variable"
		type = "real"
	}

	Variable
	{
		name = "bellSlope"
		class = "array"
		type = "real"
	}

	Variable
	{
		name = "minItemLevelEquation"
		class = "variable"
		type = "equation"
	}

	Variable
	{
		name = "maxItemLevelEquation"
		class = "variable"
		type = "equation"
	}

	Variable
	{
		name = "targetLevelEquation"
		class = "variable"
		type = "equation"
	}

	Variable
	{
		name = "itemNames"
		class = "array"
		type = "file_dbr"
	}
}
