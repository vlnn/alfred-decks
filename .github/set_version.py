import plistlib
import sys
from pathlib import Path

DEFINITION = Path(__file__).resolve().parent.parent / "info.plist"


def with_version(definition, version):
    return {**definition, "version": version}


def main(version):
    definition = plistlib.loads(DEFINITION.read_bytes())
    DEFINITION.write_bytes(plistlib.dumps(with_version(definition, version)))


if __name__ == "__main__":
    main(sys.argv[1])
