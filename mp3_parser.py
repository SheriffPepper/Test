import struct;


def id3v2_2(data: bytes) -> dict:
    print("Welcome ID3v2.2!");
    return {};


def id3v2_3(data: bytes) -> dict:
    # Container header
    version: str = "ID3v2.3";
    flags: bytes = struct.unpack('>H', data[4:6])[0];
    length: int = int(''.join(map(lambda x: f"{x:07b}", data[6:10])), 2);

    container: dict = {
        "version": version,
        "flags": flags,
        "length": length,
        "tags": []
    };

    # print("----- Header -----")
    # print("[0x00000000 : 0x00000004] Version: ",
    #       version,
    #       f"({data[:4]})");
    # print("[0x00000004 : 0x00000005] Flags:   ",
    #       flags,
    #       f"({data[4:6]})");
    # print("[0x00000005 : 0x0000000a] Length:  ",
    #       length,
    #       f"({data[6:10]})");

    # Tags
    # print("\n----- Tags -----");

    tags: list = container["tags"];

    offset: int = 10;
    while True:
        header = data[offset:offset + 10];
        # print(f"[0x{offset:08x} : 0x{offset + 10:08x}] Header:", header);

        title = header[:4];  # First four bytes
        # Wrong tag
        if not (
                len(title) == 4 and
                all(map(lambda char: ord('A') <= char <= ord('Z') or ord('0') <= char <= ord('9'), title))
        ):
            # print("Invalid!")
            offset = container["length"] + 10;
            break;
        title: str = title.decode();
        length: int = struct.unpack(">I", header[4:8])[0]  # int(''.join(map(lambda x: f"{x:07b}"[-7:], header[4:8])), 2);
        flags: int = struct.unpack('>H', header[8:10])[0];

        # print(f"    [0x{offset:08x} : 0x{offset + 4:08x}] Title: ",
        #       title,
        #       f"({header[:4]})");
        # print(f"    [0x{offset + 4:08x} : 0x{offset + 8:08x}] Length:",
        #       length,
        #       f"({header[4:8]})");
        # print(f"    [0x{offset + 8:08x} : 0x{offset + 10:08x}] Flags: ",
        #       flags,
        #       f"({header[8:10]})");

        data_: bytes = data[offset + 10: offset + length + 10];
        if title in ("TIT1", "TIT2", "TIT3", "TALB", "TPE1", "TPE2", "TPE3", "TPE4"):
            encodings: dict = {0: "Windows-1251", 1: "utf-16", 3: "utf-8"};
            encoding = encodings[data_[0]];
            # print(f"        Data encoding:", data_[0], f"({encoding})");
            # print(f"    [0x{offset + 10:08x} : 0x{offset + length + 10:08x}] Data:",
            #       repr(data_[1:].decode(encoding)),
            #       f"({data_})");
            tags.append({
                "title": title,
                "length": length,
                "flags": flags,
                "data": data_[1:].decode(encoding)
            });
        else:
            # print(f"    [0x{offset + 10:08x} : 0x{offset + length + 10:08x}] Data:", data_);
            tags.append({
                "title": title,
                "length": length,
                "flags": flags,
                "data": data_
            });
        # print(data_);

        offset += length + 10;

    # print(data[offset:offset + 100]);
    # print(tags);
    return container;


def id3v2_4(data: bytes) -> dict:
    container: dict = id3v2_3(data);
    container["version"] = "ID3v2.4";
    return container;


def parser(filename: str) -> dict:
    with open(filename, 'rb') as mp3:
        data: bytes = mp3.read();

    # ID3v2
    if data.startswith(b'ID3'):
        # print("Header:", data[:10]);
        version: int = data[3];

        # ID3v2.2
        if version == 2:
            return id3v2_2(data);
        # ID3v2.3
        if version == 3:
            return id3v2_3(data);
        # ID3v2.4
        if version == 4:
            return id3v2_4(data);
        # Wrong version
        print(f"Wrong version '{version}'");
    # ID3v1 or Wrong format
    else:
        print("Your mp3 file version is outdated or is not the mp3 format!");


if __name__ == '__main__':
    filenames = ();  # Put addresses to your mp3 files here

    for filename in filenames:
        container = parser(filename);
        print("\nFilename:", filename, f"(version: {container['version']})");
        tags = container["tags"];
        print("Tags:", str(list(map(lambda tag: tag["title"], tags)))[1:-1])

        # ----- Tags -----
        # APIC: Attached picture
        # TALB: Album / Movie / Show title
        # TIT2: Title / song name / content description
        # TPE1: Lead performer(-s) / Soloist(-s)
        # TSSE: Software / Hardware and settings used for encoding
        # TYER: Year (ID3v2.3 only)
        # TXXX: User defined text information frame

        # Song title
        title = list(filter(lambda tag: tag["title"] == "TIT2", tags));
        if not title:
            title = "<Unknown song>";
        else:
            title = list(map(lambda x: x["data"], title));

        artist = list(filter(lambda tag: tag["title"] == "TPE1", tags));
        if not artist:
            artist = "<Unknown author>";
        else:
            artist = list(map(lambda x: x["data"], artist));

        album = list(filter(lambda tag: tag["title"] == "TALB", tags));
        if not album:
            album = "<Unknown album>";
        else:
            album = list(map(lambda x: x["data"], album));

        txxx = list(filter(lambda tag: tag["title"] == "TXXX", tags));
        if not txxx:
            txxx = [''];
        else:
            txxx = list(map(lambda x: x["data"], txxx));

        print("Song title:", repr(title)[1:-1]);
        print("Song author:", repr(artist)[1:-1]);
        print("Song album:", repr(album)[1:-1]);

        print("Text information:", repr(txxx)[1:-1]);

        images = list(filter(lambda tag: tag["title"] == "APIC", tags));
        if not images:
            print("'APIC' tags does not found");
        else:
            print(f"Founded {len(images)} image{'s' if len(images) > 1 else ''}")

            for index, image in enumerate(images):
                data: bytes = image["data"];
                tmp = data.split(b'\x00');

                # continue;
                with open(f"{', '.join(title)}.{index}.jpeg", 'wb') as img:
                    img.write(data.split(b'\x00', 4)[-1]);
