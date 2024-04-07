from typing import Optional

from fiona.collection import Collection
from fiona.crs import CRSError

from sherpa.constants import CONSOLE
from sherpa.utils import format_warning, format_error


def get_collection_srid(collection: Collection) -> Optional[int]:
    try:
        srid = collection.crs.to_epsg()
    except CRSError as ex:
        CONSOLE.print(format_error(str(ex)))
        exit(1)

    if srid is None:
        CONSOLE.print(format_warning(f"Unable to convert file CRS {collection.crs.data} to an EPSG code"))
        return 0
    else:
        return srid
