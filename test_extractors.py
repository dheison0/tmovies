import pytest

from src import extractors, models


class ExtractorTest(models.classes.Extractor):
    id = "test"
    title = "extractor test"
    pass


def test_add_extractor():
    extractors.pool.add_extractor(ExtractorTest)
    assert extractors.pool.get_extractor("test") == ExtractorTest


def test_get_extractor():
    with pytest.raises(extractors.ExtractorNotFound):
        extractors.pool.get_extractor("thatIsNotAnExtractor")
    extractors.pool.add_extractor(ExtractorTest)
    assert extractors.pool.get_extractor(ExtractorTest.id) == ExtractorTest


def test_get_all_extractors():
    extractor_list = extractors.pool.get_all_extractors()
    assert isinstance(extractor_list, list)
    for e in extractor_list:
        assert issubclass(e, models.classes.Extractor)
