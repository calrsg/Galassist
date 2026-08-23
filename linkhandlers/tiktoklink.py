from typing import List
from linkhandlers.linkinterface import LinkInterface

class TiktokLink(LinkInterface):
    """Class to handle Tiktok links."""

    @property
    def name(self) -> str:
        return "Tiktok"

    @property
    def link(self) -> str:
        return "kktiktok.com"

    @property
    def ignore(self) -> List[str]:
        return  ["tiktokez.com", "tnktok.com", "kktiktok.com"]

    @property
    def replace(self) -> List[str]:
        """Return links to replace."""
        return ["tiktok.com"]
    
    @property
    def pattern(self) -> str:
        """Return the regex pattern for the Tiktok link.
        Matches vt.tiktok.com short links and the full www.tiktok.com paths the
        desktop site shares, which carry a query string and no trailing slash."""
        return r"(https?:\/\/)((?:vt|www)\.tiktok\.com)(\/[-a-zA-Z0-9()@:%_\+.~#?&=\/]*)"