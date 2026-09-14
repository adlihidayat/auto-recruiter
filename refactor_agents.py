import os

agents_dir = "apps/agents"
for root, dirs, files in os.walk(agents_dir):
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            with open(filepath, "r") as f:
                content = f.read()
            if "apps.agents.shared." in content:
                new_content = content.replace("apps.agents.shared.", "core_ai_lib.shared.")
                with open(filepath, "w") as f:
                    f.write(new_content)
                print(f"Updated {filepath}")
