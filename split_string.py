#It is logic used for splitting the large pdf text into small chunks.

text = "This is a very long string... maybe over 10000 characters."
start = 0
chunk_size = 23

while start < len(text):
    chunk = text[start:start + chunk_size]
    last_space_index = chunk.rfind(" ")

    if last_space_index == -1:
        last_space_index = chunk_size  # fallback if no space found

    print(text[start:start + last_space_index])

    start = start + last_space_index + 1  # move past the space
