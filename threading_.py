import os
import typing as t

import concurrent.futures

import threading

import requests

import utils


thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

def download_and_save_pokemon(arg):
    """Download and save a single pokemon."""
    pokemon = arg[0]
    output_dir = arg[1]
    session = get_session()
    content = utils.maybe_download_sprite(session, pokemon["Sprite"])
    if content is not None:
        target_dir = os.path.join(output_dir, pokemon["Type1"])
        utils.maybe_create_dir(target_dir)
        filepath = os.path.join(target_dir, pokemon["Pokemon"] + ".png")
        utils.write_binary(filepath, content)


def dowload_and_save_all_pokemons(pokemons, output_dir):
    """Download and save all pokemons using a sequentially."""
    args = [(p, output_dir) for p in pokemons]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(download_and_save_pokemon, args)

@utils.timeit
def main(output_dir: str, inputs: t.List[str]):
    """Download for all intpus and place them in output_dir."""
    utils.maybe_create_dir(output_dir)
    dowload_and_save_all_pokemons(utils.read_pokemons(inputs), output_dir)
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", help="directory to store the data")
    parser.add_argument("inputs", nargs="+", help="list of files with metadata")
    args = parser.parse_args()
    utils.maybe_remove_dir(args.output_dir)
    main(args.output_dir, args.inputs)