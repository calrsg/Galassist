from typing import List
from linkhandlers.linkinterface import LinkInterface

class InstagramLink(LinkInterface):
    """Class to handle Instagram links."""

    @property
    def name(self) -> str:
        return "Instagram"

    @property
    def link(self) -> str:
        return "oginstagram.com"
    
    @property
    def status(self) -> str:
        return None

    @property
    def ignore(self) -> List[str]:
        return  ["ddinstagram.com", "zzinstagram.com", "d.vxinstagram.com", "oginstagram.com"]

    @property
    def replace(self) -> List[str]:
        """Return links to replace."""
        return ["instagram.com"]
    
    @property
    def pattern(self) -> str:
        """Return the regex pattern for the Instagram link.
        Matches Instagram links with reel and post components."""
        return r"(https?:\/\/)((?:www\.)?instagram\.com)(\/reel\/|\/p\/)([-a-zA-Z0-9()@:%_\+.~#?&=\/]*)"