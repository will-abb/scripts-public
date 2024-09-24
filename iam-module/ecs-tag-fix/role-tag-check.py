import re


def format_roles(input_file, output_file):
    with open(input_file, "r") as infile:
        lines = infile.readlines()

    output_lines = []
    current_role = None
    managed_policies = []

    role_pattern = re.compile(r"\*\*\*\* (.*)")
    policy_pattern = re.compile(r"- Managed Policy: (.*)")

    for line in lines:
        role_match = role_pattern.match(line)
        policy_match = policy_pattern.match(line)

        if role_match:
            if current_role:
                output_lines.append(f"**** {current_role}")
                output_lines.append("**** Managed Policies:")
                output_lines.extend(managed_policies)
                output_lines.append("")

            current_role = role_match.group(1).strip()
            managed_policies = []
        elif policy_match:
            managed_policies.append(f"- {policy_match.group(1).strip()}")

    if current_role:
        output_lines.append(f"**** {current_role}")
        output_lines.append("**** Managed Policies:")
        output_lines.extend(managed_policies)

    with open(output_file, "w") as outfile:
        outfile.write("\n".join(output_lines))


if __name__ == "__main__":
    input_file = "roles_policies.txt"
    output_file = "formatted_roles.md"
    format_roles(input_file, output_file)
    with open(output_file, "r") as outfile:
        print(outfile.read())
