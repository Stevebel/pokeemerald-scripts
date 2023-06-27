from os import path
from pycparser import parse_file, c_generator
from config import get_base_dir
import re
import shutil

class Species:
    def __init__(self, species, name, cry, cry_reverse):
        self.species = species
        self.name = name
        self.cry = cry
        self.cry_reverse = cry_reverse
        self.modified = False

def get_species_names_and_constants(file_name):
    species = []
    with open(file_name, 'r') as f:
        for line in f:
            match = re.match(r'\s*\[SPECIES_(\w+)\] = _\("(.*)"\)', line)
            if match and match.group(1) != "NONE":
                species.append((match.group(1), match.group(2)))
            elif len(species) > 0:  # To avoid breaking on initial non-matching lines
                break
    return species

def get_cries(file_name):
    cries = []
    with open(file_name, 'r') as f:
        # Skip lines until we reach the gCryTable section
        for line in f:
            if 'gCryTable::' in line:
                break

        # Read the cry names in the gCryTable section
        for line in f:
            match = re.match(r'\s*cry Cry_(\w+)', line)
            if match:
                cries.append(match.group(1))
            else:
                break

    return cries

def get_reverse_cries(file_name):
    cries_reverse = []
    with open(file_name, 'r') as f:
        # Skip lines until we reach the gCryTable_Reverse section
        for line in f:
            if 'gCryTable_Reverse::' in line:
                break

        # Read the cry names in the gCryTable_Reverse section
        for line in f:
            match = re.match(r'\s*cry_reverse Cry_(\w+)', line)
            if match:
                cries_reverse.append(match.group(1))
            else:
                break

    return cries_reverse

def get_species_objects(species_file, cries_file):
    species_names = get_species_names_and_constants(species_file)
    cries = get_cries(cries_file)
    cries_reverse = get_reverse_cries(cries_file)

    species_list = []
    for (species, name), cry, cry_reverse in zip(species_names, cries, cries_reverse):
        species_list.append(Species(species, name, cry, cry_reverse))

    return species_list

def camel_to_snake(name):
    name = re.sub('[^a-zA-Z0-9]', '_', name)
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

def format_cry_name(name):
    return re.sub('[^a-zA-Z0-9]', '_', name)

def update_cry_files(species_objects, cries_directory):
    for species in species_objects[0:401]:
        cry_file = path.join(cries_directory, f'{camel_to_snake(species.cry)}.aif')
        new_cry_file = path.join(cries_directory, f'{camel_to_snake(species.name)}.aif')
        if cry_file != new_cry_file:
            if not path.isfile(cry_file):
                print(f'Error: Cry file not found {species.cry.lower()}.aif, using bulbasaur cry instead')
                cry_file = path.join(cries_directory, 'bulbasaur.aif')

            shutil.copyfile(cry_file, new_cry_file)
            species.cry = format_cry_name(species.name)
            if species.cry != species.name:
                print(f'Name adjusted: {species.name} -> {species.cry}')
            species.cry_reverse = species.cry
            species.modified = True
                

def update_cry_tables(species_objects, cry_tables_file):
    with open(cry_tables_file, 'w') as f:
        f.write('\t.align 2\ngCryTable::\n')
        for species in species_objects:
            f.write(f'\tcry Cry_{species.cry}\n')
        
        f.write('\n\t.align 2\ngCryTable_Reverse::\n')
        for species in species_objects:
            f.write(f'\tcry_reverse Cry_{species.cry_reverse}\n')

def update_sound_data_file(species_objects, sound_data_file):
    # First, read in the existing file
    with open(sound_data_file, 'r') as f:
        lines = f.readlines()

    # Find the position of the last line that starts with "\t.align 2\nCry_"
    last_cry_index = max(i for i, line in enumerate(lines) if line.startswith('Cry_'))

    # Generate the new entries and insert them at the correct position
    new_entries = []
    for species in species_objects:
        if species.modified:
            new_entries.append('\t.align 2\n')
            new_entries.append(f'Cry_{species.cry}::\n')
            new_entries.append(f'\t.incbin "sound/direct_sound_samples/cries/{camel_to_snake(species.name)}.bin"\n')
    lines[last_cry_index + 3:last_cry_index + 3] = new_entries  # insert new entries after the last cry section

    # Write out the updated file
    with open(sound_data_file, 'w') as f:
        f.writelines(lines)



if __name__ == "__main__":
    base_dir = get_base_dir()
    species_names_file = path.join(base_dir, 'src', 'data', 'text', 'species_names.h')
    cry_tables_file = path.join(base_dir, 'sound', 'cry_tables.inc')
    cry_audio_dir = path.join(base_dir, 'sound', 'direct_sound_samples', 'cries')
    direct_sound_data_file = path.join(base_dir, 'sound', 'direct_sound_data.inc')

    species_objects = get_species_objects(species_names_file, cry_tables_file)
    update_cry_files(species_objects, cry_audio_dir)
    update_cry_tables(species_objects, cry_tables_file)
    update_sound_data_file(species_objects, direct_sound_data_file)
