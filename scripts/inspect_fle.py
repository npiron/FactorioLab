try:
    import factorio_ai_lab.fle_api as fle

    print("FLE API Imported Successfully")
    print("Attributes:", dir(fle))

    if hasattr(fle, "Prototype"):
        print("\nPrototypes:", [p for p in dir(fle.Prototype) if not p.startswith("_")])

    if hasattr(fle, "recipes"):
        print("\nRecipes found directly!")

    # Try to find a get_recipe function
    candidates = [x for x in dir(fle) if "recipe" in x.lower()]
    print("\nRecipe-related functions:", candidates)

except ImportError:
    print("Could not import factorio_ai_lab.fle_api. It might be a fake module or not installed.")
    import sys

    print("sys.path:", sys.path)
