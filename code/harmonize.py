"""harmonize.py - shared rules for units, censoring, and Midcontinent Rift membership.

Plain-language note: this file holds the conversion rules (re-used from the QA checker
package, for example silicon in percent becomes SiO2 in weight percent) and the word lists
used to decide whether a sample belongs to the Midcontinent Rift. Other scripts import it.
You do not need to open it unless you want to check a rule.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcrqa.units import *  # noqa: F401,F403,E402
from mcrqa.units import FEO_TO_FE2O3, harmonize, parse_text_value, parse_usgs_qualified  # noqa: F401,E402


# ---------------------------------------------------------------- rift membership
RIFT_TEXT = re.compile(
    r"keweena|midcontinent rift|mid-continent rift|duluth complex|duluth gabbro|portage lake|nonesuch|"
    r"copper harbor|chengwatana|porcupine volc|porcupine mountain|mineral lake intrusi|mellen|siemens creek|"
    r"kallander|powder mill|north shore volc|beaver bay|beaver river|oronto|freda|bergland|tamarack|"
    r"eagle (?:deposit|intrusion|east|mine)|partridge river|south kawishiwi|bald eagle|wild lake intrusion|"
    r"greenwood lake intrusion|tuscarora|logan (?:sill|intrusion)|silver cliff|endion|schroeder|lutsen|"
    r"two harbors|grand marais|brule river|ely'?s peak|lakewood bas|lakeside lava|leif erick|sucker river|"
    r"baptism river|larsmont|white pine|copperwood|potato river|clam falls|north branch|minong|isle royale|"
    r"greenstone flow|tobacco river|puckwunge|nopeming|fond du lac f|solor church|jacobsville|bayfield gr|"
    r"chequamegon|orienta|devils? island|hinckley|interflow sed|midcontinent rift intrusive|beaver lake intr|"
    r"bad river gabbro|wolf ridge|coldwell|mamainse|michipicoten|nipigon|osler|gargantua|"
    r"alona bay|crystal lake gabbro|pigeon river|cloud river|mount mollie|riverdale sill|black bay|"
    r"prairie lake|chipman lake",
    re.I)
POST_RIFT_SED = re.compile(r"jacobsville|bayfield gr|chequamegon|orienta|devils? island|hinckley", re.I)
RIFT_SED = re.compile(r"nonesuch|copper harbor conglom|freda|oronto|puckwunge|nopeming|fond du lac f|"
                      r"solor church|interflow sed|white pine|copperwood", re.I)
NONRIFT_TEXT = re.compile(
    r"michigamme|ironwood|negaunee|biwabik|virginia f|thomson f|animikie|rove f|knife lake|giants?'?s? range|"
    r"vermilion|ely greenstone|soudan|newton lake|bell creek|quinnesec|hemlock f|wolf river|wausau|stettin|"
    r"marquette range|baraga gr|goodrich|palms f|siamo|kona|mesnard|wewe|ajibik|engadine|franconia|munising|"
    r"maquoketa|galena|platteville|decorah|prairie du chien|mt\.? simon|mount simon|copps f|pembine|"
    r"carney lake|mille lacs|cuyuna|archean|neoarchean|mentor complex|penokean|athens|mcgrath|"
    r"denham f|trout lake f|emperor|bad river dolomite|tyler f|felch|vulcan|riverton|amasa|dunn creek|"
    r"badwater|paint river|hiawatha|lake owen|barron quartzite|baraboo|waterloo quartzite|sioux quartzite|"
    r"st\.? peter|jordan s|eau claire f|wonewoc|tunnel city|oneota|shakopee|glenwood|cincinnati|"
    r"silurian|ordovician|cambrian|devonian|pleistocene|quaternary|glacial|till\b",
    re.I)
NONRIFT_AGES = re.compile(r"archean|early precambrian|paleoproterozoic|middle precambrian|cambrian|ordovician|"
                          r"silurian|devonian|mississippian|pennsylvanian|permian|triassic|jurassic|"
                          r"cretaceous|tertiary|paleogene|neogene|quaternary|pleistocene|holocene", re.I)


def rift_decision(primary_text, secondary_text, geologic_age, map_member):
    """Decide Midcontinent Rift membership.

    primary_text: unit/stratigraphy/rock-unit fields; secondary_text: deposit, project, locality;
    map_member: SGMC membership class at the sample point ('' if none or excluded unit).
    Returns (in_mcr, how, reason).
    """
    p, s, age = (primary_text or ""), (secondary_text or ""), (geologic_age or "")
    if RIFT_TEXT.search(p) and not NONRIFT_TEXT.search(p):
        return True, "text+map" if map_member else "text", "rift unit named in source"
    if NONRIFT_TEXT.search(p):
        return False, "", "non-rift unit named in source: " + NONRIFT_TEXT.search(p).group(0)
    if NONRIFT_AGES.search(age):
        return False, "", "non-rift geologic age in source: " + age
    if map_member:
        if RIFT_TEXT.search(s):
            return True, "map+context", "on rift map unit; rift named in locality/project"
        return True, "map", "on rift map unit (SGMC)"
    if RIFT_TEXT.search(s) and not NONRIFT_TEXT.search(s):
        return True, "context", "rift named in locality/project only"
    return False, "", "not on a rift map unit and no rift name in source"


def member_class(text, map_class, rock_class=""):
    """Rift sub-class: rift_igneous, rift_sedimentary, post_rift_sedimentary.

    Order: unit named in the source wins; then the rock type (an igneous rock on a sandstone map
    polygon is a dike or a mapping-scale effect, so it is rift_igneous); then the map unit class.
    """
    t = text or ""
    rc = rock_class or ""
    if POST_RIFT_SED.search(t):
        return "post_rift_sedimentary"
    if RIFT_SED.search(t):
        return "rift_sedimentary"
    if RIFT_TEXT.search(t):
        return "rift_sedimentary" if rc == "sedimentary" else "rift_igneous"
    if rc.startswith("igneous"):
        return "rift_igneous"
    if rc == "sedimentary" and map_class == "rift_igneous":
        return "rift_sedimentary"
    return map_class or "rift_igneous"
