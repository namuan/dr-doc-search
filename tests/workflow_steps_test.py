from doc_search.workflow import (
    ConvertImagesToText,
    ConvertPDFToImages,
    VerifyInputFile,
    workflow_steps,
)


def test_return_expected_workflow() -> None:
    expected_workflow_steps = workflow_steps()

    assert expected_workflow_steps == [
        VerifyInputFile,
        ConvertPDFToImages,
        ConvertImagesToText,
        # LoadExistingIndex,
        # CreateIndexIfNotExists,
        # FindInterestingSections,
        # AskQuestion
    ]
