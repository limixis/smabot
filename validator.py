from random import choice
from string import ascii_lowercase, ascii_uppercase
import argparse


class Validator(object):
    def __init__(self, keys_path):
        self.keys_path = keys_path
        self.keys = []
        with open(self.keys_path) as f:
            for key in f.readlines():
                self.keys.append(key.strip())

    def validate_keys(self, input_key):
        if input_key in self.keys:
            self.keys.remove(input_key)
            return True
        else:
            return False

    def reset(self):
        self.__init__(self.keys_path)


class Generator(object):
    def __init__(self, keys_path):
        self.keys_path = keys_path

    def generate_keys(self, key_len, count):
        key_set = set()
        while len(key_set) < count:
            key = ''.join(choice(ascii_lowercase + ascii_uppercase) for j in range(key_len))
            key_set.add(key)

        with open(self.keys_path, 'w') as f:
            for key in key_set:
                print >> f, key


def parse_args():
    parser = argparse.ArgumentParser(description="Generate tokens for authentication")
    parser.add_argument("-f", dest="output_file", default="./keys.tsv", help="Path to file with keys")
    parser.add_argument("-l", dest="length", default=5, help="one token's length")
    parser.add_argument("-n", dest="n", default=500, help="number of tokens")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    key_gen = Generator(args.output_file)
    key_gen.generate_keys(args.length, args.n)