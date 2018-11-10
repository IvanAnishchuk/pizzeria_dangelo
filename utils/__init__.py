"""
Theoretically this should be an installable library.

It's very likely I will use this as an installable library at some point,
I just didn't have time recently to develop it and I couldn't copypaste
anybody else's code so I decided to quickly hack something new.
"""
import os
import random
import time
import threading
import uuid

COUNTER = 0  # Global thread-safe counter


def seq_uuid(
        timestamp: int = 0,  # 32-bit current timestamp, defaults to time.time()
        pid: int = 0,  # 0..65536 (see docs) defaults to current process ID
        counter: int = 0,  # 0..4096 sequential counter, defaults to global threadsafe counter
        node: int = 0,  # 0..4095 unique node id
        rand: int = 0,  # 0..65535 random number, defaults to randbits
        namespace: int = 0,  # 0..255 unique model ID
        extra: int = 0,  # 0..65535 arbitrary number
        cursor: int = 0,  # 0..65535 reserved for pagination cursors
) -> uuid.UUID:
    """
    Returns a standard uuid5 object but uses custom data instead of hashing.
    FIXME: hell with standard bits, I need more data
    FIXME: or keep them and move the cursor stuff out, that way I can expand everything

    Main feature is that this custom uuids will be sortable by creation
    time and thus effective to use as database ids. Another bonus is that first
    bits are normal unix timestamp so it can be used for filtering by timestamp
    without involving any additional fields.

    Data structure:
        - 4 bytes unix epoch timestamp (we can add some epoch bits after 2106)
        - 2 bytes PID (lower 32 bits only [0])
        - 0.5 bytes version bits
        - 1.5 bytes seq counter (defaults to a global threadsafe var but we
          could use some other method like redis to make it more global)
        - 0.5 bytes variant bits [1]
        - 1.5 bytes node it (some spare bits can be used for future needs)
        - 2 bytes random data in case all other collision protection fails
        - 1 byte "namespace" (arbitrary number or letter unique for models)
        - 1 byte reserved for any extra collision protection needed [2]
        - 2 lower bytes reserved for cursors (a signed offset) [3]

    The result should be unique enough even without any input but for guaranteed
    uniqueness at least node id has to be set correctly (setting per-model
    namespace is also recommended and extra could be model's sequential id).

    Note that this is a quick and dirty version of the generator, many things
    can and should be optimized before any production use. Counter is relatively
    short, only allowing 4096 unique ids per second per process. This is not a
    copy-paste, it's based on my original research and never published yet.
    But feel free to reuse, I'm CC0-ing it :)

    [0] Currently pid_max = 32768 on most 64-bit systems, if higher value is
        used and PID is longer, use the "extra" byte for it
    [1] There's another unused bit there if there are more than 4096 nodes.
    [2] I.e. if somehow somebody tries to generate one at the same second,
        with the same node id, PID, random bits, and counter. We could use lower
        nanoseconds bits or some additional shared counter, epoch id or century
        if 32-bit timestamp is not enough, or upper PID bits, or pretty much
        anything there.
    [3] It's actually the nicest form of position-limit cursors I could think of
        so far, maybe it could be improved. But this way is cool, you can take
        any (signed!) number in -32768..+32767 range and request a page of that
        size going forward or backward by bitwise &-ing to the end of an id. Or
        encoding to hex and replacing the last hex chars if it's easier.
        And if someone thinks that the hex form is too long we can switch to
        22-byte base64 encoding or basically any way suitable for a pair of
        64-bit integers. We can see it as no worse than passing sequential id
        and limit/direction as two 64-bit integers (which wouldn't be too
        insane, only slightly ineffective) but with a nicer id format it makes
        much more sense.
    """
    if not timestamp:
        timestamp = int(time.time())
        # Here we could also fetch nanoseconds if needed
    if timestamp >= 2 ** 32:
        timestamp %= 2 ** 32  # Revisit before 2100
    if not pid:
        pid = os.getpid()
    # I'm pretty sure it's not the most optimized way to do bitwise operations
    # but I'm in a hurry and this works. I can run profiling later when the more
    # pressing things are finished. At very least it's mostly readable.
    if pid >= 2 ** 32:
        pid %= 2 ** 32

    if not counter:
        with threading.Lock():
            # Thread-safe increment
            global COUNTER
            COUNTER += 1
            if COUNTER >= 2 ** 12:
                COUNTER %= 2 ** 12
            counter = COUNTER

    if not rand:
        rand = random.getrandbits(16)
    elif rand >= 2 ** 16:
        rand %= 2 ** 16

    if node > 2 ** 12:
        node %= 2 ** 12
    if namespace > 2 ** 8:
        namespace %= 2 ** 8
    if extra >= 2 ** 8:
        extra %= 2 ** 8
    if cursor >= 2 ** 8:
        cursor %= 2 ** 8

    return uuid.UUID(
        bytes=b''.join([
            timestamp.to_bytes(4, 'big'),
            pid.to_bytes(2, 'big'),
            counter.to_bytes(2, 'big'),
            node.to_bytes(2, 'big'),
            rand.to_bytes(2, 'big'),
            bytes([namespace, extra]),
            cursor.to_bytes(2, 'big', signed=True),
        ]),
        version=5,
    )
