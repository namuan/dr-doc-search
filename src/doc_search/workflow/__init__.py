from .verify_input_file import VerifyInputFile


def workflow_steps() -> list:
    return [
        VerifyInputFile,
    ]
