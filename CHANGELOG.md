## 1.6.3 (2023-02-18)

### Fix

- Support ImageMagick on Windows

## 1.6.2 (2023-02-18)

### Fix

- Support Python3.8

## 1.6.1 (2023-02-18)

### Fix

- Downgrade supported Python version to 3.8.1

## 1.6.0 (2023-02-05)

### Feat

- Set temperature when working with OpenAI feat: Store chat in a chat archive which persists between sessions

## 1.5.1 (2023-01-29)

### Fix

- Fix broken indexing, only worked for first 2 text chunks @Klingefjord
- Suppress warnings

## 1.5.0 (2023-01-29)

### Feat

- Allow user to specify a different LLM instead of OpenAI

## 1.4.1 (2023-01-14)

### Fix

- Ignore empty text chunk as it'll cause error later

## 1.4.0 (2023-01-14)

### Feat

- Minor improvements in usability
- Add line-height when displaying answers

## 1.3.0 (2023-01-08)

### Feat

- Add support for huggingface embedding and allow user to select a different embedding provider from OpenAI
- Add an option to pre-process a PDF file

### Fix

- Update Changelog and remove # used for GH issues

## 1.2.0 (2023-01-07)

### Feat

- Remove duplicate processing of finding similarities

### Fix

- Only copy pdf if the source path is different

### Refactor

- Simplify code

## 1.1.0 (2023-01-07)

### Feat

- Provide option to just create a model for provided book
- WebUI using Holoviz Panel framework

### Refactor

- Cleanup
- Combine workflow steps in a single file to make it easy to port to other projects

## 1.0.1 (2023-01-06)

### Fix

- Ignore tests (temp) as they can't run on Github Actions due to binary dependencies

## 1.0.0 (2023-01-06)

### Feat

- Write workflow to generate book summary

## 0.11.0 (2023-01-05)

### Feat

- Add steps to convert pdf file to scanned pages of text

## 0.10.0 (2023-01-04)

### Feat

- Single version using another method

## 0.9.0 (2023-01-04)

### Feat

- Add annotated tag

## 0.8.0 (2023-01-04)

### Feat

- Add poetry_dynamic_versioning to automatic release versioning

## 0.7.0 (2023-01-04)

### Feat

- Verify input pdf file and set number of pages

## 0.6.0 (2023-01-04)

### Feat

- Initial commit with a skeleton project

### Refactor

- Formatting
