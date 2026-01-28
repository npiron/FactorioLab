import sys
import os
import json

# Ensure we can import modules from src
sys.path.append(os.path.join(os.getcwd(), "src"))

from factorio_ai_lab.env_adapter import FleEnv


def dump_recipes():
    print("🚀 Connecting to FLE to dump recipes...")
    env = FleEnv(instance_id=0)
    try:
        env.reset(soft=True)
    except Exception as e:
        print(f"Reset warning (ignorable): {e}")

    # Lua script to dump game.recipe_prototypes
    lua_script = """
    local recipes = {}
    for name, proto in pairs(game.recipe_prototypes) do
        local ingredients = {}
        for _, ing in pairs(proto.ingredients) do
            table.insert(ingredients, {name=ing.name, amount=ing.amount, type=ing.type})
        end
        
        local products = {}
        for _, prod in pairs(proto.products) do
             table.insert(products, {name=prod.name, amount=prod.amount, type=prod.type})
        end

        recipes[name] = {
            category = proto.category,
            ingredients = ingredients,
            products = products,
            order = proto.order,
            hidden = proto.hidden,
            enabled = proto.enabled
        }
    end
    rcon.print(game.table_to_json(recipes))
    """

    try:
        rcon_client = env.instance.rcon_client
        print("📡 Sending dump command...")
        # Wrap in /sc for silent execution of the block, but rcon.print will output to console
        response = rcon_client.send_command(f"/sc {lua_script}")

        result_stdout = str(response)
        print(f"📨 Response Length: {len(result_stdout)}")

        if len(result_stdout) < 100:
            print(f"⚠️ Warning: Short response: {result_stdout}")

    except Exception as e:
        print(f"⚠️ Error sending RCON command: {e}")
        return

    try:
        raw_json = result_stdout.strip()
        # Find start and end of JSON { }
        start = raw_json.find("{")
        end = raw_json.rfind("}") + 1

        if start == -1 or end == 0:
            print(f"❌ Could not find JSON in output: {raw_json[:200]}...")
            return

        json_str = raw_json[start:end]
        data = json.loads(json_str)

        output_path = "data/knowledge/full_recipes.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        final_db = {"recipes": data}
        with open(output_path, "w") as f:
            json.dump(final_db, f, indent=2)

        print(f"✅ Successfully dumped {len(data)} recipes to {output_path}")

    except Exception as e:
        print(f"❌ Failed to parse output: {e}")


if __name__ == "__main__":
    dump_recipes()
