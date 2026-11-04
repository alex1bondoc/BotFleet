from MapGenerator import MapGenerator

if __name__ == "__main__":
    gen = MapGenerator(size=10)
    map = gen.generate_map(seed=42)
    for line in map:
        print(line)