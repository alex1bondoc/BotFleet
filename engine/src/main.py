from MapGenerator import MapGenerator

if __name__ == "__main__":
    gen = MapGenerator(seed=42, size=10)
    map = gen.generate_map(gen.seed)
    for line in map:
        print(line)