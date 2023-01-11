import sys;


def getHexDump(data: bytes,
               offset: int = 0,
               width: int = 16,
               header: bool = True,
               decoded: bool = True) -> str:
    """
    Returns the formatted hext string of data

    [data: bytes]      binary data;
    [offset: int]      data output offset;
    [width: int]       hexdump character width;
    [header: bool]     should the hexdump header displayed;
    [decoded: bool]    should the text representation of binary data displayed;
    """
    answer: str = '';
    buffer: bytes = b'';
    overlap: int = 0;

    # Add the header
    if header:
        answer += "\n Offset " + \
                  '   ' + \
                  ' '.join(map(lambda number: f"{number:02x}" + ' ' * (number + 1 and not (number + 1) % 8), range(width))) + \
                  ('   ' + "Decoded text".rjust((width + 14) // 2, ' ')) * decoded + \
                  '\n';

    for address in range(offset, len(data), width):
        heap: bytes = data[address:address + width];

        if heap == buffer and len(buffer) == width:
            overlap += 1;
        else:
            # Add overlapping
            answer += '\n' * bool(overlap) + " *" * overlap;
            answer += f"\n{address:08x}".lower() + \
                      '   ' + \
                      ' '.join(map(lambda pair: f"{pair[1]:02x}" + ' ' * (pair[0] + 1 and not (pair[0] + 1) % 8),
                                   enumerate(heap))).ljust(width * 3 + 1, ' ') + \
                      ('   │' + ''.join(
                          map(
                              lambda char: chr(char) if chr(char).isprintable() else '.',
                              heap
                          )
                      ).ljust(width, ' ') + '│') * decoded;
            overlap = 0;
        buffer = heap;

    return answer;


if __name__ == '__main__':
    try:
        arguments: list[str] = sys.argv[1:];
        filenames: list[str] = [];

        # We have file(-s)
        if arguments:
            filenames.extend(arguments);
        # We must ask the filename
        else:
            filenames.append(input("Enter the filename: "));

        # For each file print the hex format
        for filename in filenames:
            try:
                # Open file
                with open(filename, 'rb') as file:
                    data: bytes = file.read();

                # 4 Kib jumps
                for index in range(0, len(data), 1024):
                        hexdump: str = getHexDump(data[index:index + 1024], header=not index);  # Getting the hexdump
                        print(hexdump);
                        input();  # Pause the output
            except FileNotFoundError:
                print(f"No such file or directory '{filename}'");
    except KeyboardInterrupt:
        exit();
