from boib.models import BulletinType, SectionType


class BulletinTypeFactory:

    @staticmethod
    def from_anchor_class(anchor_classes: list[str]) -> BulletinType:
        if 'ordinario' in anchor_classes:
            return BulletinType.ORDINARY
        elif 'extraordinario' in anchor_classes:
            return BulletinType.EXTRAORDINARY
        else:
            raise ValueError('Unknown bulletin type')


class SectionTypeFactory:

    @staticmethod
    def from_section_text(section_text: str) -> SectionType:
        return {
            'Disposicions generals': SectionType.GENERAL,
            'Autoritats i personal': SectionType.PERSONNEL,
            'Altres disposicions i actes administratius': SectionType.OTHERS,
            'Anuncis': SectionType.ANNOUNCEMENTS,
        }.get(section_text, SectionType.LEGACY)