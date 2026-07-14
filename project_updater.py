import sys, re, typing, json

def load_project(filename:str) -> dict[str, dict[str, str]]:
    data, section, key = {}, None, None
    with open(filename, 'r') as fi:
        for line in fi.readlines():
            if re.match(r"^\[[^\]\n]+\]\n", line):
                section = line.strip()
                data[section] = {}
            elif re.match(r"^[\w]+[ ]{1}\=", line):
                key, line = line.split("=", 1)
                key = key.strip()
                data[section][key] = line
            else:
                data[section][key] += line
    for s in data:
        for k in data[s]:
            data[s][k] = data[s][k].strip()
    return data

def save_project(filename:str, data:dict[str, dict[str, str]]):
    parts = []
    for section_name in data:
        item = f'{section_name}\n'
        for key in data[section_name]:
            item += f'{key} = {data[section_name][key]}\n'
        parts.append(item)
    with open(filename, 'w') as fo:
        fo.write("\n".join(parts))

def with_project(filename, callback:typing.Callable[[dict[str, dict[str, str]]],None]):
    data = load_project(filename)
    callback(data)
    save_project(filename, data)

script, *argv = sys.argv
parameters = {
    i.split("=", 1)[0]:i.split("=", 1)[1] 
    for i in sys.argv if len(i.split("=", 1)) == 2
}

print(parameters)
def with_dict_data(
        src:dict[str, dict[str, str]],
        section_name:str, key:str, callback:typing.Callable[[typing.Any], typing.Any]):
    section = src.get(section_name, {})
    data = section.get(key)
    is_json = True
    try:
        data = json.loads(data)
    except:
        is_json = False
    data = callback(data)
    if is_json:
        data = json.dumps(data)
    section[key] = data

def main(data:dict[str, dict[str, str]]):
    for parameter in parameters:
        match parameter:
            case "set-version-patch":
                def set_version_patch(raw_version):
                    version = raw_version.split(".")
                    version[-1] = parameters[parameter]
                    return ".".join(version)
                with_dict_data(data, "[project]", "version", set_version_patch)

if "file" in parameters:
    with_project(parameters["file"], main)